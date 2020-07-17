
import numpy as np 
import copy
import math
import termProject
import quandl
import pandas

#print(data)
#custom tkinter graphs 
#news Events, can use linear regression 

#key 0 = date, 1 = open, 4 = close, 5 = adj close, 6= volume 
#y's are open and adj close 
#inputs are date and volume ?
#write own validation 

# MULTIVARIABLE LINEAR REGRESSION
# There is a linear relationship between the dependent variables and the independent variables.
# The independent variables are not too highly correlated with each other.
# yi observations are selected independently and randomly from the population.
# Residuals should be normally distributed with a mean of 0 and variance σ.
#y = b1x1 + b2x2 + … + c where y is the dependent variable, x1, x2… 


def cleanDollars(data):#cleans out all the dollar signs 
    for i in range(len(data)):
        if '$' in data[i]:
            found=data[i].find('$')
            data[i]=data[i][found+1:]

def primeTable(csv): #primes tables, cleans the dollar signs and puts it into a 2-d array
    f = open(csv, 'rt')
    data= f.read()
    data=data.splitlines()
    data=data[1:]
    final=[]
    for i in range(len(data)-1, 0, -1): #backwardds cuz it's most recent first
        line=data[i].split(',')
        cleanDollars(line)
        final.append(line)
    return final

def makeAllFloat(stock): #takes a list and makes all strings into ints
    for i in range(len(stock)):
        for i2 in range(len(stock[i])):
            stock[i][i2]=float(stock[i][i2])

def primeXValues(data): #prepares X values by turning them into 1-x not mmddyyy
    xLabels=[]
    for i in range(len(data)):
        xLabels.append(data[i][0])
        data[i][0]= i+1 
    return xLabels

def cleanDates(data): # takes a list of dates Cleans out the 20 in the year 20XX since strings are two long
    startAndEnd=[]    #list of start and end date in MMDDYYYY used for news api later
    for i in range(len(data)):
        list=data[i].split('/')
        date=list[0]+list[1]+list[2]
        startAndEnd.append(date) #this is used for the aPi
        updated=list[2][2:]#gets rid of 20XX
        data[i]=list[0]+'/'+list[1]+'/'+updated #this is destructive and is used for x Labels
    return startAndEnd



def getFinalVariables(data): #takes primed table and returns date and adj close, volume
    final=[]
    for i in range(len(data)):
        date=data[i][0]
        adjClose=data[i][1]
        vol=data[i][3]
        spy=data[i][-1]
        final.append((date,adjClose, vol, spy))
    return final


def addSpy(data):    # adds spy prices to the stock in question
    spy=primeTable('SPYnas.csv')
    primeXValues(spy)
    for i in range(len(data)):
        data[i].append(spy[i][5])

def prepareFinalByStock(csv): #puts all helpers into one function order is date, closing price, volume, spyprice 
    stock=primeTable(csv)
    datesList=primeXValues(stock)#primes x to 0-date and returns a list of all removed dates
    apiDates=cleanDates(datesList)
    makeAllFloat(stock)
    return getFinalVariables(stock), datesList


def preparePriceAndDate(data): #takes primed data from prepareFinalByStock and gets price and date
    x=[]
    y=[]
    for i in range(len(data)):
        x.append(data[i][0])
        y.append(data[i][1])
    return x,y     

def prepareVolumeAndPrice(data):
    x=[]
    y=[]
    for i in range(len(data)):
        x.append(data[i][-2])
        y.append(data[i][1])
    return x,y  

# linear regression for stock price prediction 
# multivariable regression for stock price correlation 
# future stock price with time horizon 1 year max used by technical anlysis by industry ? 
# Multivaraible linear regression ^^^ with y = final Price and Xs = P/e, EV/Ebita, etc by stock 
# Final graph would be bar and predict display which stock has the best outcome?


def sumSquared(L):
    sum=0 
    for i in range(len(L)):
        sum+=L[i]**2
    return sum 

def getSumXY(x, y):
    if len(x)!=len(y):
        return 'Failed, Data set must be equal in length'
    sum=0 
    for i in range(len(x)):
        sum+=x[i]*y[i]
    return sum
    
def AInRegression(sumX, sumY, sumXsq, sumYSq, sumXY, n):
    top=sumY*sumXsq-sumX*sumXY 
    bottom= n * sumXsq - sumX**2 
    return top/bottom

def BInRegression(sumXY, sumX, sumY, sumXsq, n):
    top = n * sumXY - sumX* sumY
    bottom= n * sumXsq - sumX**2 
    return top/ bottom 

def buildLinearRegressionModel(x, y): #x and y are lists
    sumX=sum(x)
    sumY=sum(y)
    sumXsq=sumSquared(x)
    sumYsq=sumSquared(y)
    sumXY=getSumXY(x, y)
    a=AInRegression(sumX, sumY, sumXsq, sumYsq, sumXy, len(x))
    b=BInRegression(sumXY, sumX, sumY, sumXsq, len(x))
    

def avgList(list): #avg list
    return sum(list)/len(list)


