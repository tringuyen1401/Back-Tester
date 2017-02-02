# Back-Tester

Includes files used to pull the stock price from Yahoo Finance/Google 
and then calculate the profit or loss base on those data to confirm the stratergy
of the investor

1)get price.py: get all the prices and dump to all_price.csv

2)calculate EMA/EMA14 and calculation RSI: calculate all the neccesary data for processing later
and dump all the calculated files to their responding names

3)compiledata: compile all the calculated data above, and make some extra calculations

4)TEST-OF-BACKTEST: The main component of the project, get the data from user and base on the strategy
givent to confirm if the plan is profitable or not
