#manga dex scrapper 
import selenium
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver import Chrome 
import os
from cmu_112_graphics import *  
import math
import pickle
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv

#import Graphics
'''
find_element_by_id
find_element_by_name
find_element_by_xpath
find_element_by_link_text
find_element_by_partial_link_text
find_element_by_tag_name
find_element_by_class_name
find_element_by_css_selector
'''

#Code from CMU 112 Website:
#https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


class stockGroup(object):
    def __init__(self, marketCap, industry):
        self.marketCap=marketCap
        self.industry=industry
        self.group={}  #dictionary containing every stock and respective stats with Market Cap and industry
        self.historicData={}  #stores the historic data for the stocks by name.csv
        
    def addToGroup(self, ticker, data):
        self.group[ticker]=data
    
    def getGroup(self):
        return str(self.group)

    def __repr__(self):
        return (f'Market cap= {self.marketCap} '+f'Industry={self.industry} '
            +f'group {self.group}')

    def  __str__(self):
        return ((f'Market cap= {self.marketCap} '+f'Industry= {self.industry} '
            +f'group {self.group}'))



def matchCatagories(catagories, nums): #matches parsed numbers with respective catagories, put into dictionary
    final={}
    if len(catagories)!=len(nums): #in case something goes wrong
        return final
    else:
        for i in range(len(catagories)):
            final[catagories[i]]=nums[i]
    return final



# Parts of the Code were striped and adjusted from Hack 112 code that I wrote for team Stone-Face-emote
#this part is for post mvp project
def searchForStocks(cap, industry):
    with Chrome(executable_path=r'C:\Users\George\School Work\112 code\chromedriver_win32\chromedriver.exe') as driver:
        url ='https://finviz.com/screener.ashx'
        driver.get(url)   
        mCap=driver.find_element_by_id('fs_cap')
        mCap.send_keys(cap)
        group=stockGroup(cap, industry)
        #driver.execute_script('window.scrollTo(0, 300)')
        time.sleep(1)
        ind=driver.find_element_by_id('fs_ind')
        ind.send_keys(industry)

        stocks=driver.find_elements_by_class_name('screener-link-primary')
        driver.execute_script("window.scrollTo(0, 400)")
        attributeUrl=driver.current_url
        listOfStockLinks=[]
       
        for i in range(len(stocks)):  # gives links for each stock we're going into
            listOfStockLinks.append(stocks[i].get_attribute('href'))

        stockAttributes={}
        for i2 in range(len(listOfStockLinks)):
            stockUrl=str(listOfStockLinks[i2])
            driver.get(stockUrl)
            stockA=driver.find_elements_by_class_name('snapshot-td2') 
            ticker=driver.find_element_by_id('ticker').text
            #stockAttributes[ticker]=[nums.text for nums in stockA]
            nums=[nums.text for nums in stockA]
            catagories=driver.find_elements_by_class_name('snapshot-td2-cp')
            catagories=[cat.text for cat in catagories]
            data=matchCatagories(catagories, nums)
            group.addToGroup(ticker, dict(data))
    
            with open(f'{cap}_{industry}.pickle', 'wb') as picky:
                pickle.dump(group.group, picky)
            #return group.group 

# #this is a modified version of the above function that works when given a direct url
# #So technically it's modified Hack 112 Code that I wrote for Stone-face Emote 
# def serachForGroup(url):
#     with Chrome(executable_path=r'C:\Users\George\School Work\112 code\chromedriver_win32\chromedriver.exe') as driver:
#         driver.get(url)  
#         stocks=driver.find_elements_by_class_name('screener-link-primary')
#         driver.execute_script("window.scrollTo(0, 400)")
#         attributeUrl=driver.current_url
#         listOfStockLinks=[]
#         #defaultDownload={'download.default_directory':'C:\Users\George\School Work\112 code\projects\TermProject'}
#         for i in range(len(stocks)):  # gives links for each stock we're going into
#             listOfStockLinks.append(stocks[i].get_attribute('href'))
#         #print(listOfStockLinks)
#         stockAttributes={}
#         for i2 in range(len(listOfStockLinks)):
#             stockUrl=str(listOfStockLinks[i2])
#             driver.get(stockUrl)
#             stockA=driver.find_elements_by_class_name('snapshot-td2') 
#             ticker=driver.find_element_by_id('ticker').text
#             #stockAttributes[ticker]=[nums.text for nums in stockA]
#             nums=[nums.text for nums in stockA]
#             catagories=driver.find_elements_by_class_name('snapshot-td2-cp')
#             catagories=[cat.text for cat in catagories]
#             data=matchCatagories(catagories, nums)
#             group.addToGroup(ticker, dict(data))

        
#searchForStocks('small', 'food wholesale')