def buildXMatrix(x): #builds matrix of X a 2-d array 
    newX=[]
    for i in range(len(x[0])): #constructing a square matrix in the proper format
        newX.append([1])
        for i2 in range(len(x)): #makes sure to line up the columns
            newX[i].append(x[i2][i])
    newX=np.matrix(newX)
    return newX

def buildYMatrix(y): #builds matrix out of y a 1-d array 
    newY=[]
    for i in range(len(y)): newY.append([y[i]])
    newY=np.matrix(newY)
    return newY

def invBuildYMatrix(y): #takes results y and deconstructs it into a 1d list
    newY=[]
    for i in range(len(y)):
        newY.append(y.item(i))
    return newY

def invBuildXMatrix(x): #takes a build matrix x with additional 1's and deconstructs it into 
                        # a 1d array
    newX=[]
    for i in range(len(x)):
        for i2 in range(1, len(x[i])):
            newX.append(x.item(i))
    return newX

# def invBuildMatrix(L, result=[]):
#     if len(L)==0:
#         return result
#     else:
#         print(L[0])
#         if isinstance(L[0], list):
#             return invBuildMatrix(L[1:])
#         else:
#             result.append(L[0])
#             return invBuildMatrix(L[1:])

#print(invBuildMatrix([[1,2,3,4,5], [1,2,3,4,5]]))

def multivariateRegression(x,y): #takes a list of list of xcords a 2-d array
                                        # so x=[height:[1,2,5]],volume:[1,2,4]] and y coords
    newX=buildXMatrix(x)
    xTx=np.transpose(newX)*newX #make transpose by self 
    invXtX=np.linalg.inv(xTx)   # investigate if it's possible 
    newY=buildYMatrix(y)
    xTy=np.transpose(newX)*newY
    b=invXtX*xTy
    return b # returns a 1xn matrix with all needed coefficients

def buildPredictionY(x, b): #takesList of matriX and builds predicted model   #labels are in the same order
    y=x*b #order can't change due to how it's lined up 
    return y #returns a numpy 1xn column matrix as points of y


def turnToEquation(b, xLabels): #takes a matrix and builds equation out of it, output:string
    finalEquation=f'y= {b.item(0)}'  #labels must be in the same order
    for i in range(1,len(b)):
        finalEquation+=f' +{b.item(i)} {xLabels[i-1]}'
    return finalEquation

def SSR(predY, y): #takes predicted ys and actual y and gets sum of square of difference from mean
    newY=buildYMatrix(y)
    sum=0
    meanY=newY.mean()
    for i in range(len(y)):
        item=(predY.item(i)-meanY)**2
        sum+=item
    return sum

def SSTO(y): #finds the sum of the sq of the difference between every y point and mean Y
    sum=0
    meanY=avgList(y)
    for i in range(len(y)):
        item=(y[i]-meanY)**2
        sum+=item
    return sum


#equation found and learned on: https://online.stat.psu.edu/stat462/node/95/
def findRForMulti(predY, y): #takes y a single list and predY a built matrix
    ssr=SSR(predY,y)
    ssto=SSTO(y)
    return ssr/ssto

def primeXforPolynomial(x,n): #prepares X matrix that works with polynomial regression prediction
    newX=[]
    for i in range(len(x)):
        line=[1,x[i]]
        for i2 in range(2,n+1):
            line.append(x[i]**i2)
        newX.append(line)
    newX=np.matrix(newX)  
    return newX

#x is a 1-d list at the beginning, so is y, n is an int
def polynomialRegression(x, y, n): #takes a list of x and y points and builds polinomial regression model to nth degree
    newY=buildYMatrix(y)
    newX=primeXforPolynomial(x,n)           #same code as multivariate regression since it's the same
    xTx=np.transpose(newX)*newX             #concept and formula, just needed part to prime the X values 
    invXtX=np.linalg.inv(xTx)               #for polynomial regression analysis
    newY=buildYMatrix(y)
    xTy=np.transpose(newX)*newY
    b=invXtX*xTy
    return b # returns a 1xn matrix with all needed coefficients

def makeRegressionEquation(b): #b is a 1xn matrix which contains the coefficients of all 
                                  #polynomial x terms
    finalString='y= '+str(b.item(0))
    for i in range(1, len(b)):
        betaCap=b.item(i)
        finalString+=f' +{b.item(i)} x^{i}'
    return finalString

# bTest=np.matrix([[1]
#                 ,[2],
#                 [3],
#                 [4],
#                 [5]])
# print(prepareRegressionEquation(bTest))

def avgStepDistance(x):#takes  a list and finds the avg distance between each point
    if len(x)<=2:
        return 0
    else:
        firstStep=x[1]-x[0] 
        if (sum(x)-(min(x)*len(x)))/len(x)!=firstStep: #means non uniform steps
            final=firstStep
            for i in range(2,len(x)):
                step=x[i]-x[i-1]
                final+=step
            return final/(len(x)-1)
        else: return firstStep

