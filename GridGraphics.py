from cmu_112_graphics import *



class graph(object): #graph object will store scale, function to prime the graph based on width and height of a canvas
    def __init__(xlist, yList, width, height, margin):
        app.xList=xlist
        app.yList=yList
        app.width=width 
        app.height=height
        app.grid=[] # 2d array for the grid of the graph stores center cords of each 'cell'
        app.margin=margin # margin for axes
    
    def findSpikes(): #finds all spikes in the graph looks at derivative and pixel counting? 
        pass 

    def primeForCanvas(): # primes the coords and stuff for canvas 
        pass

    def makeGrid():
        xLength=app.width-2*margin
        yLength=(app.height-2*margin)
        xStep=xLength/len(app.xList)
        yStep=yLength/len(app.yList)
        y=yStep
        while y<yLength:
            x=xStep
            coords=[]
            while x<xLength:
                coords.append(x-xStep/2,y-yStep/2)
            app.grid.append(coords)
        
        
grid1=graph([1,2,3,4,5],[3,5,2,6,7],800,800,50)

