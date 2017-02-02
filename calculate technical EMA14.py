import numpy as np
import pandas as pd
import datetime
import os

path = os.path

def main():
    complist = pd.read_csv(path.join('companylist.csv'))
    data = pd.read_csv(path.join('allprice.csv'))
    try :
        EMA = pd.read_csv(path.join('EMA14.csv'))
        for x in range(len(EMA['Date']),len(data['Date'])):
            EMA = pd.concat([EMA, data.ix[x]], axis=0)
    except:
        EMA = pd.DataFrame()
        EMA = pd.concat([EMA, data['Date']], axis = 1)

    for x in range(len(complist)):
        try:
            caldf1 = data[complist.ix[x]]
        except:
            continue
        try:
            status = "update"
            ema_comp= EMA[complist.ix[x]]
        except:
            status = "new"
            
        name = complist.ix[x][0]
        if (status == "new"):
            day = 0
            caldf1["EMA"] = ""
        else:
            day = len(ema_comp)
            caldf1['EMA']= EMA[name]
            print(caldf1)
        
        z=0
        w=0
        for y in range(len(caldf1)):
            ema = np.nan
            try:
                yema = caldf1.ix[y-1]['EMA']
            except:
                continue
            price = caldf1.ix[y][0]
            if z<15:                                              
                if pd.notnull(caldf1.ix[y][0]) and caldf1.ix[y][0]!=0 and caldf1.ix[y][0]!="":
                    z+=1
                    w += price
                if z == 14:
                    startema = w/14
                    z+=1
                    caldf1.set_value(y, 'EMA', startema)
            try:
                ema = price*(2/15) + yema*(1-(2/15))
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
    EMA.to_csv(path.join('EMA14.csv'))
        
main()
            
            
    
