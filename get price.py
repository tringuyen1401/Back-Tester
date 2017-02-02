import numpy as np
import pandas as pd
#import datetime
import pandas.io.data as web
import warnings
from datetime import timedelta, date
import datetime
from pandas.tseries.offsets import BDay
import os

path = os.path

def perdelta(start,end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def merge_file(y, y_max,path):
    a = pd.read_csv(path+'all_price'+str(y)+'.csv')
    if (y < y_max):
        a = pd.read_csv(path+'all_price'+str(y)+'.csv')
        return pd.concat([a,merge_file(y+1,y_max,path)], axis=1)
    
    else:
    #    a.dropna(axis=0)
        return pd.read_csv(path+'all_price'+str(y)+'.csv')
    

def main():
    temptime = datetime.datetime.now()
    print(temptime)
    warnings.filterwarnings("error")
#final df
    wtf = pd.DataFrame() 
    final = pd.DataFrame()
#unprocessed df
    unproc = pd.DataFrame()
    unproc['complist'] = ''
#number of unprocessed comp
    pos = 0
    #define date where we start fetching data, or check if any data exists
    try:
        maindf = pd.read_csv(os.path.join('allprice.csv'))
        final['Date'] = maindf['Date']
        day_num = len(maindf['Date'])
        
        start = datetime.datetime.strptime(str(maindf.loc[day_num - 1][0]), '%Y-%m-%d')
        end = datetime.datetime.today()
        status = "update"
        day = day_num
        for x in perdelta(start,end, timedelta(days = 1)):
            final.set_value(day,'Date',x)
            day+=1
    except (UnboundLocalError, OSError):        
        start = datetime.datetime(2010,1,1)
        end = datetime.datetime.today()
        day_num = 0
        maindf = pd.DataFrame()
        status = "new"
    complist = pd.read_csv(path.join('Data/companylist.csv'))
    #traverse through the company list
    for x in range(len(complist)):
        time = datetime.datetime.now()
        day_num1 = day_num 
        rsdf = pd.DataFrame()
        name = complist.ix[x]
        file_num = 1
        #fetch data
        try:
            data = web.DataReader(complist.ix[x], 'yahoo', start, end)
            print(complist.ix[x] + "'s Data obtained from Yahoo " + str(time.isoformat()))
        except:
            try:
                data = web.DataReader(complist.ix[x], 'google', start, end)
                print(complist.ix[x] + "'s Data obtained from Google " + str(time.isoformat()))
            except:
                try:
                    data = web.DataReader(complist.ix[x], 'fred', start, end)
                    print(complist.ix[x] + "'s Data obtained from Fred " + str(time.isoformat()))
                except:
                    continue
                continue
            print(complist.ix[x] + "Cannot be Obtained " + str(time.isoformat()))
            continue
       #create or append base on the status 
        if status == "new":
            rsdf[name] = data['Adj Close'] 
        else:
            try:
                rsdf[name] = maindf[name]
                rsdf.columns.values[0]='Adj Close' 
            except KeyError:
                unproc.set_value(pos,'complist',str(name))
                pos+=1                      
        comprice = data['Adj Close']
        if (status == "update"):
            rsdf = rsdf.append(comprice, ignore_index=True)
        rsdf.rename(columns= {'Adj Close' : str(name)}, inplace = True)
        if (status == 'new' and x == 0):
            #since it's new, add an index Date column from 2010 to today
            date = pd.date_range('20100101', end, freq=BDay())
            final = pd.DataFrame(rsdf[name], index=date)
        else:
            #dump the data for every 1000 companies to decrease processing time
            if (x%1000 == 0 and x != 0): 
                if file_num != 1:
                    final.to_csv(path.join('all_price'+str(file_num)+'.csv'), index = False)
                else:
                    final.to_csv(path+'all_price'+str(file_num)+'.csv', index= True)
                file_num += 1
                final = pd.DataFrame(rsdf[name])
            else:        
                final = final.join(rsdf[name])
    #dump all data frame to file
    final.to_csv(path+'all_price'+str(file_num)+'.csv', index = False)
    y = 1
    final = merge_file(y,file_num,path)
    final.rename(columns={'Unnamed: 0' : 'Date'} , inplace=True) 
    temptime = datetime.datetime.now()
    final.to_csv(path.join('all_price.csv'), index= False)
    #list of unprocessed companies due to not found data
    unproc.to_csv(path.join('unproc.csv'), index= False)
    print(temptime)



main()