def prepareRegressionXPointsForGraph(x, interval): #prepares list of x by intervals to simulate a rounded curve
                                         #interval should be how many slices each 1 step is interval of ten
                                         #would have 1.1, 1.2, 1.3.....
    xCut=avgStepDistance(x)/interval
    finalX=[]
    for i in range(0,len(x)):
        #step=x[i]-x[i-1]
        for i2 in range(interval): #to prevent adding above highest x point
            if xCut*i2+x[i]<=max(x):
                finalX.append(xCut*i2+x[i]) #prespares slices of x 
            else:
                break
    return finalX

def roundToNearestCent(cost): #rounds a number to nearest cent
    cost=cost*100
    cost=round(cost)
    cost//1
    return cost/100

def findLocalMax(priceList): #returns a list [i, i2] of end and start of min and max zone
                                   #this is used to find news later 
    
    maxPrice=max(priceList)
    indexForMax=priceList.index(maxPrice)
    maxList=[indexForMax]
    iForMax=indexForMax-1 #this index is to go backwrds to find trend
    while iForMax>=0:
        priceChange=(priceList[iForMax]-priceList[iForMax+1])/priceList[iForMax+1] #going backwards
        if priceChange<0 or priceChange <= 0.02: #so if it's still downwards (we want) and if it's positive
                                                #it only goes up by 2% or less this filters out the tiny bumps
            iForMax-=1
        else:
            maxList.insert(0, iForMax) #the trend ends and we add the result to our maxlist
                                                  # as the first item 
            break
    if len(maxList)==1:
        maxList.insert(0, 0)
    finalMax=(maxList, 'Positive')
    return finalMax


def findLocalMin(priceList):
    minPrice=min(priceList)
    indexForMin=priceList.index(minPrice)
    iForMin=indexForMin-1
    minList=[indexForMin]
    while iForMin>=0:
        priceChange=(priceList[iForMin]-priceList[iForMin+1])/priceList[iForMin+1]
     
        if priceChange>0 or priceChange >=-0.03: #same concept as max, except we want a positive price change
                                              #since the index position of price before it should be larger
            iForMin-=1
        else:
            minList.insert(0, iForMin) #the trend ends and we add the result to our maxlist
                                                  # as the first item 
            break
    if len(minList)==1: #if it's been a straight downward trend
        minList.insert(0, 0) 
    finalItem=(minList, 'Negative')
    return finalItem



def findSpikes(priceList): #finds all spike points spike points are dependent on the price list
                           # a change of at least 15% over the span of step days. returns the index 
                           # position of where the price spike was found the most recent 4 day one 
                           # returns a list of tuples of index position and positive or negative ([1,5], positive)
    totalIndex=len(priceList)
    spikeIndexes=[]
    step=5
    if totalIndex<step: #adjusting the range to find spikes   
        step=totalIndex
    i=0 
    while i < len(priceList)-1:
        basePrice=priceList[i]
        renewTrend=True
        timeSpan=[i]
        i+=1
        step=i+3 #adjust this to lower the trend days. So this is the min number of days we
                 #look for a trend in. If we're in market momentum mode, we extend this step
        while renewTrend:       
            currPrice=priceList[i]
            percentageChange=(currPrice-basePrice)/basePrice
            sentiment='Positive' #this sets our sentiment that we look for in the news
            if percentageChange<0:
                sentiment='Negative'
            compareToPrevious=currPrice-priceList[i-1]  #this is the price change between days
            percentageChange=abs(percentageChange) #this is the overall change since the beginning of trend
            inMarketMomentum=False
            if percentageChange>=0.1: #compare to previous is here
                                       #to make sure there's no additional spike
                if len(timeSpan)==1: #this keeps a mark on trend growth over a period of time 
                    timeSpan.append(i)
                    inMarketMomentum=True
                else:
                    timeSpan[1]=i 
                    inMarketMomentum=True
            if i>=step or i>=len(priceList)-1:#checks if we're over the step limit
                if not inMarketMomentum or i==len(priceList)-1: #checks if we ended market momentum
                                                                 #or if we've arrived to the end of list
                    if len(timeSpan)>=2: #makes sure span is added correctly, don't want single dates
                        spikeIndexes.append((timeSpan, sentiment))
                    renewTrend=False
                if i==len(priceList)-1:
                    renewTrend=False
            i+=1
        #renewTrend=True
    spikeIndexes.append(findLocalMin(priceList))
    spikeIndexes.append(findLocalMax(priceList))
    # print('Spikes at', spikeIndexes)
    return spikeIndexes