options = webdriver.ChromeOptions() 
historicalPrices = {'prefs': {'download': {'default_directory': r'C:\Users\George\School Work\112 code\projects\TermProject'}}}

def getHistoricalPrices(ticker, timeHorizon):
    with Chrome(executable_path=r'C:\Users\George\School Work\112 code\chromedriver_win32\chromedriver.exe', desired_capabilities = historicalPrices) as driver:
        
        historicData=f'https://www.nasdaq.com/market-activity/stocks/{str(ticker)}/historical'
        driver.get(historicData)
        time.sleep(2)
        time.sleep(1)
        link=''
        if timeHorizon == '1M':
            link=1   
        elif timeHorizon== '6M':
            link=2
        # else: #add this later    
        #     link=3      /html/body/div[4]/div/main/div/div[5]/div[2]/div/div[1]/div/div[1]/div[3]/div/div/div/button[2]         
                          #/html/body/div[3]/div/main/div/div[5]/div[2]/div/div[1]/div/div[1]/div[3]/div/div/div/button[2]
        timeHorizonLink=f'/html/body/div[3]/div/main/div/div[5]/div[2]/div/div[1]/div/div[1]/div[3]/div/div/div/button[{link}]'
        time.sleep(1)
        try: #if no popup 
            driver.find_element_by_xpath(timeHorizonLink).click()
        except: #if there is popup 
            driver.find_element_by_xpath('//*[@id="__ghostery-close-icon-line1"]').click() # gets rid of popup
            driver.find_element_by_xpath(timeHorizonLink).click()
        time.sleep(1)
            '/html/body/div[4]/div/main/div/div[5]/div[2]/div/div[1]/div/div[1]/div[3]/a'
        csv='/html/body/div[3]/div/main/div/div[5]/div[2]/div/div[1]/div/div[1]/div[3]/a'
        driver.execute_script("window.scrollTo(0, 500)")
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH,csv)))
        time.sleep(3) #this is for additional backup incase it pulls the 1 month data instead of 
                      #the 6 month or YTD
        #csvFile=driver.find_element_by_xpath(csv).get_attribute("href")
        csvFile=driver.find_element_by_class_name('historical-data__download').get_attribute('href')
        csvFile=csvFile
        content=requests.get(csvFile, headers={'User-Agent': 'PostmanRuntime/7.24.1'}).content
        f=open(f'{ticker}{timeHorizon}.csv', 'wb')
        f.write(content)
        f.close()
        #download_file(csvFile, f'{ticker},{timeHorizon}')
        return True

apiKey= 'INSERT YOUR OWN API KEY HERE'
def getNews(ticker, dates): #500 calls 
    # format for dates= 03152019-03252019
    json=requests.get(f'https://stocknewsapi.com/api/v1?tickers={ticker}&date={dates}&items=50&token={apiKey}')
    dictionary=json.json()
    return dictionary
    







# # https://stackoverflow.com/questions/45978295/saving-a-downloaded-csv-file-using-python?rq=1
# #for downloading a csv file
# def download_file(url, filename):
#     # Downloads file from the url and save it as filename
#     # check if file already exists
#     if not os.path.isfile(filename):
#         response = requests.get(url)
#         # Check if the response is ok (200)
#         if response.status_code == 200:
#             # Open file and write the content
#             with open(filename, 'wb') as file:
#                 # A chunk of 128 bytes
#                 for chunk in response:
#                     file.write(chunk)
#     else:
#         print('File exists')
  
''' Soup Code if I would rather use this instead of web driving
    #driver.find_element_by_xpath('//*[@id="screener-content"]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[3]/a').click()
    #//*[@id="screener-content"]/table/tbody/tr[4]/td/table/tbody/tr[3]/td[3]/a
    #for stock in stocks:
    #print(stocks)
    stockLink=stocks[0].get_attribute('href')
    driver.get(str(stockLink))
    time.sleep(5)
    currentUrl=driver.current_url
    page = requests.get(currentUrl)
    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.find(class_='screener-link'))
    all=soup.get_text()
    #print(marketCaps)
    print(all)



    
'''
