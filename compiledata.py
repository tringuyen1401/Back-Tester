import numpy as np
import pandas as pd
import datetime
import os

path = os.path


def main():
    data = pd.read_csv(path.join('ALL.csv'))
    finaldf = pd.DataFrame()
    
    #Get information columns
    finaldf = pd.concat( [finaldf,data['company'], data['ticker'], data['exchg_desc'],
                              data['smg_desc'], data['img_desc'], data['mktcap']], axis = 1)
    finaldf = finaldf.rename( columns = {'exchg_desc' : 'exchange', 'smg_desc' : 'sector', 'img_desc' : 'industry'} )

    #Get BS values to main data
    data = pd.read_csv('/Users/Tri/workspace/python/Data/IS.csv')
    finaldf = pd.concat([finaldf, data.ix[:,5:152]], axis = 1)
    
    #Get IS values to main data
    data = pd.read_csv('/Users/Tri/workspace/python/Data/IS.csv')
    finaldf = pd.concat([finaldf, data.ix[:,5:189]], axis = 1)
    
    #Ratio dataframe
    ratio = pd.DataFrame()
    ratio['company'] = finaldf['company']
    ratio['ticker'] = finaldf['ticker']
    for x in range(1,8):
        #Ratios with trailing:
        #Trailing Gross Profit Margin
        gi12 = "gross_12m"
        nr12 = "sales_12m"
        gpm12 = "grossprofitmargin12m"
        ratio[gpm12] = finaldf[gi12] / finaldf[nr12]
        #Trailing Operating Margin
        opm12 = "operatingprofitmargin12m" 
        oi12 = "gopinc_12m" 
        ratio[opm12] = finaldf[oi12] / finaldf[nr12]
        #Trailing Net Profit Margin
        npm12 = "netprofitmargin12m"
        ni12 = "netinc_12m" 
        ratio[npm12] = finaldf[ni12] / finaldf[nr12]
        
        #Current Ratio = Current Asset/ Current Liability
        cr = "currentratio" + str(x)
        ca = "ca_y" + str(x)
        cl = "cl_y" +str(x)
        ratio[cr] = finaldf[ca]/finaldf[cl]
        
        #Quick ratio = (cash + investment + receivables)/ current lib
        qr = "quickratio" + str(x)
        c = "cash_y" + str(x)
        i = "stinv_y" + str(x)
        r = "ar_y" + str(x)
        ratio[qr] = (finaldf[c] + finaldf[i] + finaldf[r])/finaldf[cl]
        
        #Cash ratio = (Cash + Investment) / current lib
        cr = "cashratio" + str(x)
        ratio[cr] = (finaldf[c] + finaldf[i])/finaldf[cl]
        
        #Debt to Asset Ratio = total lib / total ass
        dta = "debttoasset" + str(x)
        tl = "liab_y" + str(x)
        ta = "assets_y" + str(x)
        ratio[dta] = finaldf[tl] / finaldf[ta]
        
        #Debt to Capital Ratio = total debt / (total debt + equities)
        dcr = "debttocapitalratio" + str(x)
        ap = "ap_y" + str(x)
        sd = "stdebt_y" + str(x)
        ld = "ltdebt_y" + str(x)
        d = finaldf[ap] + finaldf[sd] + finaldf[ld]
        tle = "totloe_y" + str(x)
        se = finaldf[tle] - finaldf[tl]
        ratio[dcr] = d / (se + d)

        #Debt to Equity Ratio = total debt / total shareholder's equity
        dte = "debttoequityratio" + str(x)
        ratio[dte] = d/ se
        
        #Interest Coverage Ratio = EBIT / interest payment
        icr = "interestcoverageratio" + str(x)
        ni = "netinc_y" + str(x)
        it = "inctax_y" + str(x)
        ie = "int_y" + str(x)
        ieno = "intno_y" + str(x)
        ratio[icr] = (finaldf[ni] + finaldf[it] + finaldf[ie] + finaldf[ieno]) / (finaldf[ie] + finaldf[ieno])

        #Gross Profit Margin = Gross Income / Net Revenue      
        gpm ="grossprofitmargin" + str(x)
        gi = "gross_y" + str(x)
        nr = "sales_y" + str(x)
        ratio[gpm] = finaldf[gi] / finaldf[nr]

        #Operating Profit Margin = Operating Income / Net Revenue
        opm = "operatingprofitmargin" + str(x)
        oi = "gopinc_y" + str(x)
        ratio[opm] = finaldf[oi] / finaldf[nr]

        #Net profit margin = Net income / Net Revenue
        npm = "netprofitmargin" + str(x)
        ni = "netinc_y" + str(x)
        ratio[npm] = finaldf[ni] / finaldf[nr]

        #ROA = Net income/ total assets
        roa = "ROA" +  str(x)
        ratio[roa] = finaldf[ni] / finaldf[ta]

        #ROE = net income / total SE
        roe = "ROE" + str(x)
        ratio[roe] = finaldf[ni] / se

        #Inventory Turnover = cost of goods sold / average inventory
        if x < 7:
            it = "inventoryturnover" + str(x)
            i = "inv_y" + str(x)
            ily = "inv_y" + str(x+1)
            cogs = "cgs_y" + str(x)
            ratio[it] = finaldf[cogs] / ((finaldf[i] + finaldf[ily] ) /2)

        #Receivables Turnover = net revenue / average receivables
        if x < 7:
            rt = "receivablesturnover" + str(x)
            rly = "ar_y" + str(x+1)
            ratio[rt] = finaldf[nr] / ((finaldf[r] + finaldf[rly])/2)

        #Payables turnover = (cost of goods sold + ending inventory - beginning inventory) / average payables
        if x < 7:
            pt = "payablesturnover" + str(x)
            pa = "ap_y" + str(x)
            paly = "ap_y" + str(x+1)
            ratio[pt] = (finaldf[cogs] + finaldf[i] - finaldf[ily]) / ((finaldf[pa] + finaldf[paly])/2)
        
        #Asset Turnover = net revenues / average total assets
        if x < 7:
            at = "assetturnover" + str(x)
            ta = "assets_y" + str(x)
            taly = "assets_y" + str(x+1)
            ratio[at] = finaldf[nr] / ((finaldf[ta] + finaldf[taly]) / 2)
                
        
    #Get EMA 14 values to main data
    data = pd.read_csv('/Users/Tri/workspace/python/Data/EMA14.csv')
    rand = data.ix[len(data)-2][2:]
    rand = rand.reset_index()
    rand.columns = ['ticker' , 'EMA14' ]
    ratio = pd.merge( ratio, rand, on = 'ticker', how= 'outer')

    #Get EMA 22 values to main data
    data = pd.read_csv('/Users/Tri/workspace/python/Data/EMAFILE.csv')
    rand = data.ix[len(data)-2][2:]
    rand = rand.reset_index()
    rand.columns = ['ticker' , 'EMA22' ]
    ratio = pd.merge( ratio, rand, on = 'ticker', how= 'outer')

    #Get RSI values to main data
    data = pd.read_csv('/Users/Tri/workspace/python/Data/RSI.csv')
    rand = data.ix[len(data)-2][2:]
    rand = rand.reset_index()
    rand.columns = ['ticker' , 'RSI' ]
    ratio = pd.merge( ratio, rand, on = 'ticker', how= 'outer')
                                        
    ratio.to_csv(path.join('ratio.csv'))
    finaldf.to_csv(path.join('test.csv')) 
main()
                                          
