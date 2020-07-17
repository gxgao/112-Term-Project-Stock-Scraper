import os
from cmu_112_graphics import *  
import pickle 
import math
import termProject
import Mlmodel
import PIL 
from tkinter import *
import random
from datetime import datetime,timedelta, date
from yahoo_fin import stock_info as si
import pMVP
from PIL import Image

class portfolio(object): #this is for future if we want to have access to multiple 
    def __init__(self):   #portfolios 
        self.stocks=[]
    
    def addStock(self, fileName):#adds a stock (csv file) this is for back tracking
                                 #and easily accessing past stocks seen 
        self.stocks.append(fileName)

class industryCap(object): #this keeps all the industry stuff together 
    def __init__(self, industry, cap):
        self.industry=industry 
        self.cap=cap
        self.dictionary=None
        self.averages=None
        self.stockList=None

    def __repr__(self):
        return (self.industry+self.cap)

class newsItem(object):
    def __init__(self, url, title, text, source, date, sentiment, tickers, image, xCoord, yCoord, r):
        self.url=url
        self.title=title
        self.text=text
        self.source=source
        self.date=date
        self.sentiment=sentiment
        self.tickers=tickers
        self.image_url=image
        self.xCoord=xCoord
        self.yCoord=yCoord
        self.radius=r
        
    def __repr__(self):
        return str(self.date)+' '+ str(self.xCoord)+' '+str(self.yCoord)
    
#Code from https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html 
def almostEqual(d1, d2, epsilon=10**-6):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)


