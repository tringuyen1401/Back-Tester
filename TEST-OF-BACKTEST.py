#BACKTEST ALGORTIHM
#QUICK RUNDOWN:
#STEP 1: ACQUIRE ALL THE DATA FROM DATABASE
# - SCREENING PROCESS: LISTS OF ALL SCREEN CRITERIAS (RSI, EPS, etc.)
#                      SIGNS OF THESE
#                      VALUES AND RANKING (THE FIRST TO BE CHOSEN WILL BE ASSIGNED AS AMOST IMPORTANT AND SO ON)
# - BUYING STYLES: BUY WHEN PRICE IS, RSI IS, EMA IS, etc.
#                  AND (ALL NECESSARY CONDITIONS ARE MET) OR OR (ONE CONDITION IS MET)
#                  TIME OF WAITING: HOW LONG SHOULD ONE WAIT FOR ONE STOCK? 
# - SELLING STYLES : LIKE ABOVE BUT FOR SELL
# - PORTFOLIO FORMING STYLE: EQUAL WEIGHTS OR MINUMUM RISK ETC.
#                            PREFERRED NUMBERS OF POSITIONS
#                            HOW OFTEN SHOULD PORTFOLIO BE REBALANCED 

#STEP 2: SCREEN ALL THE CRITERIAS
# - SCREN ALL THE STOCKS THAT SATISFY THE CRITERIAS IN EVERYYEAR
# - MAKE A DATAFRAME OF WHICH STOCKS AND WHICH YEAR
# - GET A PRICE DATAFRAME OF ONLY STOCKS THAT SATISFY TO REDUCE THE SIZE

#STEP 3: BUY
#- CREATE A YEARLY PORFOLIO
#- CREATE A DECISION DATAFRAME TO DECIDE IF BUYING CONDITIONS ARE MET
#- FOOR LOOP TO RUN INTERVALS
#- IF STOCKS ARE PURCHASED, RECORD THE DATE, THEN ACQUIRE THE PRICE
#- FURTHER CALCULATIONS OF VALUES SUCH AS COMMISION, INITIAL VALUE, PRICE, WEIGHT, ETC.
#EVERYTHING IS DONE ACCORDINGLY TO HOW PORTFOLIO IS FORMED, CONTROLLED, AND EVALUATED.

#STEP 4: SELL
#- CREATE A DECISION DATAFRAME TO DECIDE IF SELLING CONDITIONS ARE MET
#THE REST IF LIKE BUY

#STEP 5: TRANSFER TO THE GENERAL PORTFOLIO OF THE YEAR
#- CALCULATION OF UNREALIZED PROFIT/LOSS
#- TRANSFER FINISHED TRANSACTION TO TRANSACTION DATAFRAME FOR RECORD
#- STOCKS THAT ARE YET SOLD ARE BROUGHT INTO NEXT YEAR YEARLY PORTFOLIO

#COMMON NAMES:
#PORT_AUX: AUXILIARY PORTFOLIO - THIS IS THE YEARLY PORTFOLIO THAT CHANGES EVERY YEAR/INVESTING HORIZON
#ANYTHING WITH _1 OR _2 SUCH AS PORT_AUX_1 IS DATA HOLDING DATAFRAME ONLY USED FOR CALCULATION
#PORTFOLIO: PORTFOLIO DATAFRAME
#PRICE_DATA: DATAFRAME WITH ALL STOCK PRICE
#PRICE_AUX: DATAFRAME WITH PRICE OF ONLY RELEVANT STOCKS IN ONLY 1 YEAR
#ANYTHING WITH BIN: BINARY-ONLY DATAFRAME TO DECIDE SELL OR BUY
#YEAR_START: IMPORTANT VARIABLE TO HELP CUT THE PRICE DATAFRAME, BINARY DECISION DATAFRAME, AND REALIZE IF YEAR/HORIZON IS OVER



import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import time

workpath = os.path

def commission(no_stock, money_spent):
        #Calculate commision:
            if no_stock < 300000:
                comm = 0.0035 * money_spent
            elif no_stock < 3000000:
                comm = 0.002 * money_spent
            elif no_stock < 20000000:
                comm = 0.0015 * money_spent
            elif no_stock< 1000000:
                comm = 0.001 * money_spent
            else:
                comm = 0.0005 * money_spent
            if comm >= 0.005 * money_spent:
                comm = 0.005 * money_spent
            print('done cal comm')
            return comm
        