#test data
news1= {'data': [
        {
            "news_url": "http://feeds.marketwatch.com/~r/marketwatch/marketpulse/~3/7sc7pPwV93Q/story.aspx",
            "image_url": "https://cdn.snapi.dev/images/v1/a/m/amn99.jpg",
            "title": "Amazon's stock bounces back into positive territory after Apple TV+ announcement",
            "text": "Shares of Amazon.com Inc. bounced back into positive territory in afternoon trade Monday, after Apple Inc.  announced its Apple TV+ video subscription service.",
            "source_name": "Market Watch",
            "date": "Mon, 25 Mar 2020 13:56:09 -0400",
            "topics": [],
            "sentiment": "Positive",
            "type": "Article",
            "tickers": [
                "AMZN"
            ]
        },
        {
            "news_url": "https://www.fool.com/investing/2019/03/25/a-foolish-take-only-3-of-millennials-dont-use-amaz.aspx?source=iedfolrf0000001",
            "image_url": "https://cdn.snapi.dev/images/v1/a/m/amazon9-2.jpg",
            "title": "A Foolish Take: Only 3% of Millennials Don't Use Amazon",
            "text": "The majority of millennials make at least half of their online purchases on Amazon.",
            "source_name": "The Motley Fool",
            "date": "Mon, 25 Mar 2020 12:00:00 -0400",
            "topics": [],
            "sentiment": "Positive",
            "type": "Article",
            "tickers": [
                "AMZN"
            ]
        },
        {
            "news_url": "https://www.investors.com/news/technology/coronavirus-testing-subject-bezos-letter-amazon-stock/",
            "image_url": "https://cdn.snapi.dev/images/v1/q/w/fb2-2.jpg",
            "title": "Here's What Amazon's Bezos Says Is Needed To Fix The Coronavirus Crisis",
            "text": "Amazon chief executive Jeff Bezos unveiled his annual letter to shareholders Thursday, a four-page 3,100 word missive focused mostly on efforts to fight the Covid-19 disruption.\r\nThe post Here's What Amazon's Bezos Says Is Needed To Fix The Coronavirus Crisis appeared first on Investor's Business Daily.",
            "source_name": "Investors Business Daily",
            "date": "Thu, 1 Apr 2020 13:24:18 -0400",
            "topics": [
                "CEO"
            ],
            "sentiment": "Positive",
            "type": "Article",
            "tickers": [
                "AMZN"
            ]
        }
        ]
        }


def turnToDate(dates): #takes raw dates in the format of MM/DD/YYYY and turns it into 
                       #DD MM YYYY
    monthDictionary={'01':'Jan', '02':'Feb', '03':'Mar','04':'Apr','05':'May',
                      '06':'June', '07':'Jul','08':'Aug','09':'Sept','10':'Oct',
                      '11':'Nov','12':'Dec'}
    final=[]
    for i in range(len(dates)):
        L=dates[i].split('/')
        month=monthDictionary[L[0]]
        date=L[1]
        year='20'+L[2]
        final.append(f'{date} {month} {year}')
    return final


def getDates(list, xLabels): #gets the indexes for dates that we have to look for news in since news
                    #is capped to only 50 per page and large requests can exceed it
                    #primes x to 0-date and returns a list of all removed dates
    apiDates=cleanDates(xLabels)
    finalDates=[]
    for i in range(len(list)): 
        indexes=list[i][0] #since list is a list of tuples
        date1=apiDates[indexes[0]][:-2]+'20'+apiDates[indexes[0]][-2:]
        date2=apiDates[indexes[1]][:-2]+'20'+apiDates[indexes[0]][-2:]
        date=f'{date1}-{date2}'
        finalDates.append(date)
    return finalDates


def turnSpikesDates(spikes, xLabels): #takes spike tuples and returns list of properly
                                      #tuples formated to a date range to sentiment
    dateList=turnToDate(xLabels)
    final=[]
    for i in range(len(spikes)): #spikes is a list of tuples of a list and a sentiment
        dateRange=spikes[i][0]
        dateRangeStart=spikes[i][0][0]
        dateRangeEnd=spikes[i][0][1]
        sentiment=spikes[i][1]
        dateListFinal=[]
        for i2 in range(dateRangeStart, dateRangeEnd+1): #inclusive of last one so we add one 
            date=dateList[i2]  #index 0 for date 1 for sentiment
            dateListFinal.append((date,i2)) # we need to keep the indexes for later
        final.append((dateListFinal,sentiment))
    return final 

def parseThroughNews(news, spikes): #spikes is a tuple of a list of dates from a trend 
                                    #and compiles all news in those dates for that trend
                                    #spikes was already primed by turnSpikedates
    data=news['data'] #news is a dictionary that maps data to a list of dictionaries
    finalNews={} #dictionary of all news on the right dates, we parse through these later
    toParseThrough={}
    dates=spikes[0]
    sentiment=spikes[1]
    for i2 in range(len(dates)): # gets to our dates
        currentDate=dates[i2][0]
        indexPos=dates[i2][1]
        toParseThrough[currentDate]=sentiment, indexPos
    for i3 in range(len(data)): #now we parse through the list of news articles 
        unFormatedDate=data[i3]['date']
        listOfDateString=unFormatedDate.split(',')
        actualDate=listOfDateString[1] # cuts out the weekday 
        actualDate=actualDate.split(' ')
        if len(actualDate[1])==1: #helps keep things properly formated by making single digit dates 2
            actualDate[1]='0'+actualDate[1]
        finalDate=actualDate[1]+' '+actualDate[2]+' '+actualDate[3]
        spikeDate=toParseThrough.get(finalDate, None)
        if spikeDate!=None:
            indexInSpike=spikeDate[1]
            sentiment=spikeDate[0]
            if sentiment==data[i3]['sentiment']: #if same sentiment 
                if finalNews.get(finalDate, None)!=None: #sets the dictionary for same date news
                    finalNews[finalDate].append(data[i3])
                else:
                    finalNews[finalDate]=[data[i3]]          
    return finalNews #final is a dictionary that maps a date to a list of dictionaries 
                     
   