class graph(object): #graph object will store scale, function to prime the graph based on width and height of a canvas
    def __init__(self,name,xlist, yList, width, height, margin, xLabels, ticker):
        self.name=name
        self.xList=xlist #contains the actual values
        self.yList=yList
        self.width=width 
        self.height=height
        self.grid=[] # 2d array for the grid of the graph stores center cords of each 'cell'
        self.margin=margin # margin for axes
        self.marginX=None
        self.marginY=None
        self.xStep=None #pixel counting for interval steps
        self.yStep=None
        self.xTicks=None #actual x points on the x axis 
        self.yTicks=None # actualy y points on the y axis 
        self.graphWidth=None
        self.graphHeight=None
        self.zeroed=False #zeroes the y axis
        self.yInterval=None
        self.yLength=None
        #self.marginY=50
        self.shiftUp=None
        self.regressionEquation=''
        self.regressionYCoords=None
        self.regressionY=None
        self.xLength=None #differenct from graph Length and heigh this is the raw length 
        self.polynomialX=None
        self.polynomialY=None
        self.newXStep=None #recalibrated x step 
        self.newYStep=None
        self.xLabels=xLabels
        self.yLabels=None
        self.finalXLabels=None
        self.news=None#listof all news in the date range 
        self.multiR=None
        self.poynomialEquation=''
        self.ticker=ticker
        self.formatedXLabels=[]#this holds cleaned xLabels for labelling on graph

    def __eq__(self, other):
        if not isinstance(other, graph):
            return False
        elif self.name==other.name and self.yList==other.yList:
            return True
        
                        
    def makeGridLarge(self): #Same code as makeGrid but modified so Large amounts of data look Ok 
        percentOfCanvas=0.05
        marginX=self.width*percentOfCanvas 
        marginY=self.height*percentOfCanvas
        xLength=self.width-2*marginX
        yLength=self.height-2*marginY
        self.xMargin=marginX
        self.yMargin=marginY
        self.yLength=yLength
        self.xLength=xLength
        maxNumOfBoxesY=100 #creates max num of boxes in y direction 
        xStep=xLength/(max(self.xList)-min(self.xList)) 
        yRange=max(self.yList)-min(self.yList)
        lower=min(maxNumOfBoxesY, yRange, len(self.yList))
        boxYTicks=(yRange/lower) #rounds up What each box is in data no pixel count
        self.yInterval=boxYTicks
        #print('lower', lower)
        yStep=yLength/lower 
        self.xStep=xStep
        self.yStep=yStep
        y=marginY
        yI=0
        while yI<len(self.yList):
            x=marginX
            coords=[]
            xI=0
            y=marginY+yStep*(yI+1) #since bottom right corner, so technically +1
            while xI<len(self.xList)-1:
                xI+=1
                x=marginX+xStep*xI
                coords.append((x,y)) #gives tuple of x and y
            self.grid.append(coords)
            yI+=1
        #print(self.grid, yStep) 
        self.graphWidth=self.grid[0][len(self.grid[0])-1][0]-(self.grid[0][0][0]-self.xStep) #last xCord-first xCord
        self.graphHeight=self.grid[len(self.grid[0])-1][0][1]-(self.grid[0][0][1]-self.yStep) #last y cord - first y cord
        
    def addLabelCoords(self): #prepares coords for where the y's and x's should be
        xLabelBase=self.grid[-1][0][1] # bottom y
        yLabelBase=self.grid[0][0][0]-self.xStep
        xLabelBase=(xLabelBase)#+self.height)/2#between margin now 
        yLabelBase= yLabelBase/2
        finalXStep=0 # finds optimal xstep so we don't have to label every coord
        finalYStep=0
        countX=0 #keeps track of how many boxes we are up by
        countY=0
        while finalXStep<80:
            finalXStep+=self.xStep
            countX+=1
        while finalYStep<80:
            finalYStep+=self.yStep
            countY+=1
        finalXCoords=[self.grid[0][0][0]-self.xStep]
        finalYCoords=[self.grid[-1][0][1]]
        finalXCounts=[]
        finalYCounts=[]
        countStepX=countX
        countStepY=countY 
        finalXLabels=[self.formatedXLabels[0]]
        numYBoxes=len(self.grid)+1
        rangeY=max(self.yList)-min(self.yList)
        priceStep=rangeY/numYBoxes
        yLabels=[]
        yLabels.append(min(self.yList))
        while countX < len(self.grid[0]): #this is just making sure all labels are where they should be
            finalXCoords.append(self.grid[0][countX][0])
            finalXLabels.append(self.formatedXLabels[countX])
            countX+=countStepX
        while countY < len(self.grid):
            finalYCoords.append(self.grid[-countY][0][1])
            yLabels.append(Mlmodel.roundToNearestCent(min(self.yList)+priceStep*countY))
            countY+=countStepY
        return finalXCoords, finalYCoords, finalXLabels, yLabels, xLabelBase, yLabelBase

    def addTitle(self):
        xCord=self.width/2
        yCord=self.grid[0][0][1]/2
        fontSize=int(self.width/50)
        return xCord, yCord, fontSize


    def makeGridSmall(self):
        percentOfCanvas=0.05
        marginX=self.width*percentOfCanvas 
        marginY=self.height*percentOfCanvas
        xLength=self.width-2*marginX
        yLength=self.height-2*marginY
        self.yLength=yLength
        self.xLength=xLength
        self.yMargin=marginY
        xStep=xLength/(max(self.xList)-min(self.xList)) #len(self.xList)
        maxNumOfBoxes=50
        yStep=yLength/maxNumOfBoxes # this is maximum number of boxes we're going to work with
        self.xStep=xStep
        self.yStep=yStep
        y=yStep+marginY
        yI=0
        while yI<maxNumOfBoxes:
            x=marginX+xStep
            coords=[]
            xI=0
            while xI<len(self.xList)-1:
                x=marginX+xStep+xStep*xI
                coords.append((x,y)) #gives tuple of x and y
                xI+=1
            self.grid.append(coords)
            yI+=1
            y=marginY+yStep*yI

        self.graphWidth=self.grid[0][len(self.grid[0])-1][0]-(self.grid[0][0][0]-self.xStep) #last xCord-first xCord
        self.graphHeight=self.grid[len(self.grid[0])-1][0][1]-(self.grid[0][0][1]-self.yStep) #last y cord - first y cord
 

    def preparePoints(self): #canvas.create_line can add as many points as you want  
                            # L = list 
                            #canvas.create_line(*L) star argument also known as this
                            #unpacks the list 
        x=self.xList    
        y=self.yList
        marginForAxis=0.1
        minY = (self.grid[0][0][1]-self.yStep) #min Y coord
        maxY = self.graphHeight+minY           #max Y coord
        yIntervals=(maxY-minY)/(len(self.grid)-1)  
        xCords=[]
        yCords=[]
        baseX=self.grid[0][0][0]-self.xStep #leftmost x coord 
        xLabelIntervals=(max(x)-min(x))/(len(x)-1) #uniform x Steps
        baseY=self.grid[-1][0][1] #bottom most y coord 
        for i in range(len(x)):
            xGridCoord=self.grid[0][i-1][0]
            calcX=baseX+(x[i]/(len(x)-1)*self.graphWidth)-self.xStep
            if i!=0 and almostEqual(calcX, xGridCoord): #this snaps the x coord to the correct column 
                currX=xGridCoord 
                xCords.append(currX)
            else: #this accounts for non interval step like fractions (3.4 or 2.98)
                currX=calcX
                xCords.append(currX)
            currY=0
            #yGridCord= self.grid[-1][0][1] #actual grid coord
            calcY=baseY-(y[i]-min(y))/(max(y)-min(y))*self.yLength #baseY-(y[i]-min(y))/max(y)*(maxY-minY) #calculated Y based on formula
            currY=calcY #subtract cuz coord Y increases downwards
            yCords.append(currY) 
        self.xTicks=xCords #grid coords are based on bottom right corner
        self.yTicks=yCords
        self.cutTop(yCords)

    def preparePointsSmall(self): #different base formula used for smaller lists and testing 
                                  #sets a differnet number of boxes, maybe later integrate into one
                                  #function with make Gird large though the other preparepointssmall
                                  #has a different formula base don this function
        x=self.xList    
        y=self.yList
        marginForAxis=0.1
        minY = (self.grid[0][0][1]-self.yStep) #min Y coord
        maxY = self.graphHeight+minY           #max Y coord
        yIntervals=(maxY-minY)/(len(self.grid)-1)  
        xCords=[]
        yCords=[]
        baseX=self.grid[0][0][0]-self.xStep #leftmost x coord 
        xLabelIntervals=(max(x)-min(x))/(len(x)-1) #uniform x Steps
        baseY=self.grid[-1][0][1] #bottom most y coord 
        for i in range(len(x)):
            xGridCoord=self.grid[0][i-1][0]
            calcX=baseX+(x[i]/(len(x)-1)*self.graphWidth)-self.xStep
            if i!=0 and almostEqual(calcX, xGridCoord): #this snaps the x coord to the correct column 
                currX=xGridCoord 
                xCords.append(currX)
            else: #this accounts for non interval step like fractions (3.4 or 2.98)
                currX=calcX
                xCords.append(currX)
            currY=0
            yGridCord= self.grid[len(self.grid)-i-1][0][1] #actual grid coord
            fractionOfGraph=(y[i]-min(y))/(max(y)-min(y))

            calcY=baseY-fractionOfGraph*(self.yLength)#maxY-minY) #calculated Y based on formula
            currY=calcY #subtract cuz coord Y increases downwards
            yCords.append(currY) 
        self.xTicks=xCords #grid coords are based on bottom right corner
        self.yTicks=yCords
        #self.cutTop(yCords)

    def cutTop(self, yCords):       
        gridCopy=[]
        minYCord=min(yCords)
        maxYCord=max(yCords)
        index=len(self.grid)-1
        epsilon=1*10**-1
    
        while index>=0 and self.grid[index][0][1]>=minYCord: #this cleans unused Y's 
            if not almostEqual(self.grid[index][0][1], minYCord):
                gridCopy.append(self.grid[index])
            index-=1
        self.grid=gridCopy[-1::-1]
        shiftUp=self.grid[0][0][1]-self.yMargin #shift up to reorient

        for i in range(len(self.grid)):
            for i2 in range(len(self.grid[i])):
                self.grid[i][i2]=(self.grid[i][i2][0],self.grid[i][i2][1]-shiftUp) #creates new tuple with updated shift up coord
        for y in range(len(self.yTicks)):
            self.yTicks[y]-=shiftUp
        self.yLength = self.grid[-1][0][1]-self.grid[0][0][1]

    def addRegression(self):
        x1=self.xList
        y1=self.yList
        b=Mlmodel.multivariateRegression([x1],y1) #can be used for linear regression 
        matrixX=Mlmodel.buildXMatrix([x1])
        predY=Mlmodel.buildPredictionY(matrixX,b)
        R=Mlmodel.findRForMulti(predY, y1)    
        predY=Mlmodel.invBuildYMatrix(predY)
        self.regressionY=predY
        self.regressionEquation=Mlmodel.turnToEquation(b, ['x'])  #swap x1 to labels later
        self.regressionEquation+=f' R^2 = {R}'

    def addRegressionCoords(self):
        x=self.xTicks
        y=self.regressionY
        yCords=[]
        baseY=self.grid[-1][0][1] #bottom most y coord 
        maxYV=max(self.yList) #min and max Values of Y calculated once to save computing 
        minYV=min(self.yList) #these values are used for scalling steps

        for i in range(len(y)):
            calcY=baseY-(y[i]-minYV)/((maxYV-minYV))*self.yLength#-self.yStep
            yCords.append(calcY)                                     #first and last y                     
        self.regressionYCoords=yCords

    
    def makeCoords(self, x, y): #takes values and returns coords of them on the grid bug fix needed! 
        finalXCoords=[]
        finalYCoords=[]
        baseY=self.grid[-1][0][1] #bottom most y coord 
        maxYV=max(self.yList) #min and max Values of Y calculated once to save computing 
        minYV=min(self.yList) #these values are used for scaling steps
        baseX=self.grid[0][0][0]-self.xStep
        minXV=(min(self.xList))
        maxXV=(max(self.xList))
        for i in range(0,len(x)): #x and y should have same length 
            calcY=baseY-(y[i]-minYV)/(maxYV-minYV)*self.yLength
            calcX=baseX+(x[i]-minXV)/(maxXV-minXV)*self.xLength
            finalXCoords.append(calcX)
            finalYCoords.append(calcY)
        # print('Regression', finalYCoords)
        return finalXCoords, finalYCoords

    def addPolynomialRegression(self, n, interval): # n is the degree
    
        b=Mlmodel.polynomialRegression(self.xList, self.yList, n)
        self.polynomialEquation=Mlmodel.makeRegressionEquation(b)
        finalXPoints=Mlmodel.prepareRegressionXPointsForGraph(self.xList, interval) #slices x into intervals
        matrixX=Mlmodel.primeXforPolynomial(finalXPoints, n) #builds matrix X to be used for predicting
        predY=Mlmodel.buildPredictionY(matrixX, b) # builds prediction 
        findRX=Mlmodel.primeXforPolynomial(self.xList, n) #used for finding R value
        findRY=Mlmodel.buildPredictionY(findRX, b) #used for finding R value, is a built matrix
        R=Mlmodel.findRForMulti(findRY, self.yList)
        finalY=Mlmodel.invBuildYMatrix(predY) #gets us back the predicted Y in a list
        self.polynomialY=finalY
        self.polynomialX=finalXPoints 
        self.multiR=R

    def addPolynomialRegression(self, n, interval): # n is the degree This is an adaptive function
                                                    #finds best polynomial within the given degree
        i=2
        bestR=0
        while i<=n: #we are going to keep looping until we find the best R value depending on 
                    #the degree (incase there is a better value at a different degree)
            b=Mlmodel.polynomialRegression(self.xList, self.yList, i)
            self.polynomialEquation=Mlmodel.makeRegressionEquation(b)
            finalXPoints=Mlmodel.prepareRegressionXPointsForGraph(self.xList, interval) #slices x into intervals
            matrixX=Mlmodel.primeXforPolynomial(finalXPoints, i) #builds matrix X to be used for predicting
            predY=Mlmodel.buildPredictionY(matrixX, b) # builds prediction 
            findRX=Mlmodel.primeXforPolynomial(self.xList, i) #used for finding R value
            findRY=Mlmodel.buildPredictionY(findRX, b) #used for finding R value, is a built matrix
            R=Mlmodel.findRForMulti(findRY, self.yList)
            finalY=Mlmodel.invBuildYMatrix(predY) #gets us back the predicted Y in a list
            if 1>=R>=bestR:
                bestR=R
                self.polynomialY=finalY
                self.polynomialX=finalXPoints 
                self.multiR=R
            i+=1
            
        
    def addNews(self): #prepares News Coords preps x and y coords
        listOfNewsItems=[]
        news=Mlmodel.finalFindSpikesAndNews(self.ticker, self.yList, self.xLabels)
        for i in range(len(news)):
            index=news[i][0] #index position of news in the tuple
            data=news[i][1]
            for date in data:
                newsRadius=self.width//190
                newsItems=data[date]
                url=newsItems['news_url']
                title=newsItems['title']
                image=newsItems['image_url']
                text=newsItems['text']
                source=newsItems['source_name']
                date=newsItems['date']
                sentiment=newsItems['sentiment']
                tickers=newsItems['tickers']
                xCoord=self.xTicks[index+1] #plus one is to account for left shift since XTicks is +1 longer
                yCoord=self.yTicks[index+1] #due to how the grid is formated
                if yCoord<self.grid[0][0][1]-self.yStep and index+1>1 and index+2<len(self.xTicks):
                    yCoord=(abs(self.yTicks[index+2]+self.yTicks[index]))/2
                newsInfo=newsItem(url, title, text, source, date, sentiment, tickers, image, xCoord, yCoord, newsRadius)
                listOfNewsItems.append(newsInfo)

        self.news=listOfNewsItems #we have a list of news items now with thier proper coords