def sell_end_year(df1, df2, value_money):
        try: #Get number of stocks:
            no_stock = df1[df1['stock_no'] != ""].sum()
            for i in range(len(df1['ticker'])):
                ticker = df1['ticker'].tolist() #Get ticker to easily index the price
                if pd.notnull(df1.ix[i]['day_purchased']) and df1.ix[i]['day_purchased'] != "":
                    if pd.notnull(df1.ix[i]['buy_price']) and df1.ix[i]['buy_price'] != 0 and df1.ix[i]['buy_price'] != "":
                        df1.set_value(i, 'day_sold', df2['Date'].iloc[-2]) #Record down day of sale
                        df1.set_value(i,'sell_price', df2.ix[df2.ix[:,ticker[i]],ticker[i]]) #Record price
                        df1.set_value(i, 'fin_value', df1.ix[i]['stock_no'] * df1.ix[i]['sell_price']) #Final values
                    else: #If didn't buy because conditions were not satisfied, everything is zero:
                        df1.set_value(i, 'day_sold', df2['Date'].iloc[-2])
                        df1.set_value(i,'sell_price', 0)
                        df1.set_value( i, 'fin_value', 0)
            df1['fin_value'] = df1['stock_no'] * df1['sell_price']
            end_value = df1[df1['fin_value'] != ""]['fin_value'].sum()
            value_money += end_value
            #Commision:
            val = commission(no_stock, end_value)
            value_money -= val
            
            return df1, value_money
        
        except Exception as e:
            print(str(e))
            return df1, value_money
            pass

def get_RSI(company_list): #Get RSI DF
    RSI_df = pd.read_csv(workpath.join('RSI.csv'))
    RSI_df = RSI_df.ix[:,company_list]
    return RSI_df

def get_data(signal_list, company_list):
    data_df_list = [None] * len(signal_list)
    if 'RSI' in signal_list:
        RSI_df = get_RSI(company_list)
        #Get position to assign to correct position to final df_list
        position = signal_list.index("RSI")
        #Assign to list
        data_df_list[position] = RSI_df
        
    return data_df_list

                #bin_buy_df= pd.concat([bin_buy_df, rsi_buy_df['bin']],axis = 1)
                #bin_buy_df = bin_buy_df.rename(columns = {'bin' : ticker[i+1]})
        
def decision_df(list_of_df, list_of_signs, list_of_values): #Decide whether or not buy conditions are satisfied:
    bin_list = []
    for i in range(len(list_of_df)):
        cal_df = list_of_df[i]
        bin_df = cal_df.copy() #Binary df. 1 means buy (sell) on this day. 0 means no
        bin_df = bin_df.drop('Date',1)
        if list_of_signs[i] == 0: #Less than condition:
            bin_df[bin_df < list_of_values[i]] = 0.000000001 #9 zeros, super small number
            bin_df[bin_df > list_of_values[i]] = 0
            bin_df[bin_df == 0.000000001] = 1 #All the super small changes to 1 which means okay to buy(sell)
        if list_of_signs[i] == 1: #Same logic as above:
            bin_df[bin_df > list_of_values[i]] = 1000000000 #9 zeros, super big number
            bin_df[bin_df < list_of_values[i]] = 0
            bin_df[bin_df == 1000000000] = 1
        bin_df['Date'] = cal_df['Date']
        bin_df = bin_df.fillna(0) #Fill in impossible value for NaN
        bin_df.to_csv(workpath.join('111_BIN.csv'))
        bin_list.append(bin_df)
        return bin_list

def final_decision(list_of_df,and_or_list): #Final decision if there are many conditions:
    final_bin_df = list_of_df[0] #First condition is always and
    for i in range(len(list_of_df)):
        final_bin_df = final_bin_df + list_of_df[i] #Plus the dataframes
        final_bin_df = final_bin_df.drop('Date',1) #Drop date cause they can't be compared
        if and_or_list[i] == 0: #This is and; if bin is greater than 1 it means 'and' is satisfied. if not 'and' is not.
            final_bin_df[final_bin_df > 1] = 1000000000 #9 zeros, super big number
            final_bin_df[final_bin_df < 2] = 0
            final_bin_df[final_bin_df == 1000000000] = 1 #Restore and condition satisfied to 1
        if and_or_list[i] == 1: #This is or; 1 is good enough. 0 is not.
            final_bin_df[final_bin_df > 0] = 1
            final_bin_df[final_bin_df == 0] = 0
    final_bin_df['Date'] = list_of_df[0]['Date'] #Restore dates
    return final_bin_df

def form_portfolio(port_list, df, start_money):
    if port_list[0] == 0: #Basic portfolio with equal auxiliary weight and value in beginning of year:
        df['weight_aux'] = 1/port_list[1]
        df['value_aux'] = start_money / port_list[1]
    return df
    
    
