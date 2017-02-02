import numpy as np
import pandas as pd
import datetime
import math
import os

path = os.path


def main():
    complist = pd.read_csv(path.join('companylist.csv'))
    data = pd.read_csv(path.join('allprice.csv'))
    EMA = pd.DataFrame()
    EMA = pd.concat([EMA, data['Date']], axis = 1)
    #calculation of EMA
    for x in range(len(complist)):
        try:
            caldf1 = data[complist.ix[x]]
        except:
            continue
        name = complist.ix[x][0]
        caldf1["EMA"] = ""
        z=0
        w=0
        for y in range(len(caldf1)):
            ema = np.nan
            try:
                yema = caldf1.ix[y-1]['EMA']
            except:
                continue
            price = caldf1.ix[y][0]
            if z<23:
                if pd.notnull(caldf1.ix[y][0]) and caldf1.ix[y][0]!=0 and caldf1.ix[y][0]!="":
                    z+=1
                    w += price
                if z == 22:
                    startema = w/22
                    z+=1
                    caldf1.set_value(y, 'EMA', startema)
            try:
                ema = price*(2/23) + yema*(1-(2/23))
            except:
                continue
            if ema == np.nan:
                caldf1.set_value( y, 'EMA', yema)
            else:
                caldf1.set_value( y, 'EMA', ema)
            if caldf1.ix[y, 'EMA'] == np.nan:
                caldf1.set_value( y, 'EMA', yema)
            if yema == np.nan:
                print("nan?")
                
            y+=1
        x+=1
        caldf1 = caldf1.rename(columns = {"EMA" : str(name)})
        EMA = pd.concat([EMA, caldf1[str(name)]], axis = 1)
    EMA.to_csv(path.join('EMAFILE.csv'))
        
main()
            
            
    