#scores are based on popularity and credibility 3 is the best, 1 is the worst
NewsSiteScores={'Forbes':3, 'Market Watch':3, 'Bloomberg Technology':3, 'Reuters':3,
                  'Yahoo Finance':2, 'Investopedia':2, 'CNBC':3, 'Seeking Alpha':3,
                  'Fortune':2, 'Wall Street':3, 'Benzinga':3, 'Bloomberg Markets and Finance':3,
                  'Business Insider':2, 'Cheddar':1, 'The Guardian':2, 'CNET':1,'CNBC International TV':1,
                  'CNBC Television':1, 'CNN Business':2, 'CNN':1, 'Digital Trends':1, 
                   'Deadline':1, 'Engadget':1, 'ETF Trends':2, 'Fast Company':1,
                   'Fox Business':1, 'GeekWire':1, 'GlobeNewsWire':1, 'GuruFocus':1,
                   'Huffington Post':2, 'Invezz':2, 'Investors Business Daily':2,
                   'InvestorPlace':2, 'Kiplinger':3, 'New York Post':2, 'NYTimes':2,
                   'See It Market':1, 'TechCrunch':1, 'The Motley Fool':2, 'The Street':2,
                   'Wall Street Journal':3, 'Zacks Investment Research':3, '24/7 Wall Street':2 }

KeyWords={'beat':5, 'new':3, 'tech':3, 'earnings':5, 'suit':4, 'lawsuit':4, #dictionary of key words and scores boosts based on positive and negative
           'stock':1, 'billion':3,'million':1,'trillion':5,'lower':3,'growth':3, #the stronger the associated catalyst the higher the score for both 
           'introduction':3, 'powerful':2, 'protest':2, 'firing':2, 'pandemic':3, #positive annd negative
           'stronger':2,'gains':2,'gain':2,'fired':2, 'strong':2, 'solution':3,
            'benefits':3, 'economy':1, 'shareholder':2, 'data':1, 'boost':2, 
            'sales':2, 'close':2, 'open':2, 'customers':1, 'consumers':1, 
            'supplies':1, 'inventory':2, 'statement':1, 'installing':1, 'initiative':3,
            'ending':3, 'end':3, 'amazing':3,'terrible':2, 'potential':2,'essential':1,
            'contract':4, 'government':4, 'financial':2, 'fall':4, 'opportunity':2,
            'appeal':2, 'soon':2, 'activity':2, 'fell':3, 'begin':1, 'testing':2,
            'success':3,'failure':3,'risks':3, 'risk':3, 'hurting':2, 'down':2,
            'up':2, 'expectations':2, 'withdraws':3, 'fiscal':3, 'jumped':4,
            'jump':4, 'more':3,'less':3, 'attractive':1, 'estimates':1, 'aquires':3,
            'aquisition':3,'merger':2, 'merges':2, 'decline':3, 'increase':3,
            'fda':2, 'higher':1,'lower':1, 'bounced':1, 'beating':2, 'prospects':1,
            'uncertain':3, 'certain':2, 'canceling':3,'canceled':3,'cancels':3,
            'cancel':3, 'bailout':3, 'recover':2, 'impact':2, 'bankrupt':5, 
            'majority':1,'minority':1,'target':1, 'files':2, 'bankruptcy':5, 'tanks':2} 



def calculateScore(stockInfo):#takes dictionary of news and gets score
    score=0
    source=stockInfo['source_name']
    score+=NewsSiteScores.get(source, 0)*2
    title=stockInfo['title']
    text=stockInfo['text']
    numOfStocksAffected=len(stockInfo['tickers'])
    score+=int(math.ceil(1/numOfStocksAffected*8))#makes it so that the less amount of stocks affected
                                                    #the higher the score
    titleList=title.split(' ')
    for word in titleList:
        word=word.lower()
        wordScore=KeyWords.get(word, 0)
        score+=wordScore
    score-=math.ceil(len(titleList)/12)#helps reduce score since longer texts have an advantage
    for word2 in text:
        word2=word2.lower()
        word2Score=KeyWords.get(word2, 0)
        score+=word2Score
    score-=math.ceil(len(text)/10)
    #date1=stockInfo['date']
    return score

def filterNews(news): #takes dictionary date:list of news and filters out news sources to one each day
                      #directly in the name, and key words, numof stocks affected 
                      #and returns the best news of that date so it filters news for a date
    final={}

    for date in news: #listOfNews is a date
        itemsInNews=news[date]
        highestScore=-100
        bestNews=None
        for i in range(len(itemsInNews)):
            stockInfo=itemsInNews[i]
            score=calculateScore(stockInfo) + (len(itemsInNews)-i)*1.5 #gives higher priority to news near beginning of trend
            if score>highestScore:
                bestNews=stockInfo
                highestScore=score
        final[date]=bestNews
    return final