def main():
    temptime = datetime.datetime.now().time()
    print('Start at ' +str(temptime))
    #Get all screening data and prices:
    data = pd.read_csv(workpath.join('ratio.csv'))
    price_data = pd.read_csv(workpath.join('allprice.csv'), index_col=['Date'])
    
    #Time horizon:
    day = 2
    month = 2
    year = 2013
    time = datetime.date(year,month,day)
    today = datetime.date.today()
    #Time difference to get the first years:
    t = relativedelta(today,time).years
    #Restrict to 7:
    if t > 7:
        t = 7

    #Ask criteria:
    Crit_screen = ['ROA','ROE','eps'] #Criteria list
    Value_screen = [0.8,0.8,5] #Values of criteria
    Sign_screen =[1,1,1] #Signs of request: 0-less than 1- more than

    #Ranking the importance of the criterias.
    ranking = [10, 9 ,7] 
    
    #When to buy:
    Buy = 0 #Buy on first day
    Buy = 1 #Different from Buy = 0
    day_buy_ave = 30

    if Buy != 0:
        wait_day = 30 #ask for waiting day.
        #2 options:
            #Buy with all money and wait to sell to buy other stuff or
            #Always buy appropriate weights with regard to total stocks found
        #Ask for option:
        buy_opt = 3
        #ask if should spend all money after wait day or wait until can buy
        # 0 = spend all
        # 1 = wait forever
        if buy_opt == 0:
            #Ask for threshold of cash: (when cash is below this, don't  buy)
            cash_thres = 0.1 #in percentage of total wealth
        if buy_opt == 1:
            #Ask if new weights should include stocks already owned
            weight_opt = 0 #0 - no #1 - yes
            
    buy_signal = ['RSI'] #Signal value eg. RSI, other technical price values
    buy_signal_sign = [0] #Signs 0 = less than 1= more than
    buy_signal_value = [30] #The value duh
    buy_and_or = [0] #And or for many different signals. 0 - and 1- or. First one is always and.
    
    #When to sell:
    Sell = 1
    max_sell = 30
    min_sell = 25
    if Sell == 0:
        day_sell_ave = 30
    if Sell == 1:
        rsi_sell_lev = 40

    sell_signal = ['RSI'] #Signal sell
    sell_signal_sign = [1] #Signs 0 - less 1 - more
    sell_signal_value = [40] #Value list
    sell_and_or = [0]
    
    #How to form portfolio:
    start_money = 1000000
    Port = 0
    
    #Portfolio control list: style, preferred number of stocks, maximum number of stocks, ranking percentile
    port_crit = [0,10,15,0.5] 

    #Comission:
    comm = 0 #Define later
    ranking_list = []
    #Screen:
    stockname = pd.DataFrame(columns = ['ticker','year'])
    ranking_year = [] #Get all the years for a new list containing the names of the year for later use
    for i in range(t,0,-1):
        #Create list of columns' names and list of input criteria:
        critname = []
        critlist = []
        for p in range(len(Crit_screen)):
            #Append all the criterias and criteria values:
            if Crit_screen[p] == 'eps':
                critname.append(Crit_screen[p]+'_y'+str(i))
            else:
                critname.append(Crit_screen[p]+str(i))
                
            critlist.append(Value_screen[p])
            ranking_list.append(critname[p])            
        for k in range(len(critname)):
            #Screening: choose only items that satisfy:
            if Sign_screen[k] == 0:
                stocklist = data[data[critname[k]]<critlist[k]]
            if Sign_screen[k] == 1:
                stocklist = data[data[critname[k]]>critlist[k]]
            stocklist['year'] = 2016 - i
            stockname = stockname.append(stocklist)
            
        ranking_year.append(2016-i)
        
    #Ranking: These things can be quite confusing
    h = 0
    f = 0

    stockname_col = ['ticker','year'] #Final stockname dataframe will have these columns
    while h < len(ranking_list):
        for r in range(len(ranking_year)):
            sum_col = []
            while f < len(Sign_screen):
                col_name = ranking_list[h] + '_rank'
                #Get rank of the requirements:
                if Sign_screen[f] == 0:
                    stockname[col_name] = stockname.groupby('year')[ranking_list[h]].rank(ascending = True)
                    stockname[col_name] = stockname[col_name] * ranking[f]
                if Sign_screen[f] == 1:
                    stockname[col_name] = stockname.groupby('year')[ranking_list[h]].rank(ascending = False)
                    stockname[col_name] = stockname[col_name] * ranking[f]
                f += 1
                h += 1
                sum_col.append(col_name) #Get the column names to get total points later
                
            col_name = 'rank_' + str(ranking_year[r])
            #Summing all the points to find rank
            stockname[col_name] = stockname[sum_col].sum(axis=1)
            stockname_col.append(col_name)
            r += 1
            f = 0

    stockname = stockname.ix[:,stockname_col]
    stockname.to_csv(workpath.join('ranking.csv'))

    
    #Portfolio management. Create portfolio dataframe:
    total_value = 0
    cash = start_money
    portfolio = pd.DataFrame() #This portfolio goes from year to year
    transaction = pd.DataFrame() #Record all transaction
    #Create yearly auxiliary portfolio:
    for l in range(t,0,-1): #Reiterate over the course of time:
        start_money = cash
        year = 2016 - l +1
        col_name = 'rank_' + str(year-1)
        stockname_col = ['ticker','year',col_name] #Remove unnecessary ranks
        stockname_1 = stockname.ix[:,stockname_col]
        stockname_1 = stockname_1.rename(columns = {col_name : 'rank_point'}) #Change name to "rank_point"
        
        port_aux = stockname_1[stockname_1['year'] == 2016-l+1].drop_duplicates(cols = 'ticker') #Remove duplicate (stocks that satisfy too many conditions)
        port_aux['weight'], port_aux['weight_aux'], port_aux['value_aux'], port_aux['stock_no'], port_aux['buy_price'], \
                    port_aux['sell_price'], port_aux['ini_value'], port_aux['fin_value'],port_aux['day_purchased'],port_aux['day_sold'], \
                    port_aux['return'] = "", "", "", "", "", "", "", "", "" ,"", ""
        
        try: #Update ranking for stocks in portfolio
            ticker = portfolio['ticker'].tolist()
            stockname_2 = stockname_1[stockname_1['ticker'].isin(ticker)]
            portfolio = portfolio.sort(columns = 'rank_point')
            stockname_2 = stockname_2.sort(columns = col_name)
            portfolio = portfolio.drop('rank_point')
            portfolio['rank_point'] = stockname_2[col_name]
        except Exception as e:
            print(str(e))
            pass           
        
        port_aux = port_aux.append(portfolio) #Port_aux is the yearly portfolio that disappears and changes.
        port_aux = port_aux.drop_duplicates(['ticker'], take_last = True)
        port_aux = port_aux[port_aux['ticker'] != 'cash']
        port_aux['rank'] = port_aux['rank_point'].rank(ascending = True)
        port_aux = port_aux.sort(columns = 'rank')
        port_aux = port_aux.reset_index()
        port_aux = port_aux.drop('index',1)
        ticker = port_aux["ticker"].tolist() #get tickers that are relavant to shrink down size of price Dataframe
        price_aux = pd.DataFrame()

        port_aux.to_csv(workpath.join('000000_FIRST_PORT_A.csv'))
        if Buy == 0: #Easy buy thus start of the year
            start_date = datetime.date(2016-l+1,1,1)
            end_date = datetime.date(2016-l+1,12,31)
        if Buy != 0: #Need more dates for calculations
            start_date = datetime.date (2016-l,11,1)
            end_date = datetime.date(2016-l+1,12,31)
        year_start = datetime.date(2016-l+1,1,1)
        
        #Create new price dataframe:
        try:
            price_aux = price_data.ix[:,ticker] #Yearly price. Flexible price dataframe used for calculation
            price_aux = price_aux.reset_index()
            price_aux['Date'] = pd.to_datetime(price_aux['Date'])
            price_aux = price_aux[price_aux['Date'] > start_date]
            price_aux = price_aux[price_aux['Date'] < end_date]
            price_aux = price_aux.dropna(axis = 0, how='all')
            price_aux = price_aux.dropna(axis = 1, how='all')
            
        #Clean up the database to remove all empty columns and rows:
        #(Clean stocks whose prices are unavailable)
            ticker = list(price_aux.columns.values)
            port_aux = port_aux[port_aux['ticker'].isin(ticker)]
            port_aux = port_aux.reset_index()
            port_aux = port_aux.drop('index',1)
            price_aux = price_aux.reset_index()
            price_aux = price_aux.drop('index',1)
        except:
            pass

        
        price_aux.to_csv(workpath.join('testdata_price.csv'))
            

                  
        #Buying:
        begin_value = 0
        total_no = 0
        position_no = len(port_aux[port_aux['day_purchased'] != ""])
        print(position_no)
        #Buy = 0: Simple buy everything on first day:
        if Buy == 0:
            try:
                port_aux['day_purchased'] = start_date
                port_aux = form_portfolio(port_crit, port_aux, start_money)
                
                for i in range(port_crit[1]):
                    name = port_aux.ix[i,'ticker']
                    port_aux.set_value(i,'stock_no', port_aux.ix[i]['value_aux'] // price_aux.iloc[price_aux.iloc[:,i+1].first_valid_index(),i+1])
                    port_aux.set_value(i,'buy_price', price_aux.iloc[price_aux.iloc[:,i+1].first_valid_index(),i+1])
                #Evaluation:
                port_aux['ini_value'] = port_aux['stock_no'] * port_aux['buy_price']
                begin_value = port_aux['ini_value'].sum()
                #Commission:
                total_no = port_aux['stock_no'].sum()
                comm = commission(total_no, begin_value)
                
                port_aux['weight'] = port_aux['ini_value'] / begin_value
                cash = start_money - begin_value - comm
            except Exception as e:
                print(str(e))
                pass
                            

        #Buy with defined strategy:
        if Buy != 0:
            try:
                print(2016-l+1)
                bin_buy_df = pd.DataFrame()
                bin_buy_df['Date'] = price_aux['Date']
                

                #GET DATA and DECIDE:
                data_df_list = get_data(buy_signal, ticker) #Get all data for all necessary stocks
                bin_list = decision_df(data_df_list,buy_signal_sign,buy_signal_value)
                final_bin_df = final_decision(bin_list,buy_and_or)
                final_bin_df['Date'] = price_aux['Date']
                final_bin_df.to_csv(workpath.join('111_FINALBIN.csv'))
                                                    
                #Add while van con sell dc in the future
                print(price_aux.ix[301,'Date'])
                while year_start < datetime.date(2016-l+2,1,1) and year_start < price_aux.ix[price_aux.ix[:,'Date'].last_valid_index(),'Date'].date() + datetime.timedelta(days = 1): #Still this year
                    start_money = cash
                    print("++++++++++++++") 
                    name = port_aux.ix[i,'ticker']
                    #Make decisions binary DF:
                    final_bin_df_1 = final_bin_df[year_start < final_bin_df['Date']] #Make another final bin only in this time range
                    final_bin_df_1 = final_bin_df_1[final_bin_df_1['Date'] < year_start + datetime.timedelta(days=wait_day)]
                    final_bin_df_1 = final_bin_df_1.reset_index()
                    final_bin_df_1 = final_bin_df_1.drop('index',1)
                    print("ooooooooooooooo")
                    a =  0
                    while a < len(port_aux['ticker']) and position_no <= port_crit[1]:
                        switch = 0
                        b = 0
                        while switch != 1 and b < len(final_bin_df_1['Date']) and position_no <= port_crit[1] and start_money > -50000:
                            try:
                               if final_bin_df_1.ix[b,port_aux.ix[a,'ticker']] == 1 and port_aux.ix[a,'day_purchased'] == "":
                                  port_aux.set_value(a, 'day_purchased', final_bin_df_1.ix[b]['Date'].date())
                                  switch = 1
                                  position_no += 1
                            except Exception as e:
                               pass
                            b+=1
                        a += 1
                    print("FINISH THE SHITE")

                    port_aux = form_portfolio(port_crit, port_aux, start_money)
                    print('outta here')

                    #Calculate stock number and buy price.
                    new_stock = 0
                    new_value = 0
                    
                    for c in range(len(port_aux['ticker'])):
                        if pd.notnull(port_aux.ix[c]['day_purchased']) and port_aux.ix[c]['day_purchased'] != "" and port_aux.ix[c]['buy_price'] == "":
                           try: 
                                #Get index_no because pandas can't understand dates as index
                                print('WE HAVE' + str(start_money))
                                if start_money > -50000:   
                                    index_no = price_aux[price_aux['Date'] == port_aux.ix[c]['day_purchased']]
                                    index_no = index_no.index.tolist()[0]
                                    print('------------------')
                                    print(port_aux.ix[c,'ticker'])
                                    print('==================')
                                    port_aux.set_value(c,'buy_price', price_aux.ix[index_no,port_aux.ix[c,'ticker']])
                                    if port_aux.ix[c, 'buy_price'] != "" and pd.notnull(port_aux.ix[c, 'buy_price']):
                                        port_aux.set_value(c,'stock_no', port_aux.ix[c]['value_aux'] // price_aux.ix[index_no,port_aux.ix[c,'ticker']])
                                        #calculate ini_value here to avoid blank space:
                                        port_aux.set_value(c, 'ini_value', port_aux.ix[c]['stock_no'] * port_aux.ix[c]['buy_price'])
                                        new_stock += port_aux.ix[c,'stock_no']
                                        new_value += port_aux.ix[c,'ini_value']
                                    else:
                                        port_aux.set_value(c,'day_purchased', "")
                                else:
                                    port_aux.set_value(c,'day_purchased',"")
                           except Exception as e:
                                print(str(e))
                                print('fail')    
                                pass    

                    #Evaluation:
                    comm = commission(new_stock, new_value)

                    port_aux.to_csv(workpath.join('222_PORT_AUX.csv'))

                    for e in range(len(port_aux['ticker'])):
                        if pd.notnull(port_aux.ix[e]['day_purchased']) and port_aux.ix[e]['day_purchased'] != "":
                            port_aux['weight'] = port_aux.ix[e]['ini_value'] / begin_value
                    
                    cash = start_money - new_value - comm
                    print(cash)
                    
                    #Create new auxiliary to get average if sell at end of year or spend all     
                    if buy_opt == 0: #Buy all stocks in portfolio righ after wait_day
                        print("KKKKKKKKKKKKKKKKKKKKKK")
                        aux_df = port_aux[port_aux['day_purchased'] != ""]
                        aux_df_1 = aux_df[aux_df['day_purchased'] < datetime.date(2016-l,12,31)]
                        aux_df = aux_df[aux_df['day_purchased'] > datetime.date(2016-l,12,31)]
                        aux_df = aux_df.reset_index()
                        aux_df = aux_df.drop('index', 1)
                        ticker_1 = aux_df["ticker"].tolist() #ticker_1 all tickers in aux_df
                        price_aux_1 = price_data.ix[:,ticker_1]
                        price_aux_1 = price_aux_1.reset_index()
                        price_aux_1['Date'] = pd.to_datetime(price_aux_1['Date'])
                        price_aux_1 = price_aux_1[price_aux_1['Date'] > year_start + datetime.timedelta(days=wait_day)]
                        price_aux_1 = price_aux_1[price_aux_1['Date'] < end_date]
                        price_aux_1 = price_aux_1.reset_index()
                        price_aux_1 = price_aux_1.drop('index',1)
                        print("HHHHHHHHHHHHHHHHHHHHHH")
                        
                        if Port == 0:
                           aux_df['weight_aux'] = 100/len(aux_df)
                           aux_df['value_aux'] = cash / len(aux_df['ticker'])
                           
                        for d in range(len(aux_df['ticker'])):
                           if pd.notnull(price_aux_1.ix[:,d+1].first_valid_index()) and price_aux_1.ix[:,d+1].first_valid_index() != "None" and price_aux_1.ix[:,d+1].first_valid_index() != "":
                               name = aux_df.ix[d]['ticker']
                               aux_df.set_value(d,'stock_no', aux_df.ix[d]['value_aux'] // price_aux_1.ix[price_aux_1.ix[:,aux_df.ix[d,'ticker']].first_valid_index(),aux_df.ix[d,'ticker']])
                               aux_df.set_value(d,'buy_price', price_aux_1.ix[price_aux_1.ix[:,aux_df.ix[d,'ticker']].first_valid_index(),aux_df.ix[d,'ticker']])
                           else:
                               aux_df.set_value(d,'stock_no', 0)
                               aux_df.set_value(d,'buy_price', 0)
                        aux_df['ini_value'] = aux_df['stock_no'] * aux_df['buy_price']
                        port_aux = port_aux[port_aux['day_purchased'] != ""]
                        port_aux = port_aux[port_aux['day_purchased'] > datetime.date(2016-l,31,12)]
                        port_aux = port_aux.reset_index()
                        port_aux = port_aux.drop('index',1)
                        print("UUUUUUUUUUUUUUUUUUUUUUUUUU")
                        print(aux_df)
                        aux_df.to_csv(workpath.join('11111111_aux_for_check.csv'))
                        print(aux_df['ini_value'].sum())
                        
                        if aux_df['ini_value'].sum() != 0 : #Ignore if all the aux_df are zero
                            print('got in')
                            cash -= aux_df['ini_value'].sum()
                            comm = commission(aux_df['stock_no'].sum(), aux_df['ini_value'].sum())
                            aux_df['ini_value'] = aux_df['buy_price'] * aux_df['stock_no']
                            aux_df['weight'] = aux_df['ini_value'] / aux_df['ini_value'].sum()
                            cash -= comm
                            #Merge the two:
                            port_aux['ini_value'] = port_aux['ini_value'] + aux_df['ini_value']
                            port_aux['stock_no'] = port_aux['stock_no'] + aux_df['stock_no']
                            port_aux['weight'] = port_aux['ini_value'] / port_aux['ini_value'].sum()
                            #Change total worth of portfolio:
                            begin_value += port_aux['ini_value'].sum()       
                            aux_df.to_csv(workpath.join('11_AUX_DF.csv'))
                            price_aux_1.T.to_csv(workpath.join('11_PRICE_AUX_1.csv'))
                            port_aux.to_csv(workpath.join('11_PORT_AUX.csv'))
                            price_aux.to_csv(workpath.join('11_Price_AUX.csv'))

                        port_aux = port_aux.append(aux_df_1)
                        port_aux = port_aux.reset_index()
                        port_aux = port_aux.drop('index',1)
                        print("FINISH BUYING EVERYTHING")
                       
                    #De selling outside while cash > cash_thres
                    if Sell == 0:
                        port_aux, cash = sell_end_year(port_aux,price_aux,cash)
                        year_start = datetime.date(2016-l+2,1,1)
                        print("FINISH SELLING")

                    if Sell != 0:
                        earliest_buy = year_start
                        bin_sell_df = pd.DataFrame()
                        bin_sell_df['Date'] = price_aux['Date']
                        name = port_aux.ix[i,'ticker']

                        #GET DATA and DECIDE:
                        data_df_list = get_data(sell_signal, ticker) #Get all data for all necessary stocks
                        bin_list = decision_df(data_df_list,sell_signal_sign,sell_signal_value)
                        final_sell_bin = final_decision(bin_list,sell_and_or)
                        final_sell_bin['Date'] = price_aux['Date']
                        final_sell_bin = final_sell_bin[earliest_buy < final_sell_bin['Date']]
                        final_sell_bin = final_sell_bin[final_sell_bin['Date'] < year_start + datetime.timedelta(days=wait_day)]
                        final_sell_bin = final_sell_bin.reset_index()
                        final_sell_bin = final_sell_bin.drop('index',1)
                        final_sell_bin.to_csv(workpath.join('111_FINAL_sell_BIN.csv'))
                        print("SELLAAAAAAAAAAAAAAAAAAAAAAAAA")
                        for a in range(len(port_aux['ticker'])):
                            switch = 0
                            b = 0
                            while switch != 1 and b < len(final_sell_bin['Date']):
                                try:
                                   if final_sell_bin.ix[b,port_aux.ix[a,'ticker']] == 1 and port_aux.ix[a,'day_purchased'] != "":
                                      port_aux.set_value(a, 'day_sold', final_sell_bin.ix[b]['Date'].date())
                                      switch = 1
                                      position_no -= 1
                                except Exception as e:
                                   print(str(e))
                                   pass
                                b+=1
                                
                        for c in range(len(port_aux['ticker'])):
                            if pd.notnull(port_aux.ix[c]['day_sold']) and port_aux.ix[c]['day_sold'] != "":
                               #Get index_no because pandas can't understand dates as index
                               index_no = price_aux[price_aux['Date'] == port_aux.ix[c]['day_sold']]
                               index_no = index_no.index.tolist()[0]
                               try:
                                   port_aux.set_value(c,'sell_price', price_aux.ix[index_no,port_aux.ix[c,'ticker']])
                                   #calculate fin_value here to avoid blank space:
                                   if port_aux.ix[c,'sell_price'] != "" and pd.notnull(port_aux.ix[c,'sell_price']) and port_aux.ix[c,'sell_price'] != "NaN" and port_aux.ix[c,'day_sold'] > port_aux.ix[c,'day_purchased']:
                                       port_aux.set_value(c, 'fin_value', port_aux.ix[c]['stock_no'] * port_aux.ix[c]['sell_price'])
                                       print('------------------')
                                       print(port_aux.ix[c,'ticker'])
                                       print('==================')
                                       port_aux.set_value(c, 'return', (port_aux.ix[c]['sell_price'] - port_aux.ix[c]['buy_price'])/port_aux.ix[c]['buy_price'])
                                   else:
                                       port_aux.set_value(c, 'sell_price', "")
                                       port_aux.set_value(c, 'day_sold', "")
                                                                                      
                               except Exception as e:
                                   print(str(e))    
                                   pass
                               #Get the date and then set buy_price value
                                
                        #Evaluation:
                        final_value = port_aux[port_aux['fin_value'] != ""]['fin_value'].sum()
                        #Commission:
                        df_play = port_aux[port_aux['day_purchased'] != ""]
                        
                        if port_aux[port_aux['day_sold'] != ""]['day_sold'].dropna().min() == "" or pd.isnull(port_aux[port_aux['day_sold'] != ""]['day_sold'].dropna().min()):
                            year_start = year_start + datetime.timedelta(days=wait_day)
                            print(year_start)
                        else:
                            print(year_start)
                            year_start = port_aux[port_aux['day_sold'] != ""]['day_sold'].dropna().min() + datetime.timedelta(days = 1)
                            print(year_start)
                            print('WIN')
                            
                        #Values of stocks still holding:
                        df_play_2 = df_play[pd.isnull(df_play['day_sold'])]
                        df_play_2 = df_play_2[df_play_2['day_sold'] == ""]
                        unsold_value = df_play_2['ini_value'].sum() #THIS NEEDS REDONE CAUSE EVERY STOCKS NEED CURRENT VALUE
                        
                        #Values of sold stocks:
                        df_play_1 = df_play[df_play['day_sold'] == year_start - datetime.timedelta(days = 1)]
                        print(df_play_1)
                        sell_value = df_play_1['fin_value'].sum()
                        total_no = df_play_1['stock_no'].sum()
                        print("b4")
                        comm = commission(total_no, sell_value)

                        print('MONEY only_____ ' + str(cash))
                        cash += sell_value
                        print('MONEY is now_____ ' + str(cash))
                        
                        try:
                            print('after')
                            aux_df = port_aux[port_aux['return'] != ""]
                            aux_df = aux_df[aux_df['day_sold'] == year_start - datetime.timedelta(days = 1)]
                            transaction = transaction.append(aux_df)
                            regen_list = aux_df['ticker'].tolist()
                            year_list = aux_df['year'].tolist()
                            rank_list = aux_df['rank_point'].tolist()
                            rank_list_1 = aux_df['rank'].tolist()
                            print('henry')
                        except Exception as e:
                            print(str(e))

                        
                        print('cccccccccccccccc')
                        port_aux = port_aux[port_aux['day_sold'] != year_start - datetime.timedelta(days = 1)] #Plus 1 day
                        #Clear the stocks that have been bought and purchased:
                        for m in range(len(regen_list)):
                            port_aux.ix[len(port_aux)+1,'ticker'] = regen_list[m]
                            port_aux.ix[len(port_aux),'year'] = year_list[m]
                            port_aux.ix[len(port_aux), 'rank_point'] = rank_list[m]
                            port_aux.ix[len(port_aux), 'rank'] = rank_list_1[m]
                            
                        port_aux = port_aux.reset_index()
                        port_aux = port_aux.drop('index', 1)
                        port_aux = port_aux.fillna("")

                        port_aux = port_aux.sort(columns = 'rank')
                        print('whyuttttttttttttttttt')

                        #NEED TO SORT PRICE, PORT_AUX

                        port_aux.to_csv(workpath.join('11_PORT_AUX.csv'))
                        transaction.to_csv(workpath.join('transaction.csv'))
                                
                        
                        
            except Exception as e:
                aux_df.to_csv(workpath.join('11_AUX_DF.csv'))
                port_aux.to_csv(workpath.join('11_PORT_AUX.csv'))
                price_aux.to_csv(workpath.join('11_Price_AUX.csv'))
                print(str(e))
                print("tai toi co")
                pass
                            
        if Sell == 0:
            port_aux, price_aux, cash = sell_end_year(port_aux,price_aux,cash)
            for i in range(len(port_aux['ticker'])):
                try:
                    port_aux.ix[i,'return'] = (port_aux.ix[i,'fin_value'] - port_aux.ix[i,'ini_value']) / port_aux.ix[i,'ini_value']
                except Exception as e:
                    pass
            year_start = datetime.date(2016-l+2,1,1)
            print("FINISH SELLING")         
        
                

        #Selling:
        #Sell =2: Simple sell everything on last day:
        if Sell == 2:
            try:
                port_aux['day_sold'] = price_aux['Date'].iloc[-2]
                for i in range(len(port_aux['ticker'])):                   
                    port_aux.set_value(i,'sell_price', price_aux.iloc[price_aux.iloc[:,i+1].last_valid_index(),i+1])
                port_aux['fin_value'] = port_aux['stock_no'] * port_aux['sell_price']
                end_value = port_aux['fin_value'].sum()
                cash += end_value
                if total_no < 300000:
                    comm = 0.0035 * total_no
                elif total_no < 3000000:
                    comm = 0.002 * total_no
                elif total_no < 20000000:
                    comm = 0.0015 * total_no
                elif total_no < 1000000:
                    comm = 0.001 * total_no
                else:
                    comm = 0.0005 * total_no
                if comm >= 0.005 * end_value:
                    comm = 0.005 * end_value
                cash -= comm
            except Exception as e:
                print(str(e))
                pass                         
                
        #Return calculation for yearly portfolio:
        for i in range(len(port_aux['ticker'])):
            try:
                port_aux.ix[i,'return'] = (port_aux.ix[i,'fin_value'] - port_aux.ix[i,'ini_value']) / port_aux.ix[i,'ini_value']
            except Exception as e:
                pass
            
        path = workpath.join('test' +str(2016-l+1) + '.csv')
        port_aux.to_csv(path)

        #Transaction log:
        if Sell == 0:
            try:
                aux_df = port_aux[pd.notnull(port_aux['return'])]
                transaction = transaction.append(aux_df)
            except Exception as e:
                print(str(e))
        

        #Open position remains in portfolio:
        try:
            portfolio = pd.DataFrame()
            aux_df = port_aux[port_aux['buy_price'] != ""]
            portfolio = portfolio.append(aux_df)
            portfolio = portfolio[portfolio['day_sold'] == ""]

            portfolio = portfolio.drop('rank',1)

            portfolio_1 = portfolio.copy()
            portfolio_1, cash =  sell_end_year(portfolio_1, price_aux, cash)
            
            portfolio_1.set_value(len(portfolio_1)+1,'ticker',"cash")
            portfolio_1.set_value(len(portfolio_1),'fin_value',cash)
            portfolio_1.set_value(len(portfolio_1),'ini_value', start_money)
            portfolio_1.set_value(len(portfolio_1),'return', (cash - start_money)/start_money)

            
            for i in range(len(portfolio_1['ticker'])):
                try:
                    portfolio_1.ix[i,'return'] = (portfolio_1.ix[i,'fin_value'] - portfolio_1.ix[i,'ini_value']) / portfolio_1.ix[i,'ini_value']
                except Exception as e:
                    pass
        
            
            year = 2016-l+1
            name = str('portfolio') + str(year)
            path = workpath.join(name + '.csv')
            portfolio.to_csv(path)
            temptime = datetime.datetime.now().time()
            print('End at '+ str(temptime))
        except Exception as e:
            print(str(e))
            print("LOI LON")
            pass
        
            
            
        
                                
main()
