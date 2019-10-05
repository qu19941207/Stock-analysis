# This algorithm uses talib's STOCH function to determine entry and exit points.

# When the stochastic oscillator dips below 10, the stock is determined to be oversold
# and a long position is opened. The position is exited when the indicator rises above 90
# because the stock is thought to be overbought.

import talib
import numpy as np
import pandas as pd

# Setup our variables
def initialize(context):
    context.stocks = symbols('SPY', 'AAPL', 'GLD', 'AMZN')
    
    # Set the percent of the account to be invested per stock
    context.long_pct_per_stock = 1.0 / len(context.stocks)
    
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())

# Rebalance daily.
def rebalance(context, data):
    
    # Load historical data for the stocks
    hist = data.history(context.stocks, ['high', 'low', 'close'], 30, '1d')
    
    # Iterate over our list of stocks
    for stock in context.stocks:
        current_position = context.portfolio.positions[stock].amount
        slowk, slowd = talib.STOCH(hist['high'][stock],
                                   hist['low'][stock],
                                   hist['close'][stock],
                                   fastk_period=5,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)

        # get the most recent value
        slowk = slowk[-1]
        slowd = slowd[-1]
        
        # If either the slowk or slowd are less than 10, the stock is 
        # 'oversold,' a long position is opened if there are no shares
        # in the portfolio.
        if slowk < 10 or slowd < 10 and current_position <= 0 and data.can_trade(stock):
            order_target_percent(stock, context.long_pct_per_stock)
        
        # If either the slowk or slowd are larger than 90, the stock is 
        # 'overbought' and the position is closed. 
        elif slowk > 90 or slowd > 90 and current_position >= 0 and data.can_trade(stock):
            order_target(stock, 0)