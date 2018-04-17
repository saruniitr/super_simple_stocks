#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Super Simple Stock Market
#
# Simple client to submit transactions to Global Beverages Corporation Exchange
#
#


import zmq
import argparse
from argparse import RawTextHelpFormatter
import json
from decimal import Decimal
import logging

def prepare_msg(action, **kwargs):
	msg = dict()
	args = dict()
	for key in kwargs:
		args[key] = kwargs[key]
	msg["action"] = action
	msg["args"] = args
	return msg

def main(cmd_args, port=5555):
	logging.basicConfig(level=logging.INFO,\
						format='%(asctime)s.%(msecs)03d %(name)-4s [%(levelname)-4s] %(message)s',\
						datefmt='%d-%m-%Y %H:%M:%S')
	logger = logging.getLogger('CLIENT')

	action = cmd_args[0]
	params = cmd_args[1:]

	if action == 'GBCE_DIV_YIELD':
		msg = prepare_msg(action, symbol=params[0], price=params[1])
	elif action == 'GBCE_PE_RATIO':
		msg = prepare_msg(action, symbol=params[0], price=params[1])
	elif action == 'GBCE_RECORD_TRADE':
		msg = prepare_msg(action, symbol=params[0], trade_type=params[1],\
			quantity=params[2], price=params[3])
	elif action == 'GBCE_CALC_STOCK_PRICE':
		msg = prepare_msg(action, symbol=params[0])
	elif action == 'GBCE_CALC_GBCE_INDEX':
		msg = prepare_msg(action)
	elif action == 'GBCE_CLEAR_TRADES':
		msg = prepare_msg(action)
	elif action == 'GBCE_EXIT':
		msg = prepare_msg(action)
	else:
		logger.info("Invalid action [{0}]".format(action))

	context = zmq.Context()

	#  Socket to talk to server
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://localhost:{0}".format(port))

	socket.send_json(msg)
	if action != 'GBCE_EXIT':
		resp = socket.recv_json()
		if resp["args"]["status"] == "error":
			logger.info('Error executing {0} ({1})'.format(action, resp["args"]["message"]))
		else:
			logger.info("Response for {0}: {1}".format(action, resp["args"]["value"]))
	socket.close()


if __name__ == '__main__':
	help_text = 'Specifies the action followed by arguments\n'
	help_text += 'Possible actions and usage shown below:\n'
	help_text += '1. GBCE_DIV_YIELD <symbol> <price>\n'
	help_text += '2. GBCE_PE_RATIO <symbol> <price>\n'
	help_text += '3. GBCE_RECORD_TRADE <BUY/SELL> <symbol> <quantity> <price>\n'
	help_text += '4. GBCE_CALC_STOCK_PRICE <symbol>\n'
	help_text += '5. GBCE_CALC_GBCE_INDEX\n'
	help_text += '6. GBCE_EXIT\n'
	parser = argparse.ArgumentParser(description='This is a simple client for Global Beverages Corporation Exchange',\
									formatter_class=RawTextHelpFormatter)

	parser.add_argument('--action', action="store", dest="action", nargs="*",\
						required=True, help=help_text)
	args = parser.parse_args()

	main(args.action)