def appStarted(app):
    app.cap='Press spacebar to enter'
    app.industry='Press p to enter'
    app.timeHorizon='Press t to enter'
    app.initState=True
    # app.results=pickle.load(open('data.pickle', 'rb'))
    # f=open('test.txt', 'rt')
    app.results=None #eval(f.read()) 
    app.graph=None 
    app.displayState=False
    app.rows=None
    app.cols=None
    app.xStep=None
    app.yStep=None
    app.fontSize=8
    app.ticker='Press Space to Enter!'
    app.timeHorizon='Press t to Enter!'
    app.singleStockAnalysis=False
    app.industryAnalysis=False
    app.singleResults=None
    app.displayStateSingle=False
    app.graphState=False
    app.inputStateSingle=False
    app.showRegression=False
    app.showSpikes=False
    app.showNews=False 
    app.showedNews=0 #index position of which news to show
    app.images=[]
    with open("popularTickers1.pickle", "rb") as picky: 
        popularTickers = pickle.load(picky)

    app.popularTickers=popularTickers #this is used for aesthetics 
    app.scrollCords=[]
    app.scrollingTickers=[]
    app.timerDelay=10
    app.scrollGap=0 #used to calculate the scroll coords
    prepScroll(app, app.height-app.height/6)
    app.showEstimate=False #this is the screen where the user sees the estimate they put in
    app.userEstimate=None
    app.faangPrices=[('FB', None), ('AMZN',None),
                     ('AAPL',None), ('NFLX',None), 
                    ('GOOG',None)]
    initializeFanngPrices(app)
    app.timeCount=0 
    app.faangCounter=0 #this is used to update faang prices 
    app.fundamentals={} #dicitionary of fundamental values
    app.showFundamentals=False 
    app.fangImage = app.loadImage('fang1.png')  #source: drew these myself
    app.fangImage = app.scaleImage(app.fangImage, 1/2)
    app.fangImage2 = app.fangImage.transpose(Image.FLIP_LEFT_RIGHT)
    
    app.portfolio=[]
    app.justLeft=False
    app.portfolioX, app.portfolioY=0, 0
    app.portfolioMargin=0
    app.portfolioState=False
    app.portfolioIndex=0
    app.portfolioShowLength=8 #max number of things we want to display at once
    app.industries=[]
    app.industryIndex=0 #this keeps track of what industry we are looking at (for history and
                        #back tracking)
    app.stockListIndex=0 #this allows us to index through specific stocks to analyze in 
                         #industry analysis
    prepIndustryAnalysis(app, 'Large_Drug Stores.pickle')
    prepIndustryAnalysis(app, 'Mid_Gold.pickle')
    #prepIndustryAnalysis(app, 'small _food wholesale.pickle')
    app.displayStockInd=False #this diplays the stock in comparison to the Industry
    app.errorState=False #enters if we webdriver failed
    app.industryInputState=False 
    
   
    
def initializeFanngPrices(app): #sets initial faang prices does not crash with no internet
    for i in range(len(app.faangPrices)):
        ticker=app.faangPrices[i][0]
        price=None
        try:   #this allows us to not crash on no internet state or if yahoo finance has a problem
            price=si.get_live_price(ticker.lower())
        except:
            pass
        app.faangPrices[i]=(ticker, price)

        
def mousePressed(app, event): #clicking events
    if app.initState==True:
        if event.x>app.width/2:
            app.initState=False
            app.singleStockAnalysis=True
            app.inputStateSingle=True
        if event.x<app.width/2:
            app.initState=False
            app.industryAnalysis=True
            app.displayState=False
            app.industryInputState=True
    if app.displayStateSingle: #this is when the portfolio button is displayed:
        if (event.x>app.portfolioX-app.portfolioMargin and event.x<app.portfolioX+app.portfolioMargin
            and event.x>app.portfolioY-app.portfolioMargin/2 and event.x<app.portfolioY+app.portfolioMargin/2):
            app.portfolioState=True

    if app.graphState==True: #interact with the news Dots here
        # if app.graph!=None:
        if app.graph.news!=None:
            for i in range(len(app.graph.news)):
                r=app.graph.news[i].radius
                x=app.graph.news[i].xCoord
                y=app.graph.news[i].yCoord
                if event.x >= x-r and event.x<=x+r and event.y>=y-r and event.y<=y+r: #if you clikc onto the #the news dot 
          
                    app.showedNews=i #set's the index position of which news card we want to see
            
                    app.showNews=True
            
              
        
                        
