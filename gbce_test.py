#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Super Simple Stock Market
#
# Unit Test module for Global Beverages Corporation Exchange
#
#

import zmq
import json
from decimal import Decimal
from random import randint, uniform
import unittest


def prepare_msg(action, **kwargs):
	msg = dict()
	args = dict()
	for key in kwargs:
		args[key] = kwargs[key]
	msg["action"] = action
	msg["args"] = args
	return msg
 
class TestGBCE(unittest.TestCase):
 
	def setUp(self):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.socket.connect("tcp://localhost:5555")

	def send_msg(self, msg):
		self.socket.send_json(msg)
		resp = self.socket.recv_json()
		return resp

	def test_invalid_symbol(self):
		resp = self.send_msg(prepare_msg('GBCE_DIV_YIELD', symbol='TEST', price=json.dumps(100.00)))
		self.assertEqual(resp["args"]["status"], "error")
		self.assertEqual(resp["args"]["value"], None)

	def test_calc_dividend_yield(self):
		resp = self.send_msg(prepare_msg('GBCE_DIV_YIELD', symbol='POP', price=json.dumps(100.00)))
		self.assertEqual(resp["args"]["value"], str(0.08))

		resp = self.send_msg(prepare_msg('GBCE_DIV_YIELD', symbol='POP', price=None))
		self.assertEqual(resp["args"]["status"], "success")

		resp = self.send_msg(prepare_msg('GBCE_DIV_YIELD', symbol='POP'))
		self.assertEqual(resp["args"]["status"], "error")
		self.assertEqual(resp["args"]["value"], None)

	def test_calc_pe_ratio(self):
		msg = prepare_msg('GBCE_PE_RATIO', symbol='POP', price=json.dumps(1000.00))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["value"], str(125.0))

		msg = prepare_msg('GBCE_PE_RATIO', symbol='POP', price=None)
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["value"], None)

		msg = prepare_msg('GBCE_PE_RATIO', symbol='POP')
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "error")
		self.assertEqual(resp["args"]["value"], None)

	def test_record_trade(self):
		# clear existing trades for a consistent state
		self.clear_trades()

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='TEA', trade_type='BUY',\
			quantity=str(100), price=json.dumps(20.54))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "success")

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='POP', trade_type='BUY',\
			quantity=str(300), price=json.dumps(150.25))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "success")

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='POP', trade_type='SELL',\
			quantity=str(100), price=json.dumps(180.5))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "success")

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='TEA', trade_type='SELL',\
			quantity=str(100), price=json.dumps(25.70))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "success")

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='TEA', trade_type='HOLD',\
			quantity=str(100), price=json.dumps(25.70))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "error")

		msg = prepare_msg('GBCE_RECORD_TRADE', symbol='TEA', trade_type='SELL',\
			quantity=str(100))
		resp = self.send_msg(msg)
		self.assertEqual(resp["args"]["status"], "error")

	def clear_trades(self):
		resp = self.send_msg(prepare_msg('GBCE_CLEAR_TRADES'))
		self.assertEqual(resp["args"]["status"], "success")

	def generate_trades(self, num_trades):
		# generate few trades within required duration
		symbols = [ 'TEA', 'POP', 'ALE', 'GIN', 'JOE' ]
		trade_types = [ 'BUY', 'SELL' ]
		sym = ''
		for i in range(num_trades):
			sym = symbols[randint(0, len(symbols) - 1)]
			trade = trade_types[randint(0, len(trade_types) - 1)]
			quantity = randint(100, 500)
			price = round(uniform(10.0, 100.00), 4)
			msg = prepare_msg('GBCE_RECORD_TRADE', symbol=sym, trade_type=trade,\
				quantity=str(quantity), price=json.dumps(price))
			resp = self.send_msg(msg)
			self.assertEqual(resp["args"]["status"], "success")

		return sym

	def test_calc_stock_price(self):
		# clear existing trades for a consistent state
		self.clear_trades()

		resp = self.send_msg(prepare_msg('GBCE_CALC_STOCK_PRICE', symbol='TEA'))
		self.assertEqual(resp["args"]["status"], "success")

		sym = self.generate_trades(5)
		resp = self.send_msg(prepare_msg('GBCE_CALC_STOCK_PRICE', symbol=sym))
		self.assertEqual(resp["args"]["status"], "success")

	def test_calc_all_share_index(self):
		self.clear_trades()
		resp = self.send_msg(prepare_msg('GBCE_CALC_GBCE_INDEX'))
		self.assertEqual(resp["args"]["value"], str("0.0"))

		self.generate_trades(10)
		resp = self.send_msg(prepare_msg('GBCE_CALC_GBCE_INDEX'))
		self.assertNotEqual(resp["args"]["value"], str("None"))

	def tearDown(self):
		self.socket.close()

 
if __name__ == '__main__':
    unittest.main()
