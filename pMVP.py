import pandas
import requests
import quandl
from yahoo_fin import stock_info as si
import pickle
# from rtstock.stock import Stock
#quandl API key=aQ-zkv2NbK2fzm4gUszY 
#alpha vantage API Key = YS8IJK901GY372CE
# from alpha_vantage.timeseries import TimeSeries
# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split
# from sklearn.svm import SVR 
from Mlmodel import *
import numpy as np

import pickle
import Mlmodel 

quandl.ApiConfig.api_key = 'aQ-zkv2NbK2fzm4gUszY'

#such as the stock ticker with prices & the industry comparison! Go crazy between now and TP3; and good luck :)


data, datesList= prepareFinalByStock('HistoricalQuotes (3).csv')
x, y=preparePriceAndDate(data)
def make2dMatrix(x):
    final=[]
    for i in range(len(x)):
        temp=[x[i]]
        final.append(temp)
    return final
x=np.reshape(x, (len(x), 1))



def getLivePrice(stock):
    mydata = si.get_live_price(stock) #quandl.get('EOD/AAPL')
    price=roundToNearestCent(mydata)
    return price

def getPriceList(L): #takes list of stocks and gets a list of prices for each one
    priceList=[]
    for i in range(len(L)):
        price=getLivePrice(L[i])

        priceList.append(price)
    return priceList

L=['aapl', 'fb', 'zm', 'snap', 'nflx', 'ntdoy', 'amzn']



with open('Mid_Gold.pickle', 'rb') as picky:
    ind=pickle.load(picky)



def industryAnalysis(ind):  #ind is a dictionary that comes from pickle, we now string parse 
                            #and try to get averages for everything 
    industryAverage={} # we create a dictionary for hte average value for each fundamental in industry
    stockList=[]
    for stock in ind: #stock is the ticker that maps to another dictionary of fundmentals
        fundamentals=ind[stock]
        stockList.append(stock)
        for item in fundamentals:
         
            if (item!='Index' and item!='Shortable' and item!='Optionable' and 
                item!='Earnings' and item!='Volatility' and item!='52W Range'): # we throw don't really care for these
                number=fundamentals[item]
                number=cleanNumber(number) #we clean it so we can analyze it later 
                if number!=None: #this avoids null values good cuz if we included we can screw up average
                  
                    if item not in industryAverage: #first time seen so we add it  list is used
                        industryAverage[item]=[number]  #so we can have an easier time averaging lists
                    else:
                        industryAverage[item].append(number)
   
    return industryAverage, stockList #returns formed dictionary with a list for every term
                                      #stock list is to access the numbers later 

def averageIndustry(industryAverage): #this gets the average for each catagory for the industry
    industryAverages={}
    for item in industryAverage:
        average=Mlmodel.avgList(industryAverage[item])
        industryAverages[item]=Mlmodel.roundToNearestCent(average) #this rounds to 2 decimal places
    return industryAverages


def cleanNumber(string): #takes a string and cleans out M, B, % and evaluates negative
    final=string
    tomultiply=1
    if string=='-': #this indicates blank Value retrieved
        return None
    if '%' in string:
        i=string.index('%')
        final=string[:i]
    if 'M' in string:
        tomultiply=1000000
        i=string.index('M')
        final=string[:i]   
    if 'B' in string:  
        tomultiply=1000000000
        i=string.index('B')
        final=string[:i]
    if 'K' in string:
        tomultiply=1000
        i=string.index('K')
        final=string[:i]
    if '-' in string:
        tomultiply=-1*tomultiply
    if ',' in string:
        number=string.split(',') #since volumes use commas 
        final=''
        for i in range(len(number)):
            final+=number[i]
    final=float(final)*tomultiply
    return final             


# ind, stockList=industryAnalysis(ind)
#print(averageIndustry(ind))
#Sprint(stockList) 
# print(si.get_quote_table('amzn'))

# # msft = yf.Ticker("MSFT")
# # print(msft.info)
# #print (getPriceList(L))


# content=requests.get('https://www.nasdaq.com/market-activity/stocks/aapl')
# print(content.json())

# popularTickers=si.tickers_sp500()
# with open(f'popularTickers1.pickle', 'wb') as picky:
#     pickle.dump(popularTickers, picky)

#print(si.get_live_price('aapl'))
#print(mydata)

# with open("popularTickers.pickle", "rb") as picky: 
#     popularTickers = pickle.load(picky)
# print('second', popularTickers)    

# ts = TimeSeries(key='YS8IJK901GY372CE',output_format='pandas')
# data, meta_data = ts.get_intraday(symbol='AAPL',interval='1min', outputsize='compact')
# print(data['4. close'][0])

#x=make2dMatrix(x)
#y=make2dMatrix(y)
#x=np.array(x)
#y=np.array(y)

# print('data', x, y)

#fitted= LinearRegression().fit(x, y)
# print(fitted.score(x, y))

# #https://medium.com/@randerson112358/predict-stock-prices-using-python-machine-learning-53aa024da20a 

# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
# svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)   #types of kernal: Linear, Polynomial, rbf, simoid

# svr_rbf.fit(x_train, y_train)
# # print(svr_rbf.score(x_test, y_test))
# # #print(fitted.predict(x))
# # print(y)
# # print(svr_rbf.predict(x))