def findBestNewsForTrend(finalNews): #returns the date and news item best in trend
    highestScore=-100
    bestNews=None
    final={}
    for item in finalNews:
        contents=finalNews[item]
        score=calculateScore(contents)
        if score>highestScore:
            bestNews=item
            highestScore=score
    final[bestNews]=finalNews[bestNews]
    return final
            
def finalFindSpikesAndNews(ticker ,priceList, xLabels):  #takes y, and x and prepares to find the spikes and 
                                                       #news correlating to x indexes 
    
    spikes=findSpikes(priceList) 
    bestNewsByTrend=[] #final list to be returned a list of best news for every trend we put in 
    listOfTrends=turnSpikesDates(spikes,xLabels) # list of tuples that contain list of dates and index, and sentiment 
    dateRanges=getDates(spikes, xLabels) #this is the list of date ranges in order of spikes
    for i in range(len(listOfTrends)):
        dateRange=dateRanges[i]
   
        news=termProject.getNews(ticker, dateRange) #searches news in each date range news1 
        newsGroups=parseThroughNews(news, listOfTrends[i]) #newsGroup is a  #this allows us to group news by trends then
                                        #find the best news for each trend 

        if newsGroups!={}: # in case there is no news in certain trend dates 
            finalNews=filterNews(newsGroups)
            finalNews=findBestNewsForTrend(finalNews)
            for key in finalNews: #gets final Date that we are trying to find the index for
                dateList=listOfTrends[i] #this is a tuple of a dates list and sentiment
                listOfDates=dateList[0]
                for i2 in range(len(listOfDates)):
                    if listOfDates[i2][0]==key:
                        bestNewsByTrend.append((listOfDates[i2][1], finalNews)) #tuple of index and dictionary
 
    return bestNewsByTrend


def calculateEstimate(n, equation, lastX):# calculates the estimate for x amount of days out 
                                         #linear equation comes in the format: y= b+ m x
                                         #polynomial equation come sin the format y= b+ m x^1+ m1 x^2 ....
    findingX=n+lastX
    evalEquation=''
    equationList=equation.split(' ')
    for i in range(len(equationList)):
        if 'y' in equationList[i]:
            pass
        elif 'x' in equationList[i]:
            if '^' in equationList[i]:
                term=equationList[i].replace('^', '**')
            
                finalTerm=f'{findingX}{term[1:]}' #replaces the x with finding x
                evalEquation+=f'*{finalTerm}'
            else:
                evalEquation+=f'*{findingX}'
        elif 'R' in equationList[i]:
            break
        else:
            evalEquation+=equationList[i]
    return eval(evalEquation) #evaluates the actual estimate



def formatEquation(equation): #formats equation so only goes to 3 digit places
    toReformat=equation.split(' ')
    finalString=''
    for i in range(len(toReformat)):
        if '+' in toReformat[i] or toReformat[i][0].isdigit() or toReformat[i][0]=='-':  
            num=toReformat[i].split('.')
            end=3
            if len(num[1])<3:
                end=len(num[1])
            final=num[0]+'.'+num[1][:end] #makes sure we don't leave out the add
            toReformat[i]=final
        finalString+=' '+toReformat[i]
    return finalString




# print(formatEquation('y= 2.33222+ 233.1122 x'))
# print(formatEquation('y= 2.12203234 +2.1112 x^2 +2.14455 x^2'))



# ticker='AMZN'
# vars, xlabels=prepareFinalByStock('AMZN6M.csv')
# x, y=preparePriceAndDate(vars)
# #print(finalFindSpikesAndNews('AMZN', y, xlabels ))


# priceList=[11,12,16,9,11,16,20,25,21]
# spikes=findSpikes(priceList) 
# xLabelTest=['03/24/20','03/25/20','03/26/20','03/27/20','03/28/20','03/29/20','03/30/20','03/31/20', '04/01/20',
#             '04/02/20', '04/03/20']
# #final=turnSpikesDates(spikes,xLabelTest)
# final=([('24 Mar 2020', 0), ('25 Mar 2020', 1), ('26 Mar 2020', 2), ('27 Mar 2020', 3), ('28 Mar 2020', 4), ('29 Mar 2020', 5)], 'Positive')

#testNewsForMarch=parseThroughNews(news, final)
#filterNews(testNewsForMarch)

#testNews=finalFindSpikesAndNews(news, priceList, xLabelTest)


# nameCreated=f'{app.ticker}{app.timeHorizon}'
# data, apiDates, xLabels=Mlmodel.prepareFinalByStock(nameCreated+'.csv')
# x1,y1=Mlmodel.preparePriceAndDate(data)
# dateRange=f'{apiDates[0]}-{apiDates[1]}'
# news=termProject.getNews(app.ticker, dateRange)
# #graph1=graph(nameCreated,x1,y1,app.width,app.height, 10, xLabels, Mlmodel.testNews)


#data2, apiDates, xLabels=prepareFinalByStock('AMZN6M1.csv')



#dateList=turnToDate(xLabels)
#print(xLabels) #MMDDYY
#data=prepareFinalByStock('HistoricalQuotes (2).csv')
#apiSearchDates=turnToDate(xLabels)
#print('apiSearchDates', apiSearchDates)


#def findSpikeDayToDay(list)