def keyPressed(app, event):
    if app.industryAnalysis: #controls for industry analysis
        if app.industryInputState and event.key=='Space':
            app.cap=app.getUserInput('What is the Market Cap?')
            app.initState=False
        if app.industryInputState and event.key=='p':
            app.industry=app.getUserInput('What is the Industry')
            app.initState=False
        if not app.displayState and event.key=='Enter':
            if (app.cap!='Press spacebar to enter' 
                and app.industry!='Press p to enter'):
                try:
                    termProject.searchForStocks(app.cap, app.industry) #get's dictionary for entered inputs and historic prices dictionary
                except:
                    pass
                try:
                    fileName=f"{app.cap}_{app.industry}.pickle"
                    prepIndustryAnalysis(app, fileName)
                except:
                    app.errorState=True
        if event.key=='d':
            app.displayState=not app.displayState
            app.industryInputState=False
            
        if app.displayState: #we use arrows to navigate here 
            industry=app.industries[app.industryIndex] #sets the industry we're on
            if event.key=='Down':
                app.stockListIndex=moveIndex(app, 1, app.stockListIndex, len(industry.stockList)+1) 
            elif event.key=='Up': #+1 is to account for the averages tab
                app.stockListIndex=moveIndex(app, -1, app.stockListIndex, len(industry.stockList)+1)
            elif event.key =='Right':
                app.industryIndex=moveIndex(app, 1, app.industryIndex, len(app.industries))
                industry=app.industries[app.industryIndex]
                app.stockListIndex=moveIndex(app, 0, app.stockListIndex, len(industry.stockList)+1) #this prevents out of bounds
            elif event.key=='Left':
                app.industryIndex=moveIndex(app, -1, app.industryIndex, len(app.industries))
                industry=app.industries[app.industryIndex]
                app.stockListIndex=moveIndex(app, 0, app.stockListIndex, len(industry.stockList)+1)
                 #this is to prevent                                                                                         #out of bounds
            elif event.key=='Enter':
                app.displayStockInd=not app.displayStockInd
            
    
    else: #controls for single stock analysis
        if event.key=='t':
            app.timeHorizon=app.getUserInput('What is the Time Horizon? [1M], [6M]') #add YTD later
            app.initState=False
            app.inputStateSingle=False
            app.displayStateSingle=True
            
        if event.key=='Space':
            app.ticker=app.getUserInput('What is the ticker?')
            app.initState=False
            app.inputStateSingle=False
            app.displayStateSingle=True
            preparePortfolioButton(app)
        if not app.portfolioState and event.key=='Enter':
            if (app.timeHorizon!='Press t to Enter!' and app.timeHorizon!=None
                and app.ticker!='Press Space to Enter!' and app.ticker!=None):
                app.inputStateSingle=False
                app.displayStateSingle=True
                try:
                    termProject.getHistoricalPrices(app.ticker, app.timeHorizon) #creates Csv for stock and returns true when done
                    fileName=f'{app.ticker}{app.timeHorizon}.csv'
                    prepGraph(app, fileName) #this is the actual code that needs to be run   
                except:
                    app.errorState=True      
        if event.key=='d': #builds results
            #app.drawInputStateSingle=not app.inputStateSingle
            #app.displayStateSingle=not app.displayStateSingle
            #prepGraph(app, 'AMZN6M.csv') #this is for quick testing
            app.graphState=not app.graphState
        if app.graphState==True:
            if event.key=='p':
                app.showRegression=not app.showRegression 
            if event.key=='s':
                app.showFundamentals=not app.showFundamentals
        if app.showRegression:
            if event.key=='g':
                app.userEstimate=app.getUserInput('How many days out do we want to estimate?')
                if app.userEstimate!=None and app.userEstimate.isdigit():
                    app.showEstimate=True
                # try:
                #     app.userEstimate=app.getUserInput('Please Enter a Number')
                # except:
                #     app.showRegression=False
        if app.showEstimate:
            if event.key=='q':
                app.showEstimate=False  
        if (app.graphState==True and event.key=='Escape' and app.showNews==False 
            and app.showFundamentals==False and app.justLeft==False): #escape is default leave we need the ands so we don't
                                              #accidently jump depths
            app.graphState=not app.graphState
        if app.showNews and event.key=='Escape':
            app.showNews=False
            app.justLeft=True #keeps track of whether we just left something or not so escape can
                              #leave the right state
        if app.showFundamentals and event.key=='Escape':
            app.showFundamentals=not app.showFundamentals
            app.justLeft=True
        if app.portfolioState:
            if event.key=='Down':
                app.portfolioIndex=moveIndex(app, 1, app.portfolioIndex, app.portfolioShowLength) #direc
            if event.key=='Up':
                app.portfolioIndex=moveIndex(app, -1, app.portfolioIndex, app.portfolioShowLength)
            if event.key=='Enter':
                try:                         #this is to null everything and make sure we're not 
                    app.showEstimate=False  #leaving behind states when we enter a new graph
                    app.showNews=False
                    app.showFundamentals=False
                    app.showRegression=False
                    app.graph=app.portfolio[app.portfolioIndex]
                    app.graphState=True
                except: #incase there is not a graph there 
                    pass
            if event.key=='Escape':
                app.portfolioState=False
    if event.key=='r':
        setAllStatesFalse(app)
        app.initState=True
        
def setAllStatesFalse(app): #resets everything for when we press R
    app.displayState=False
    app.graphState=False
    app.portfolioState=False
    app.showRegression=False
    app.showNews=False
    app.showFundamentals=False
    app.displayStateSingle=False
    app.displayState=False
    app.displayStockInd=False
    app.displayInputSingle=False
    app.singleStockAnalysis=False
    app.industryAnalysis=False
    app.errorState=False
    app.industryInputState=False
    


def prepIndustryAnalysis(app, fileName):
    with open (fileName, 'rb') as picky:#this is for quick testing
        results=pickle.load(picky)
    name=fileName.split('.')[0] #splits into name and .pickle
    name=name.split('_')
    cap=name[0]
    industry=' '+name[1]
    newIndustry=industryCap(cap, industry)
    newIndustry.dictionary=results #this is the original pickle dictionary that we will anlyze #maybe make results just an industry
                    #object? 
    parsedInd, stockList=pMVP.industryAnalysis(results) #this parses the industry and cleans things and
                                                    #begins building the averages
    newIndustry.averages=pMVP.averageIndustry(parsedInd)
    newIndustry.stockList=stockList
    app.industries.append(newIndustry) #stores it into a list of industry objects
   
    

def moveIndex(app, increment, index, max): # this just makes sure we don't leave bounds
    currentIndex=index
    currentIndex+=increment
    if currentIndex>=max:
        currentIndex=max-1
    if currentIndex<0:
        currentIndex=0
    return currentIndex


def prepFundamentals(app): #this initializes the dictionary of fundamentals needs
                            #to be at the beginning to avoid recalling it in the redraw all funciton
    ticker=app.ticker
    try:
        table=si.get_quote_table(ticker) #dictionary of funamental values
        app.fundamentals=table
    except:
        ticker=app.graph.name.split('.') #this is for when we can't find it through yahoo finance
        ticker=ticker[0][:-2]
        table=si.get_quote_table(ticker)
        app.fundamentals={app.ticker:None, '1y Target Est': 'None'}

def timerFired(app): 
    for i in range(len(app.scrollCords)):
        app.scrollCords[i][0]+=3 #moves x coord by 10
        if app.scrollCords[i][0]>=app.width:
            app.scrollCords[i][0]=app.scrollCords[i-1][0]-app.scrollGap
    app.timeCount+=1
    if app.timeCount%1000==0:
        app.timeCount=0
        prepFaangPrices(app, app.faangCounter)
        app.faangCounter+=1
        if app.faangCounter==len(app.faangPrices): #if it reaches the end we reset back to 0
            app.faangCounter=0

    if app.justLeft:
        if app.timeCount%100==0:
            app.justLeft=False

