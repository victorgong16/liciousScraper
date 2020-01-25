import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
import lxml
import re
import html
from collections import defaultdict

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)


#Set URL
driver.get("https://www.toronto.ca/explore-enjoy/festivals-events/winterlicious/restaurants-menus/?view=tabList")
more_buttons = driver.find_elements_by_class_name("pageToggleBtn")

#Toggle the list so the restaurants list is actually populated
more_buttons[0].click()
time.sleep(10)
page_source = driver.page_source

#Parse the HTML for the table of restaurants
soup = BeautifulSoup(page_source, 'lxml')
results = soup.find_all(id=re.compile("liciouslisttablerow*"))

res = []

#Parse the tables for the restaurant names and save them
for tableRow in results:
    rowString = str(tableRow.find(class_="showdetail"))
    nameString = rowString.split("\"")[5]
    restaurantName = html.unescape(nameString.split("=")[1])
    res.append(restaurantName)

clientID = "kqKvxdiDC4Q1FTPxHOv6VA"
apiKey = ""

#Define Yelp API end point to call and parameters
endpoint = "https://api.yelp.com/v3/businesses/search"
header = {"Authorization": "bearer %s" % apiKey}

restaurantsList = defaultdict()

for restaurant in res:
    parameters = {"term" : restaurant, 
              "limit" : 1,
              "location" : "Toronto"}

    response = requests.get(url = endpoint, params = parameters, headers = header)

    #Convert response from JSON to dict

    data = response.json()
    
    for business in data["businesses"]:
        restaurantsList[business["name"]] = business["rating"]
        
sortedRestaurantsList = sorted(restaurantsList.items(), key=lambda x : x[1], reverse=True)

f = open("C:/Users/Victor/Desktop/liciousRestaurants.txt", "w+", encoding="utf-8")

for pair in sortedRestaurantsList:
    f.write(pair[0] + " " + str(pair[1]) + "\r\n")

f.close()
    