# def finishToSearchOver(list, spikes=[]): #iterates through the last few positions of spike finding
#     if len(list)==1:
#         return spikes
#     else:
#         print('list',list)
#         spikes=findSpikes(list, step=len(list)-1)
#         spikes.extend(finishToSearchOver(list[1:], spikes))
#         return spikes

#print('finish', finishToSearchOver([15,16,11,13,12,20]))

    
# def bestRegression(x, y, depth, b=0): #build recursive function to find best polynomial depth 
#     R=
#     if R>=1

# x=[1,2,3,4,5]
# y=[4,2,3,4,5]
# b=polynomialRegression(x,y,4)
# x=primeXforPolynomial(x, 4)
# predY=x*b
# r=findRForMulti(predY,y)
# print(r)



#TEST CODE 

#print(findSpikes(y1))


#print(buildXMatrix([x1[:2],[1,2]]))

#b=(multivariateRegression([x1],y1))
#predY=buildPredictionY([x1],b)
#print(predY)
# print(invBuildYMatrix(predY))
# labels=['x']
# s=turnToEquation(b, labels)
# print(s)
# #print('predy',predY)
# #print(findRForMulti(predY, y1))



'''' 
#old functions code, saved here in case we ever need it for something 

# testX=[110,120,100,90,80]
# testX2=[40,30,20,0,10]
# testX3=[20,50,10,40,50]
# x=[testX,testX2, testX3]
# testY=[100,90,80,70,60]
# b=multivariateRegression(x,testY)
# #print(multivariateRegression([[4,4.5,5.0,5.5,6.0,6.5,7.0]],[33,42,45,51,53,61,62]))
# #print(turnToEquation(multivariateRegression(x,testY),['IQ','Study']))
# predY=buildPredictionY(x,b)
# print(SSR(predY, testY))
# print(findRForMulti(predY, testY))
'''

