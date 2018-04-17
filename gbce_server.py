#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
"""
Super Simple Stock Market

Global Beverages Corporation Exchange Server
"""

from gbce_models import gbce

def main():
	"""
	Simple server for Global Beverages Corporation Exchange (GBCE)
	Initializes with sample data and listens for transactions from Client
	"""
	server = gbce()
	server.load_data('sample_data.json')
	server.start()

if __name__ == '__main__':
	main()
