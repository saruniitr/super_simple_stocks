# -*- coding: utf-8 -*-
#
"""
# Super Simple Stock Market
"""

import sys
import zmq
import json
import time
import datetime
from functools import reduce
from decimal import Decimal
import logging
import logging.handlers

def load_json(filename):
	"""Helper function to read json file"""
	with open(filename) as j:
		return json.load(j)

class stock:
	"""
	Class that represents a Stock
	"""
	def __init__(self, symbol, div_type, last_div, fixed_div, par_value):
		self.symbol = symbol
		self.div_type = div_type
		self.last_div = last_div
		if fixed_div != "None":
			self.fixed_div = fixed_div / 100
		self.par_value = par_value
		self.trades = []
		logging.basicConfig(level=logging.INFO,\
							format='%(asctime)s.%(msecs)03d %(name)-4s [%(levelname)-4s] %(message)s',\
							datefmt='%d-%m-%Y %H:%M:%S')
		self.logger = logging.getLogger('STOCK')

	def calc_dividend_yield(self, price):
		"""
		Calculates Dividend yield for this Stock using given price
		Args:
			price(float): Price of the stock. If None then stock price is calculated

		Returns:
			dividend_yield (float)
		"""
		last_div = self.last_div
		if price is None:
			price = self.calc_vol_weighted_stock_price()
			# if there are no trades then stock price cannot be calculated
			if price is None:
				return None

		if self.div_type == "Common":
			return last_div / price
		elif self.div_type == "Preferred":
			return (self.fixed_div * self.par_value) / price

	def calc_pe_ratio(self, price):
		"""
		Calculates Price/Earnings ratio for this Stock using given price
		Args:
			price(float): Price of the stock. If None then PE cannot be calculated

		Returns:
			PE ratio (float)
		"""
		pe_ratio = None
		if self.last_div and price is not None:
			pe_ratio = price / self.last_div

		return pe_ratio

	def record_trade(self, trade_type, quantity, price):
		"""
		Records a trade (BUY/SELL) with the provided quantity and price
		Args:
			trade_type (string): 'BUY' or 'SELL'
			quantity (int): Quantity to buy/sell
			price (float): Price of the stock at which to buy/sell
		"""
		trade = {
			"timestamp": datetime.datetime.now(),
			"symbol": self.symbol,
			"trade_type": trade_type,
			"quantity": quantity,
			"price": price
		}
		self.trades.append(trade)
		return 'success'

	def calc_vol_weighted_stock_price(self, duration=5):
		"""
		Calculates Stock prices using Volume weighted mechanism of all trades occurred in given duration
		vol_weighted_price = sum_all_stocks(traded_price * quantity) / sum_all_stocks(quantity
		)
		Args:
			duration (int): List of all trades of this stock happened in this duration (default 5 min)

		Returns:
			stock_price (float): Calculated Stock price
		"""
		now = datetime.datetime.now()

		def within_duration(stock):
			return (now - stock['timestamp']).total_seconds() < duration * 60

		recent_trades = list(filter(within_duration, self.trades))
		if len(list(recent_trades)) == 0:
			self.logger.info('No recent trades for {0} within {1} minutes, index cannot be calculated'.\
				format(self.symbol, duration))
			return None
		prices = [ t['price'] for t in recent_trades ]
		quantity = [ t['quantity'] for t in recent_trades ]
		nr = sum(map(lambda x, y: x * y, prices, quantity))
		dr = reduce(lambda x, y: x + y, quantity)
		return round(nr / dr, 4)

	def clear_trades(self):
		"""
		Clears all trades of this particular stock
		Used mainly during testing
		"""
		self.trades.clear()