def prepFaangPrices(app, i): #prepare the faang prices to display
    tickers=app.faangPrices #tickers is a dictionary
    name=tickers[i][0]
    price=pMVP.getLivePrice(tickers[i][0])
    app.faangPrices[i]=(name,price)  


def prepGraph(app, fileName): #prepares the graph by priming coords and getting images for news
    data, xLabels=Mlmodel.prepareFinalByStock(fileName)
    x1,y1=Mlmodel.preparePriceAndDate(data)
    graph1=graph(fileName,x1,y1,app.width,app.height, 10, xLabels, app.ticker)
    graph1.formatedXLabels=copy.copy(graph1.xLabels)
    if max(y1)-min(y1)>20 or len(graph1.xList)>50:
        graph1.makeGridLarge()
        graph1.preparePoints()
    else:
        graph1.makeGridSmall()
        graph1.preparePointsSmall() # different formula for smaller graphs

    graph1.addNews()
    for i in range(len(graph1.news)): #this is to preload every news image so we can
        newsInfo=graph1.news[i]         #show them when the user clicks on the dots
        newsImage=newsInfo.image_url    #it's a list with corresponding index positions to each
                                        #news Item
        image=app.loadImage(newsImage) # all images are pulled from news source
        image =app.scaleImage(image, 2/3) #source of image will appear on graphics state where they 
                                            #appear in
        app.images.append(image)
    app.graph=graph1
    prepFundamentals(app)
    if app.graph not in app.portfolio:
        app.portfolio.append(app.graph) 

def addScrollPrices(app): #adds prices to tickers stored in popular too slow for rn
    for i in range(len(app.popularTickers)):
        stock=app.popularTickers[i]
        price=si.get_live_price(stock)
        app.popularTickers[i]+=f' {price}'


def prepScroll(app, y): #prepping the initial scroll bar just a cute animation y is the y coord
                        # we want the scrolling on
    tickerList=app.popularTickers
    scroll=[]
    scrollCords=[]
    #adjusts gapwidth by canvas size so at most
    #only a certain percent of tickers will be on canvas
    for i in range(10):
        tickerIndex=random.randint(0,len(tickerList)-1)
        scroll.append(tickerList[tickerIndex])
    gapWidth=app.width/(int(len(scroll)*0.7))
    app.scrollGap=gapWidth
    for i in range(len(scroll)):
        scrollCords.append([0-i*gapWidth,y]) #
    app.scrollingTickers=scroll
    app.scrollCords=scrollCords
    #addScrollPrices(app)


def drawPortfolioDisplay(app, canvas): #display portfolio / past things we've looked at
    shownStocks=app.portfolio
    #this screen always shows a maximum of 8 stocks before we start scrolling
    canvas.create_rectangle(0,0, app.width, app.height, fill='gray20')
    i=0
    margin=30
    maxNumOfItems=8
    app.portfolioShowLength=maxNumOfItems
    gap=(app.height-2*margin)/maxNumOfItems
    fontSize=app.width//80
    
    while i < maxNumOfItems: 
        fill='green3'
        font=f'coureir {fontSize}'
        if i==app.portfolioIndex:
            font=f'coureir {fontSize+2} bold'
            fill='deep sky blue'
        if i >= len(shownStocks):
            canvas.create_text(app.width/2, gap*(i)+margin,width=app.width-2*margin,
                                font=font, fill=fill, text='None')
        else:
            lastPrice=shownStocks[i].yList[-1]
            canvas.create_text(app.width/2, gap*(i)+margin,width=app.width-2*margin,
                                font=font, fill=fill, 
                                text=f'{shownStocks[i].name} closing price: ${lastPrice}') #its a list of graphs so 
        i+=1                                                                                    #we get the attribute name and last price
                                                                                                #through indexing

                                                                            
def drawScrollingTickers(app, canvas): #draws the scrolling ticker bar
    font=f'coureir 12'
    color='SpringGreen2'
    for i in range(len(app.scrollCords)):
        scrollItem=app.scrollingTickers[i]
        canvas.create_text(app.scrollCords[i][0], app.scrollCords[i][1], text=f'{scrollItem}', font=font, fill=color)


def drawEstimation(app, canvas): #input is the user input to find 
    margin=app.graph.margin
    estimate=Mlmodel.calculateEstimate(float(app.userEstimate), app.graph.regressionEquation, app.graph.xList[-1])
    font=f'Coureir {int(app.width/90+2)} bold'
    fill='Green3'
    estimatePolynomial=Mlmodel.calculateEstimate(float(app.userEstimate), app.graph.polynomialEquation, app.graph.xList[-1])
    
    canvas.create_rectangle(margin, margin, app.width-margin, app.height-margin,
                            fill='gray15')
    canvas.create_text(app.width//2, app.height//2, width=int(app.width-margin*2), #20 is added since it's formated wierly
                        text=f'''Linear Equation: {Mlmodel.formatEquation(app.graph.regressionEquation)}
                                \nBase date:  {app.graph.formatedXLabels[0]}          
                                \nLast date: {app.graph.formatedXLabels[-1]}
                                \nYour input: {app.userEstimate} days after Last Date
                                \nLinear Estimate: ${Mlmodel.roundToNearestCent(estimate)}
                                \nPolynomial Equation: {Mlmodel.formatEquation(app.graph.polynomialEquation)}
                                \nPolynomial R^2: {app.graph.multiR}
                                \nPolynomial Estimate: ${Mlmodel.roundToNearestCent(estimatePolynomial)} (Very Unreliable for Small Date Ranges and far out estimate)
                                \nAnalyst 1Y Price Target (Yahoo Finance): {app.fundamentals['1y Target Est']} '''
                                , font=font, fill=fill)


def drawStockFundamentals(app, canvas): #draw the fundamentals of the stock
    margin=30
    canvas.create_rectangle(margin, margin, app.width-margin, app.height-margin,
                            fill='gray20')
    count=1
    gap=(app.height-2*margin)/(len(app.fundamentals)+1)
    fill='green3'
    for item in app.fundamentals:
        canvas.create_text(app.width/2, gap*count+margin, text=f'{item}: {app.fundamentals[item]}',
                            fill=fill )
        count+=1


def drawFaang(app, canvas, y, color): #draws the fang stocks with prices attached at coordinate y
    font=f'courier {app.width//80}'
    for i in range(len(app.faangPrices)):
        ticker=app.faangPrices[i][0]
        price=None
        if app.faangPrices[i][1]!=None: #if we couldn't retireve the prices we default to none
            price=Mlmodel.roundToNearestCent(app.faangPrices[i][1])
        canvas.create_text(app.width/(len(app.faangPrices)+1)*(i+1), y, width=app.width-20, 
                            text=f'{ticker}: {price}'
                            ,fill=color, font=font)
    
        #{app.faangPrices[i][0]}: {Mlmodel.roundToNearestCent(app.faangPrices[i][1])

def drawInputSingle(app, canvas): #draw the input state single for single stock analysis
    font='Coureir 24 bold'
    color='light sky blue'
    gap=30
   
    canvas.create_rectangle(0,0,app.width, app.height, fill='gray20')
    drawFaang(app, canvas, 50, color)
    canvas.create_image(app.width/2-app.width/3, app.height/2, image=ImageTk.PhotoImage(app.fangImage))
    canvas.create_image(app.width/2+app.width/3, app.height/2, image=ImageTk.PhotoImage(app.fangImage2))
    canvas.create_text(app.width/2, app.height/2-gap, text=f'Single Stock Analysis', font=font, 
                        width=app.width, fill=color)
    canvas.create_text(app.width/2, app.height/2, text=f'Ticker = {app.ticker}', font=font,
                         width=app.width, fill=color)
    canvas.create_text(app.width/2, app.height/2+gap, text=f'TimeHorizon = {app.timeHorizon}'
                        , font=font, width=app.width, fill=color)
    #drawScrollingTickers(app, canvas)
    
        
