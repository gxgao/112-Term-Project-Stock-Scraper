# 112-Term-Project-Stock-Scraper
Project was done at the end of 15-112. 
Video Demo is here: https://www.youtube.com/watch?v=qcPmRuLafEA&t=9s

The program is a simple Stock Analyzer: 
Can do single stock analysis. It web scrapes for stock info and graphs it in a custom built tkinter graphing interface which can be commanded to use multivariate regression to build a linear, and a polynomial regression model (The models are based loosely on a time series analysis).  Additionally, it pulls from the web stock fundamentals (p/e ratio, volume, ROA etc.) so that they can be easily accessed. 
Furthermore, it analyzes the price chart and points out major price spikes and uses a stock news API to get correlated news for that price change.
After MVP and Additional:
There is an industry average analyzer that, given a market cap and industry, it finds all relevant companies and pulls the average values for each of their fundamentals. This can then be used to compare individual stocks within the industry to get a better financial sense of how a company is doing. 



How to run the project. For example, which file the user should run in an editor. If your project uses data/source files, also describe how the user should set those up.

To run the project you need to first make sure the webdriver is paired properly to your web browser and that the executable path leads to where your webdriver is stored. 
Next make sure that all pickle, excel, image, and supplemental program files stay in the same folder as the main function (Graphics). 

To run the entire thing you need to make sure you have a good stable internet connection otherwise it could throw a SSL error or network error at some point. There are some built in safeguards with try and except but it’s better to be safe. If it fails on a run (it’s more likely for industry analysis) please restart the program and try again (sometimes the internet connection just stabilizes/ a bug with selenium is cleared, or the host server lets you through.).  IF you cannot get that to run I have included instructions in the quick test on how to run things with examples that I’ve preloaded (industry analysis should already have 2 loaded).

ALSO NOTE: If the CSV File obtained from NASDAQ is incomplete (errors in dates, skipping dates, etc, etc) the grapher may screw up. Most likely it will skip a few of the last data points or omit it all together. Also if you close the webdriver prematurely it may crash the program. 
IF not sure check the excel sheet for errors. 

To start, click on the right side of the screen for single stock analysis. Follow instructions on screen to enter your ticker and time period.
ONCE in the graphing state: 
Press ‘p’ to get polynomial and linear regression. 
Once Regression is shown press ‘g’ to get an estimate. Enter a number. There are some checks in place to test if you didn’t but you won’t get anything unless you enter a number.
To leave the estimate: press ‘q’ 
To get fundamentals: press ‘s’ to leave also press ‘s’. 
To get news click the dots. To leave press Escape. 
To leave graphing state press ‘escape’ 
Once in the display state with what you’ve input (the one without the fangs) 
Click on portfolio to be led to portfolio. You can move up and down with the arrow keys, and ‘enter’ to enter into a graph. Press ‘escape’ to leave

	In industry analysis:
	After you’ve input what you want (MAKE SURE TO CHECK https://finviz.com/screener.ashx to see if you’re market cap and industry are legal things that can be sent). IF THEY ARE NOT THE PROGRAM WILL ENTER ERROR STATE AND YOU must restart with R or close the program (that would be the safest). ALSO NOTE: Finviz is a fickle server host, and likes to shut down the connection often. Thus it may take a few tries to get the web scraping to work. You can preload the pickle file of industries you’ve seen before with: 
prepIndustryAnalysis(app, ‘filename.csv’)
in the app started. Make sure to put it as the last command in app started so after:
  app.industryInputState=False 
ex:
  app.industryInputState=False 
  prepIndustryAnalysis(app, ‘Mid_advertising.pickle)


	Arrow keys to navigate, ‘enter’ to see the numbers (you can also exit by pressing enter again). The way it’s loaded right now always includes drug stores and mid gold. Thus to get your actual results press the ‘right’ arrow key until it scrolls the results just obtained from the scraping. If it’s not there, the scraping probably contained an error and you must restart with ‘r’ or restart the program. 

General commands:
To restart, press ‘r’

Which libraries you're using that need to be installed. If you can include the library in the submission, that is preferred.

import os
from cmu_112_graphics import *  
import pickle 
import math
import Mlmodel
import PIL 
from tkinter import *
import random
from datetime import datetime,timedelta, date
from yahoo_fin import stock_info as si
from PIL import Image
import selenium
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver import Chrome 
import math
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv
import pandas
import requests
import quandl
from yahoo_fin import stock_info as si
import pickle
import numpy as np
Import copy


Shortcut commands:
To run on quick mode, I added a tester filer called tester 3. This skips the web scraping part (which can take a little time) and immediately has 2 industries loaded as well as a 2 graphs preloaded. To swap graphs, there are around 7 additional excel files that you can swap to. You just need to swap the prepGraph(csvFile)  function in the main graphics program to the CSV file you want to graph and analyze. It should be triggered by the event.key==’L’ which can be pressed after you go into single stock analysis, and once you enter ‘anything’ into the ticker. Make sure not to press ‘Enter’ during the input collection state. Thus you can skip web scraping and go immediately to the custom build graph. SO basically If you press L after entering anything into the inputs, it skips directly to the graphing state with no web scraping. NOTE: THIS FUNCTION IS NOT AVAILABLE IN THE MAIN FILE. Pressing L will do nothing. Please read on about the news functionality if you are in testing mode!


NOTE: This requires a NEWS API to work. An API key can be found https://stocknewsapi.com/. Your api key must be inserted into the termproject.py file under the variable apiKey= 'INSERT YOUR OWN API KEY HERE'