class gbce:
	"""
	Class that represents Global Beverages Corporation Exchange (GBCE)
	"""

	context = None
	socket = None
	port = None
	stocks_list = dict()
	allowed_trades = [ 'BUY', 'SELL' ]

	def __init__(self, port=5555, debug=False):
		# Initialize message queue context and bind to retrieve transactions from Clients
		gbce.context = zmq.Context()
		gbce.port = port
		gbce.socket = gbce.context.socket(zmq.REP)
		gbce.socket.bind("tcp://*:{0}".format(port))

		# No of arguments required for a particular action
		self.arg_count = {
			'GBCE_DIV_YIELD': 2,
			'GBCE_PE_RATIO': 2,
			'GBCE_RECORD_TRADE': 4,
			'GBCE_CALC_STOCK_PRICE': 1,
			'GBCE_CALC_GBCE_INDEX': 0,
			'GBCE_CLEAR_TRADES': 0,
			'GBCE_EXIT': 0
		}

		logging.basicConfig(level=logging.INFO,\
							format='%(asctime)s.%(msecs)03d %(name)-4s [%(levelname)-4s] %(message)s',\
							datefmt='%d-%m-%Y %H:%M:%S')
		self.logger = logging.getLogger('GBCE')

	def load_data(self, sample_data_file):
		d = load_json(sample_data_file);
		sample_data = d["sample data"]
		for item in sample_data:
			s = stock(item["Symbol"], item["Div Type"],\
						item["Last Dividend"], item["Fixed Dividend"],\
						item["Par Value"])
			gbce.stocks_list[item["Symbol"]] = s

	def _send_response(self, action, status, message, value=None):
		resp = dict()
		args = dict()
		resp["action"] = action
		args["status"] = status
		args["message"] = message
		if isinstance(value, float):
			args["value"] = json.dumps(value)
		else:
			args["value"] = value
		resp["args"] = args
		gbce.socket.send_json(resp)

	def send_response(self, action, message, value):
		self._send_response(action, "success", message, value)

	def send_err_response(self, action, message):
		self._send_response(action, "error", message)

	def geometric_mean(self, prices, precision=4):
		"""
		Calculates Geometric mean of the Prices
		geometric mean = nth root (p1 * p2 * ..... * pn)
		Args:
			prices (list): List of Prices
			precision(int): Floating point precision, default 4 places

		Returns:
			gm(float): Geometric mean of given list of prices

		"""
		gm = 0.0
		if len(prices):
			gm = float(reduce(lambda x, y: x * y, prices)) ** (1 / float(len(prices))) 

		return round(gm, precision)

	def calc_gbce_index(self):
		"""
		Calculates All shares Index
		index = geometric_mean(all stocks prices)
		Args:
			None

		Returns:
			all share index: Calculated index of all shares
		"""
		prices = []
		for sym, stock in gbce.stocks_list.items():
			p = stock.calc_vol_weighted_stock_price()
			'''if there are no trades available within given duration
			then None is returned'''
			if p is None:
				continue

			prices.append(p)

		return self.geometric_mean(prices)

	def handle_transaction(self, msg):
		"""
		Message handler that receives messages from Clients and acts on the requested action

		Args:
			msg: packet that specifies action followed by required arguments

		Returns
			resp: includes action executed, status, value, error message (if any)
		"""
		action = msg["action"]
		args = msg["args"]
		if action not in self.arg_count.keys()\
			 or	len(args) != self.arg_count[action]:
			self.send_err_response(action, "Invalid number of arguments")
			return True

		sym = args.get("symbol", None)
		if sym is not None:
			s = gbce.stocks_list.get(args["symbol"], None)
			if s is None:
				self.send_err_response(action, "Invalid Symbol '{0}'".format(sym))
				return True

		self.logger.info('{0}'.format(msg))

		"""
		Extract arguments according to action and invoke relevant function
		Values are deserialized where applicable and serialized in action response message
		"""
		value = None

		if action == "GBCE_DIV_YIELD":
			price = args.get("price", None)
			if price is not None:
				price = json.loads(price)
			value = s.calc_dividend_yield(price)
		elif action == "GBCE_PE_RATIO":
			price = args.get("price", None)
			if price is not None:
				price = json.loads(price)
			value = s.calc_pe_ratio(price)
		elif action == "GBCE_RECORD_TRADE":
			trade_type = args.get("trade_type", None)
			if trade_type not in gbce.allowed_trades:
				self.send_err_response(action, "Trade type can be either BUY or SELL")
				return True
			quantity = json.loads(args["quantity"])
			price = json.loads(args["price"])
			value = s.record_trade(trade_type, quantity, price)
		elif action == "GBCE_CALC_STOCK_PRICE":
			value = s.calc_vol_weighted_stock_price()
		elif action == "GBCE_CALC_GBCE_INDEX":
			value = self.calc_gbce_index()
		elif action == "GBCE_CLEAR_TRADES":
			for k, s in gbce.stocks_list.items():
				s.clear_trades()

		#  Send reply back to client
		self.send_response(action, "", value=value)

	def start(self):
		self.logger.info('Server listening on Port {0}'.format(gbce.port))
		while True:
			#  Wait for next request from client
			msg = gbce.socket.recv_json()
			if msg["action"] == "GBCE_EXIT":
				self.stop()
				break

			# handle message and respond
			self.handle_transaction(msg)

	def stop(self):
		"""
		Stops listening to Clients requests
		"""

		# close socket and release resources
		gbce.socket.close()
		for k, s in gbce.stocks_list.items():
			s.clear_trades()
		gbce.stocks_list.clear()
		self.logger.info('Server Exit')