def drawDisplaySingle(app, canvas): # make graph here 
    fontSize = int(app.width/50)
    font=f'Arial {fontSize} bold'
    color='light sky blue'
    gap=30
    #drawScrollingTickers(app, canvas) #bug fix this is not appearing right now
    canvas.create_rectangle(0,0,app.width, app.height, fill='gray20')
    canvas.create_text(app.width/2, app.height/2-gap, text=f'Single Stock Analysis'
                        , font=font, width=app.width-40, fill=color)
    canvas.create_text(app.width/2, app.height/2, text=f'Ticker = {app.ticker}'
                        , font=font, width=app.width-40, fill=color)
    canvas.create_text(app.width/2, app.height/2+gap, text=f'TimeHorizon = {app.timeHorizon}'
                        , font=font, width=app.width-40, fill=color)
    drawPortfolioButton(app, canvas, color, fontSize)
    if app.graph==None:
        canvas.create_text(app.width/2, app.height/2+gap*2, text=f'Press Enter to build results'
                            , font=font, fill=color)
    else:
        if app.graph.news==None:
            canvas.create_text(app.width/2, app.height/2+gap*2, text=f'Graph is Ready! Fetching News...'
                            , font=font, fill=color)
        else:
            canvas.create_text(app.width/2, app.height/2+gap*2, text=f'Results Ready! Press d to fetch them!'
                            , font= font, fill=color )


def preparePortfolioButton(app): #prepares the portfolio button
    app.portfolioMargin=50
    app.portfolioX=app.width/2
    app.portfolioY=app.height-app.portfolioMargin/2


def drawPortfolioButton(app, canvas, color, fontSize): #draws the blue portfolio button
    margin=app.portfolioMargin
    portfolioFont=f'courier {int(fontSize*4/5)}' # we want the font to be a bit smaller than the display ones
    canvas.create_rectangle(app.portfolioX-app.width/5, app.portfolioY-margin/2, app.portfolioX+app.width/5,
                            app.portfolioY+margin/2, fill=color)
    canvas.create_text(app.portfolioX, app.portfolioY, text='Portfolio',
                     font=portfolioFont, fill='gray20')
 

def drawLabels(app, canvas, graph1):#draws labels at corerct intervals
    finalXCoords, finalYCoords, xLabels, yLabels, xLabelBase, yLabelBase=graph1.addLabelCoords()
    font='Courier 6 bold'
    for i in range(len(finalXCoords)):
        canvas.create_text(finalXCoords[i], xLabelBase, text=xLabels[i], angle=90, font=font, fill='light sky blue')
    for i in range(len(finalYCoords)):
        canvas.create_text(yLabelBase, finalYCoords[i], text=yLabels[i], font=font, fill='light sky blue')

def drawGraph(app, canvas): #draws the actual graph 
    canvas.create_rectangle(0,0,app.width,app.height,fill='gray20')
    graph1=app.graph 
    grid=graph1.grid
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            x,y=grid[r][c]
            #print('XY and ystep', x, y, graph1.yStep)
            canvas.create_rectangle(x-graph1.xStep,y-graph1.yStep,x,y, outline='gray30')
    xTicks=graph1.xTicks
    yTicks=graph1.yTicks
    drawLineChart(app, canvas, xTicks, yTicks)
    drawLabels(app, canvas, graph1)
    drawTitle(app, canvas, graph1, 'green')
    drawNewsDots(app, canvas, graph1)
    if app.showRegression==True:
        graph1.addRegression()
        graph1.addRegressionCoords()
        color='green4'
        if '-' in graph1.regressionEquation.split(' ')[2]: #means theres a negative slope
            color='red3'
        predY=graph1.regressionYCoords
        regressionX=graph1.xTicks 
        drawLineChart(app, canvas, regressionX, predY, color, w=1.5)
        equationXCord=Mlmodel.avgList(regressionX) #finds middle place to put equation
        equationYCord=Mlmodel.avgList(graph1.regressionYCoords)
        drawRegressionEquation(app, canvas, equationXCord, equationYCord, 'Green3')
        graph1.addPolynomialRegression(10, 2)
        pX, pY = graph1.makeCoords(graph1.polynomialX, graph1.polynomialY)
        drawLineChart(app, canvas, pX, pY, color=color, w=1.1)


def drawRegressionEquation(app, canvas, equationXCord, equationYCord, color): #draws the regression equation
    font=f'courier {app.width//100} bold'
    graph1=app.graph
    upShift=graph1.height//7
    string=graph1.regressionEquation
    #toReformat=string.split(' ') #list split by spaces so we can reformat to make look better
    finalString=Mlmodel.formatEquation(string)

    canvas.create_text(equationXCord, equationYCord-upShift, text=finalString, fill=color, font=font )
    canvas.create_text(equationXCord, equationYCord-upShift-50, text=f'Polynomial Regression R = {str(graph1.multiR)[0:4]}',
                        fill=color, font=font)

def drawTitle(app, canvas, graph, color): #draws the graph title
    xCord, yCord, fontSize=graph.addTitle()
    name=graph.name.split('.') #this is to get rid of .csv 
    canvas.create_text(xCord, yCord, text=name[0], font=f'Courir {fontSize} bold', fill=color)
    
def drawLineChart(app, canvas, xTicks, yTicks, color='RoyalBlue1', w=1.1): #draw lines onto grid of graph based on xTicks and Yticks of coords
    lastX=xTicks[0]
    lastY=yTicks[0]
    r=1
    canvas.create_oval(lastX-r,lastY-r, lastX+r,lastY+r)
    grid=app.graph.grid
    baseX=grid[0][0][0]-app.graph.xStep
    baseY=grid[-1][0][1]
    rightX=grid[0][-1][0]
    bottomY=grid[0][0][1]-app.graph.yStep
    #print('baseX', baseX, 'baseY', baseY, 'rightX', rightX, 'bottomY', bottomY)
    for i in range(1,len(xTicks)):
        if xTicks[i]>=baseX and xTicks[i]<=rightX and yTicks[i]>=bottomY and yTicks[i]<=baseY:
            canvas.create_oval(xTicks[i]-r,yTicks[i]-r, xTicks[i]+r,yTicks[i]+r)
            canvas.create_line(lastX, lastY, xTicks[i], yTicks[i], fill=color, width=w)
            lastX=xTicks[i]
            lastY=yTicks[i]
    
def drawNewsDots(app, canvas, graph): #draws the clickable news dots onto the canvas
    newsList=graph.news
    for i in range(len(newsList)): 
        sentiment=newsList[i].sentiment
        color='green3'
        if sentiment=='Negative':
            color='red2'
        r=newsList[i].radius
        x=newsList[i].xCoord
        y=newsList[i].yCoord
        canvas.create_oval(x-r,y-r,x+r,y+r, fill=color)