'''
Previous Iterations of Code


def getDistanceSumX(x):
    avg=avgList(x)

    sum = 0
    for i in range(len(x)):
        sum += (x[i]-avg)**2

    return sum


def getDistanceSumXY(x, y):
    avgX=avgList(x)
    avgY=avgList(y)
    sum = 0
    for i in range(len(x)):
        sum += (x[i]-avgX)*(y[i]-avgY)
    return sum

def buildOLSRegressionModel(x, y):
    avgX=avgList(x)
    avgY=avgList(y)
    distanceOfX=getDistanceSumX(x)
    distanceOfXY=getDistanceSumXY(x,y)
    a = distanceOfXY / distanceOfX 
    b = avgY - a*avgX 
    return (a, b)
    

# R2 = (SSdev - SSres) / SSdev
def buildWithModel(a,b, list):
    finalY=[]
    for i in range(len(list)):
        y=a*list[i]+b
        finalY.append(y)
    return finalY

def getResidualValue(model, y):
    sum = 0
    for i in range(len(model)):
        sum += (y[i]-model[i])**2
    return sum 


def findROLS(x, y): # finds the r value of an OLSReression model given inputs x and y
    a, b = buildOLSRegressionModel(x,y)
    deviation=getDistanceSumX(y)**2
    modelY=buildWithModel(a,b,x)
    residualValue=getResidualValue(modelY, y)**2 
    R=((deviation-residualValue)/deviation)**0.5 
    return R, R**2

#model1 = buildOLSRegression()

# data=prepareFinalByStock('HistoricalQuotes (2).csv')
# x1,y1=preparePriceAndDate(data)
# print('R values,' ,findR(x1, y1))
# print(buildOLSRegressionModel(x1,y1))


#jank mL and multivariable linear regression
#picked variables should have no correlation between the two ideally as indepedent as possible 
#using estimated multiple regression equation with numpy matrix alegbra


# print(data[1][1:])

# def prepareXForMatrix(data):
#     x=[]
#     for i in range(len(data)):
#         line=[1]
#         for i2 in range(1,len(data[i])): #loops through the tuple of final Data
#             line.append(data[i][i2])
#         x.append(line)
#     return x

# def prepareYForMatrix(data):
#     y=[]
#     for i in range(len(data)):
#         y.append(data[i][0])
#     return y


# x=prepareXForMatrix(data)
# y=prepareYForMatrix(data)


# def OLSregressionMatrix(x,y): #takes a list of x coords and y coords
#     newX=[]
#     for i in range(len(x)):
#         newX.append([1,x[i]])
#     newX=np.matrix(newX)
#     xTx=np.transpose(newX)*newX
#     newY=[]
#     for i in range(len(y)): newY.append([y[i]])
#     newY=np.matrix(newY)
#     xTy=np.transpose(newX)*newY
#     invXtX=np.linalg.inv(xTx)
#     b=invXtX*xTy
#     return f'y={b.item(0)} + {b.item(1)}x'

# print(OLSregressionMatrix([4,4.5,5.0,5.5,6.0,6.5,7.0],[33,42,45,51,53,61,62]))



def fromSpikesToNews(priceList , xLabels, news): #puts together spikes, xlabels, and news     



# b=polynomialRegression([1,2,3,4,5],[2,5,3,2,1],10)
# x=prepareRegressionXPointsForGraph([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0], 10)
# matrixX=primeXforPolynomial(x, 10)
# #print(matrixX)
# predY=buildPredictionY(matrixX, b) 
# print(x)
# print(invBuildYMatrix(predY))



def findSpikes(priceList, step=4): #finds all spike points spike points are dependent on the price list
                           # a change of at least 15% over the span of step days. returns the index 
                           # position of where the price spike was found the most recent 4 day one 
                           # returns a list of tuples of index position and positive or negative (1, positive)
    totalIndex=len(priceList)
    spikeIndexes=[]
    if totalIndex<step: #adjusting the range to find spikes   
        step=totalIndex
    i=step
    while i < totalIndex: 
        i2=0
        toSearchOver=priceList[i-step:i+1]
        basePrice=toSearchOver[0]
        while i2 < len(toSearchOver):
            DyDt=(toSearchOver[i2]-basePrice) # change within the 5 days
            percentChange=DyDt/basePrice
            sentiment='Positive'
            if percentChange<0:
                sentiment='Negative'
            percentChange=abs(percentChange)
            indexPos=i-len(toSearchOver)+i2
            
            #print(percentChange)
            if percentChange>=0.15 and (indexPos,sentiment) not in spikeIndexes:
                print(priceList[indexPos])
                spikeIndexes.append((indexPos,sentiment))  
            i2+=1
        if i==totalIndex-1 and len(toSearchOver)>=2: #looks at the remaining few to make sure we don't miss anything
            for i3 in range(1,len(toSearchOver)):
                DyDt=(toSearchOver[i3]-toSearchOver[i3-1]) 
                percentChange=DyDt/toSearchOver[i3-1]
                print('percent', toSearchOver[i3], percentChange)
                sentiment='Positive'
                if percentChange<0:
                    sentiment='Negative'
                percentChange=abs(percentChange)
                indexPos=i-len(toSearchOver)+i3
                if percentChange>=0.15 and (indexPos,sentiment) not in spikeIndexes:
                    spikeIndexes.append((indexPos,sentiment))  
            i2+=1
        i+=1
    return spikeIndexes



def filterNews(news): #takes dictionary date:list of news and filters out news sources to one each day
                      #directly in the name, and key words, numof stocks affected 
                      #and returns the best news of that date so it filters news for a date
    final={}

    for date in news: #listOfNews is a date
        itemsInNews=news[date]
        highestScore=-100
        bestNews=None
        for i in range(len(itemsInNews)):
            stockInfo=itemsInNews[i]
            score=0
            source=stockInfo['source_name']
            score+=NewsSiteScores[source]*2
            title=stockInfo['title']
            text=stockInfo['text']
            numOfStocksAffected=len(stockInfo['tickers'])
            score+=int(math.ceil(1/numOfStocksAffected*8))#makes it so that the less amount of stocks affected
                                                    #the higher the score
            titleList=title.split(' ')
            for word in titleList:
                word=word.lower()
                wordScore=KeyWords.get(word, 0)
                score+=wordScore
            score-=math.ceil(len(titleList)/8)#helps reduce score since longer texts have an advantage
            for word2 in text:
                word2=word2.lower()
                word2Score=KeyWords.get(word2, 0)
                score+=word2Score
            score-=math.ceil(len(text)/10)
            date1=stockInfo['date']
            if score>highestScore:
                bestNews=stockInfo
                highestScore=score
            
        final[date]=bestNews
    return final


#spikes
def parseThroughNews(news, spikes): #spikes is a tuple of a list of dates from a trend 
                                    #and compiles all news in those dates for that trend
                                    #spikes was already primed by turnSpikedates
    data=news['data'] #news is a dictionary that maps data to a list of dictionaries
    finalNews={} #dictionary of all news on the right dates, we parse through these later
    toParseThrough={}
    print('spikes', spikes)
    for i in range(len(spikes)):
        dates=spikes[i][0]
        sentiment=spikes[i][1]
        for i2 in range(len(dates)): # gets to our dates
            #print('data', data[i])
            currentDate=dates[i2][0]
            indexPos=dates[i2][1]
            toParseThrough[currentDate]=sentiment, indexPos
        for i3 in range(len(data)): #now we parse through the list of news articles 
                unFormatedDate=data[i3]['date']
                listOfDateString=unFormatedDate.split(',')
                actualDate=listOfDateString[1] # cuts out the weekday 
                actualDate=actualDate.split(' ')
                finalDate=actualDate[1]+' '+actualDate[2]+' '+actualDate[3]
                spikeDate=toParseThrough.get(finalDate, None)
                if spikeDate!=None:
                    indexInSpike=spikeDate[1]
                    sentiment=spikeDate[0]
                
                    if sentiment==data[i3]['sentiment']: #if same sentiment 
                        if finalNews.get(finalDate, None)!=None: #sets the dictionary for same date news
                            finalNews[finalDate].append(data[i3])
                        else:
                            finalNews[finalDate]=[data[i3]]                
    return finalNews #final is a dictionary that maps a date to a list of dictionaries 
                     # of news articles
'''