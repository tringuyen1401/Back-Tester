import numpy as np
import pandas as pd
import datetime
import os

path = os.path

def main():
    complist = pd.read_csv(path.join('companylist.csv'))
    data = pd.read_csv(path.join('EMA14.csv'))
    RSIdf = pd.DataFrame()
    RSIdf = pd.concat([RSIdf, data['Date']], axis = 1)
    for x in range(len(complist)):
        try:
            caldf1 = data[complist.ix[x]]
        except:
            continue
        name = complist.ix[x][0]
        caldf1["Change"] = ""
        caldf1["RSI"] = ""
        up = np.zeros(0)
        down = np.zeros(0)
        caldf1['Change'] = caldf1[str(name)].pct_change()
        RSI = float('nan')
        for y in range(len(caldf1)):
            if caldf1.ix[y]['Change'] > 0:
                if len(up) < 15:
                    up = np.append(up, caldf1.ix[y]['Change'])
                if len(up) ==  15:
                    up = np.delete(up, 0)
            elif caldf1.ix[y]['Change'] < 0:
                if len(down) < 15:
                    down = np.append(down, caldf1.ix[y]['Change'])
                if len(down) ==  15:
                    down = np.delete(down, 0)
            if len(up) > 13 and len(down) > 13:
                RS = (np.mean(up)/14)/(np.absolute((np.mean(down)/14)))
                RSI = (100 - (100 / ( 1 + RS)))
            caldf1.set_value(y, 'RSI', RSI)
        caldf1 = caldf1.rename(columns = {'RSI' : str(name)})
        RSIdf = pd.concat([RSIdf, caldf1[str(name)]], axis = 1)
        print(name)
    RSIdf.to_csv(path.join('RSI.csv'))
    
main()
            
                          
    