def drawNewsCard(app, canvas): #draws the news card state 
    news=app.graph.news
    indexOfNews=app.showedNews #app.showedNews keeps track of which index we're showing
    margin=app.graph.margin
    canvas.create_rectangle(margin, margin, app.width-margin, app.height-margin
                            , fill='gray10')
    newsInfo=news[indexOfNews]
    font='courier 12'
    url=newsInfo.url
    title=newsInfo.title
    textInfo=newsInfo.text
    source=newsInfo.source
    date=newsInfo.date
    sentiment=newsInfo.sentiment
    tickers=newsInfo.tickers
    #newsImage=newsInfo.newsImage
    fill='Green3'
    if sentiment=='Negative':
        fill='red3'
    gap=(app.height-margin)/8
    canvas.create_text(app.width//2, margin+20, text=date, font='22', width=app.width*4/5, fill=fill)
    canvas.create_text(app.width//2, margin+gap, text=f'Title: {title}', font=font, width=app.width*4/5, fill=fill)
    canvas.create_text(app.width//2, margin+gap*2, text=f'Text: {textInfo}', font=font, width=app.width*4/5, fill=fill)
    canvas.create_text(app.width//2, margin+gap*3, text=f'Source: {source}.\nSentiment: {sentiment}\nStocks Affected: {tickers}', 
                                    font=font, fill=fill, width=app.width*4/5)
    canvas.create_text(app.width//2, margin+gap*4, text=url, font=font, fill=fill,width=app.width*4/5)
    canvas.create_text(app.width//2, margin+gap*5, text=sentiment, font=font, fill=fill, width=app.width*4/5)
    canvas.create_image(app.width//2,margin+gap*6, image=ImageTk.PhotoImage(app.images[indexOfNews])) #pulls the correct Image


def drawInputs(app, canvas): #draws the input state for industry analysis
    font = 'Arial 24 bold'
    gap=30 
    canvas.create_rectangle(0,0,app.width, app.height, fill='gray20')
    fill='green3'
    canvas.create_text(app.width/2,  app.height/2,
                       text=f'Market Cap = {app.cap}', font=font, fill=fill)
    canvas.create_text(app.width/2, app.height/2+gap, text=f'Industry = {app.industry}'
                        , font=font, fill=fill)

    text='Press d to get results!'

    canvas.create_text(app.width/2, app.height/2+gap*2, text=text,
                            font=font, fill=fill)

def drawInitialState(app, canvas): #draws the beginning state
    font='Coureir'
    phrase='Choose Single Stock Analysis by Clicking here!'
    
    canvas.create_rectangle(0,0,app.width/2,app.height, fill='steel blue')
    canvas.create_rectangle(app.width/2,0, app.width, app.height, fill='gray20')
    canvas.create_text(app.width/2+app.width/4, app.height/2, text=phrase, font=f'{font} 18 bold', fill='RoyalBlue2',
                       width=app.width/2-30)
    phrase2='Choose Industry Analysis by clicking here! (Post-MVP Project)'
    canvas.create_text(app.width/2-app.width/4, app.height/2, text=phrase2, font=f'{font} 18 bold',
                                 fill='gray10', width=app.width/2-30)
    
    time=datetime.now()  #documentation: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    d= time.strftime('%d/%m/%Y %H:%M:%S')
    boxWidth=360
    canvas.create_rectangle(app.width/2-boxWidth/2-40, app.height-100, app.width/2+boxWidth/2+40,
                            app.height, fill='deepSkyBlue')
    canvas.create_rectangle(app.width/2-boxWidth/2-20, app.height-90, app.width/2+boxWidth/2+20, 
                            app.height-10, fill='gray14')
    canvas.create_text(app.width/2, app.height-60, text=d, font=f'{font} 24 bold', width=boxWidth, fill='Spring Green3')
    canvas.create_text(app.width/2, app.height-30, text='Ver. 0.9', font=f'{font} 12 bold',
                                 fill='SeaGreen3')
    #drawScrollingTickers(app, canvas)
    #should add a mouse hover function later


def findMaxLength(app, fontSize): # needed to properly formate the final cell sheet 
    currMax=0
    for ticker in app.results: #first set returns data for all associated stock
        for catagory in app.results[ticker]:#returns each individual data point 
            if (len(catagory)+len(app.results[ticker][catagory]))*fontSize>currMax: #finds the longestBox
                currMax=(len(catagory)+len(app.results[ticker][catagory]))*fontSize
    return currMax


def drawDisplayState(app, canvas): #creates the lists of industries we have
    canvas.create_rectangle(0,0,app.width, app.height, fill='gray20')
    titleGap=20
    industryToLookAt=app.industries[app.industryIndex] #this is the current industry
                                                        #we want to display
    canvas.create_text(app.width/2, titleGap, text=f'{industryToLookAt.industry} {industryToLookAt.cap}',
                        font='Coureir 18', fill='Green3')

    stocksInIndustry=industryToLookAt.stockList
    gap=(app.height-titleGap)/(len(stocksInIndustry)+2)

    fontsize=int(app.width/100)
    fill='Green3'
    for i in range(len(stocksInIndustry)+1):
        font=f'coureir {fontsize}'
        if i==app.stockListIndex:
            font=f'coureir {fontsize+2} bold'
        if i == 0:
            canvas.create_text(app.width/2, titleGap+gap*(i+1), text='Industry Averages', 
                                font=font, fill=fill)
        else:
            canvas.create_text(app.width/2, titleGap+gap*(i+1), text=stocksInIndustry[i-1], font=font,
                                fill=fill)



def drawStockInd(app, canvas): #we draw the stock that we entered into 
    canvas.create_rectangle(0,0,app.width, app.height, fill='gray20')
    industry=app.industries[app.industryIndex] #this is an industry object
    fontSize=int(app.width/120)
    font=f'coureir {fontSize}'

    if app.stockListIndex!=0: #0 is for averages
        stock=industry.stockList[app.stockListIndex-1] #this gets us our stock we want to display 
                                                        #minus one because we have 1 for industry averages
        data=industry.dictionary #the dictionary results 
        toDisplay=data[stock] #this is what we're showing
        topGap=30
        fill='green3'
        canvas.create_text(app.width/2, topGap, text=stock, font='Coureir 18 bold', fill=fill )
   
        cols=8 #these are set since theres always 71 items
        rows=9
        xStep=app.width/(cols+1)
        yStep=app.height/(rows+1)
        c=1
        r=1
        for item in toDisplay:
            fill='Green3' #if fundamental is above average set to green
            average=industry.averages.get(item, None)
            basePercentage=None
            if average==None:
                pass
            else:
                if pMVP.cleanNumber(toDisplay[item])==None:
                    fill='light sky blue'
                elif average>pMVP.cleanNumber(toDisplay[item]): #if fundamental is worse than average
                    fill='Red3'
            if average!=None and pMVP.cleanNumber(toDisplay[item])!=None and average!=0:
                basePercentage=(pMVP.cleanNumber(toDisplay[item])-average)/average
                basePercentage=Mlmodel.roundToNearestCent(basePercentage*100)
                basePercentage=str(basePercentage)+'%'
            canvas.create_text(xStep*c,yStep*r,
                                text=f'{item}: {toDisplay[item]}\n{basePercentage}\nAvg: {average}',
                               width=xStep, font=font, fill=fill)
            c+=1
            if c==cols+1:
                c=1
                r+=1
    else:
        fill='light sky blue'
        topGap=30
        canvas.create_text(app.width/2, topGap, width=app.width, text='Industry Averages', 
                                font=f'coureir {fontSize+4} bold', fill=fill )
        toDisplay=industry.averages
        cols=8 #these are set since theres always 71 items
        rows=9
        xStep=app.width/(cols+1)
        yStep=app.height/(rows+1)
        c=1
        r=1
        for item in toDisplay:
            fill='Green3' #if fundamental is above average set to green
            canvas.create_text(xStep*c,yStep*r,text=f'{item}: {toDisplay[item]}',
                               width=xStep, font=font, fill=fill)
            c+=1
            if c==cols+1:
                c=1
                r+=1

def drawErrorState(app, canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill='gray20')
    canvas.create_text(app.width/2, app.height/2, width=app.width-50,
                        text="Webdriving failed, either restart program or press R to reset",
                        fill='Red3', font='Coureir 24 bold')

def redrawAll(app, canvas): #this is a statemap of what should be drawn and when 
    if app.initState==True:
        drawScrollingTickers(app, canvas)
        drawInitialState(app, canvas)   
    else:
        if app.singleStockAnalysis:
            if app.inputStateSingle: #input page
                drawInputSingle(app,canvas)
                drawScrollingTickers(app, canvas)
            elif app.displayStateSingle: # else go to display what we've entered
                
                if app.graphState: #graph state
                    drawGraph(app, canvas)
                    if app.showNews:
                        drawNewsCard(app, canvas)
                    if app.showEstimate:
                        drawEstimation(app, canvas)
                    if app.showFundamentals:
                        drawStockFundamentals(app, canvas)
                elif app.portfolioState:
                    drawPortfolioDisplay(app, canvas) 
                else:
                    drawDisplaySingle(app, canvas)
                    drawScrollingTickers(app, canvas)
        elif app.industryAnalysis: #industry analysis pages 
            if not app.displayState and app.industryInputState: #input state
                drawInputs(app, canvas)
            elif (app.displayState and app.industry!=None or app.industry=='Press p to enter'
               or app.cap!=None or app.cap=='Press spacebar to enter') and app.industries!=[]: #display groups
                drawDisplayState(app, canvas)  
            if app.displayStockInd: #display single stock fundamental analysis
                drawStockInd(app, canvas)
    if app.errorState: #this is if something screwed up
        drawErrorState(app, canvas)     

def run():
    runApp(width=1250, height=650)

run()
  
'''Dead code may be useful later?

    def makeCoords(self, x, y): #takes values and returns coords of them on the grid bug fix needed! 
        finalXCoords=[]
        finalYCoords=[]
        baseY=self.grid[-1][0][1] #bottom most y coord 
        maxYV=max(self.yList) #min and max Values of Y calculated once to save computing 
        minYV=min(self.yList) #these values are used for scalling steps
        baseX=self.grid[0][0][1]-self.xStep
        minXV=(min(self.xList))
        maxXV=(max(self.xList))
        
        finalXCoords.append(baseX) #x needs x step due to how the box coords are found by
        finalYCoords.append(baseY)             #bottom right coordinate
        for i in range(len(x)): #x and y should have same length 
            calcY=baseY-(y[i]-minYV)/(maxYV-minYV)*self.yLength
            calcX=baseX+(x[i]-minXV)/(maxXV-minXV)*self.xLength
            finalXCoords.append(calcX)
            finalYCoords.append(calcY)
        return finalXCoords, finalYCoords
        #finalY2=baseY-(y[-1]-minYV)/((maxYV-minYV))*self.yLength 


    # def makeGrid(self):
    #     percentOfCanvas=0.05
    #     marginX=self.width*percentOfCanvas 
    #     marginY=self.height*percentOfCanvas
    #     xLength=self.width-2*marginX
    #     yLength=self.height-2*marginY
    #     self.yLength=yLength
    #     self.xLength=xLength
    #     self.marginY=marginY
    #     xStep=xLength/(max(self.xList)-min(self.xList)) #len(self.xList)
    #     yStep=yLength/((max(self.yList)-min(self.yList)))
    #     self.xStep=xStep
    #     self.yStep=yStep
    #     y=yStep+marginY
    #     yI=0
    #     while yI<len(self.yList)-1:
    #         x=marginX+xStep
    #         coords=[]
    #         xI=0
    #         while xI<len(self.xList)-1:
    #             x=marginX+xStep+xStep*xI
    #             coords.append((x,y)) #gives tuple of x and y
    #             xI+=1
    #         self.grid.append(coords)
    #         y=marginY+yStep*yI
    #         yI+=1
    #     self.graphWidth=self.grid[0][len(self.grid[0])-1][0]-(self.grid[0][0][0]-self.xStep) #last xCord-first xCord
    #     self.graphHeight=self.grid[len(self.grid[0])-1][0][1]-(self.grid[0][0][1]-self.yStep) #last y cord - first y cord

    # def cutTop(self, yCords):  
    #     print('ENTering cut top')       
    #     gridCopy=[]
    #     minYCord=min(yCords)
    #     print('min', minYCord)
    #     maxYCord=max(yCords)
    #     print('max',maxYCord)
    #     index=len(self.grid)-1
    #     epsilon=1*10**-1
    #     print('GridBefore', self.grid)
    #     while index>=0 and self.grid[index][0][1]>=minYCord: #this cleans unused Y's 
    #         if not almostEqual(self.grid[index][0][1], minYCord):
    #             gridCopy.append(self.grid[index])
    #         index-=1
    #     grid=gridCopy[-1::-1]
    #     shiftUp=grid[0][0][1]-self.yMargin #shift up to reorient
    #     #self.shiftUp=shiftUp
    #     for i in range(1, len(grid)):
    #         for i2 in range(len(grid[i])):
    #             self.grid[i-1][i2]=(grid[i][i2][0],grid[i][i2][1]-shiftUp) #creates new tuple with updated shift up coord
    #     for y in range(len(self.yTicks)):
    #         self.yTicks[y]-=shiftUp
    #     print('Grid After', self.grid)
    #     # newYStep=self.grid[-1][0][1]-self.grid[-2][0][1]
    #     # self.yStep=newYStep



def drawDisplayState(app, canvas): #needs work developping proper formatting, jank formatting rn
    wid=app.width
    height=app.height 
    # 
    # with open('test1.txt', 'rt') as f:
    #     text=f.read()
    
    # with open('data.pickle', 'rb') as picky2:
    #     text = pickle.load(picky2)
    fontSize=8
    # xStep, yStep, chunkStep=primeForWindow(app, canvas, fontSize)
    xStep, yStep, chunkStep=app.xStep, app.yStep, app.chunkStep
    i=0
    for ticker in app.results:
        canvas.create_text(xStep/2, yStep/2+i*chunkStep, text=ticker)
        i2=0
        for catagory in app.results[ticker]:
            r=i2*xStep//(app.cols*xStep)+1
            c=i2%(app.cols) 
            canvas.create_text(xStep*c+xStep/2,yStep*r+yStep/2+i*chunkStep, 
                         text=catagory+' '+app.results[ticker][catagory], font=f'Courier {fontSize}')
            i2+=1
        i+=1
# def primeForWindow(app): #idea to format the data in a way that can be displayed in the canvas
#                                  # in blocks
#     numOfTerms=0
#     for ticker in app.results:
#         numOfTerms=len(app.results[ticker])
#         break
#     fontSize=app.fontSize
#     longestBox=findMaxLength(app, fontSize)
#     app.cols=int(app.width/longestBox)+1
#     app.rows=int(numOfTerms/app.cols * len(app.results))+1 #number of tickers*num for each ticker + 1 row
#     app.xStep=longestBox
#     app.yStep=app.height/app.rows
#     app.chunkStep= (1 + math.ceil(numOfTerms/app.cols))*app.yStep
#     #stepSizeX, stepSizeY, chunkStep)

def findMaxLengthDict(app, dictionary): #takes a dictionary and finds max length in pixels
                                    #of key plus value
    maxLength=0
    for item in dictionary:
        currLength=0
        currLength+=len(item)+len(dictionary[item])
        if currLength>maxLength:
            maxLength=currLength
    return maxLength
        


'''