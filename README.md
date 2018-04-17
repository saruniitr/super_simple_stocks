# Super Simple Stock Market
Global Beverages Corporation Exchange is a super simple stock market for trading in drink companies

## Description
- For a given stock, 
    - Calculate the Dividend Yield
    - Calculate the P/E Ratio
    - Record a trade, with timestamp, BUY/SELL, quantity and price
    - Calculate Volume Weighted Stock Price based on trades recorded in past 5 minutes
- Calculate the GBCE All Share Index using the geometric mean of the Volume weighted Stock Price for all stocks

## Requirements
- Python 3.x (tested on 3.5.2)
- pyzmq (tested on 16.0.4)
- unittest
- Tested on Ubuntu 16.04

## Components
1. gbce_server.py - Simple server for GBCE
Server on startup loads sample data and listens for transactions on port 5555. Only actions that correspond to the requirements are handled, other actions are considered as error. For each action, correponding function is invoked and a response is returned with action status, output value and error message (if any).

2. gbce_client.py - Client that submits transactions to GBCE server
Client connects to the port 5555 and submits action along with supplied arguments. Possible actions and usages are shown below,

- GBCE_DIV_YIELD symbol price
- GBCE_PE_RATIO symbol price
- GBCE_RECORD_TRADE BUY/SELL symbol quantity price
- GBCE_CALC_STOCK_PRICE symbol
- GBCE_CALC_GBCE_INDEX
- GBCE_EXIT

3. gbce_test.py - Unit test module
Includes test cases to test all requirements mentioned in the description

## Example Run

Start Server
```
python3 gbce_server.py
```

Start Client with allowed actions
```
python3 gbce_client.py --action ACTION VARGS
```

Server logs
```
16-04-2018 01:19:08.968 GBCE [INFO] Server listening on Port 5555
16-04-2018 01:19:19.878 GBCE [INFO] {'args': {'symbol': 'POP', 'price': '100'}, 'action': 'GBCE_DIV_YIELD'}
16-04-2018 01:19:31.332 GBCE [INFO] {'args': {'symbol': 'POP', 'price': '100'}, 'action': 'GBCE_PE_RATIO'}
16-04-2018 01:19:57.684 GBCE [INFO] {'args': {'trade_type': 'BUY', 'quantity': '100', 'price': '18.5', 'symbol': 'TEA'}, 'action': 'GBCE_RECORD_TRADE'}
16-04-2018 01:20:09.269 GBCE [INFO] {'args': {'trade_type': 'SELL', 'symbol': 'TEA', 'price': '30.5', 'quantity': '50'}, 'action': 'GBCE_RECORD_TRADE'}
16-04-2018 01:20:25.111 GBCE [INFO] {'args': {'trade_type': 'BUY', 'quantity': '400', 'price': '50', 'symbol': 'POP'}, 'action': 'GBCE_RECORD_TRADE'}
16-04-2018 01:20:45.675 GBCE [INFO] {'args': {'trade_type': 'SELL', 'symbol': 'POP', 'price': '60.5', 'quantity': '400'}, 'action': 'GBCE_RECORD_TRADE'}
16-04-2018 01:20:59.372 GBCE [INFO] {'args': {'symbol': 'POP'}, 'action': 'GBCE_CALC_STOCK_PRICE'}
16-04-2018 01:21:11.949 GBCE [INFO] {'args': {}, 'action': 'GBCE_CALC_GBCE_INDEX'}
16-04-2018 01:21:11.949 STOCK [INFO] No recent trades within 5 minutes, index cannot be calculated
16-04-2018 01:21:11.949 STOCK [INFO] No recent trades within 5 minutes, index cannot be calculated
16-04-2018 01:21:11.949 STOCK [INFO] No recent trades within 5 minutes, index cannot be calculated
16-04-2018 01:26:38.697 GBCE [INFO] Server Exit
```

Client requests and logs
```
python3 gbce_client.py --action GBCE_DIV_YIELD POP 100
16-04-2018 01:19:19.878 CLIENT [INFO] Response for GBCE_DIV_YIELD: 0.08

python3 gbce_client.py --action GBCE_PE_RATIO POP 100
16-04-2018 01:19:31.333 CLIENT [INFO] Response for GBCE_PE_RATIO: 12.5

python3 gbce_client.py --action GBCE_RECORD_TRADE TEA BUY 100 18.5
16-04-2018 01:19:57.685 CLIENT [INFO] Response for GBCE_RECORD_TRADE: success

python3 gbce_client.py --action GBCE_RECORD_TRADE TEA SELL 50 30.5
16-04-2018 01:20:09.270 CLIENT [INFO] Response for GBCE_RECORD_TRADE: success

python3 gbce_client.py --action GBCE_RECORD_TRADE POP BUY 400 50
16-04-2018 01:20:25.112 CLIENT [INFO] Response for GBCE_RECORD_TRADE: success

python3 gbce_client.py --action GBCE_RECORD_TRADE POP SELL 400 60.5
16-04-2018 01:20:45.676 CLIENT [INFO] Response for GBCE_RECORD_TRADE: success

python3 gbce_client.py --action GBCE_CALC_STOCK_PRICE POP
16-04-2018 01:20:59.373 CLIENT [INFO] Response for GBCE_CALC_STOCK_PRICE: 55.25

python3 gbce_client.py --action GBCE_CALC_GBCE_INDEX
16-04-2018 01:21:11.950 CLIENT [INFO] Response for GBCE_CALC_GBCE_INDEX: 35.258

python3 gbce_client.py --action GBCE_CALC_GBCE_EXIT
```

Unit test logs,
```
python3 gbce_test.py -v

test_calc_all_share_index (__main__.TestGBCE) ... ok
test_calc_dividend_yield (__main__.TestGBCE) ... ok
test_calc_pe_ratio (__main__.TestGBCE) ... ok
test_calc_stock_price (__main__.TestGBCE) ... ok
test_invalid_symbol (__main__.TestGBCE) ... ok
test_record_trade (__main__.TestGBCE) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.036s

OK
```
