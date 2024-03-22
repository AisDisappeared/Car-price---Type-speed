
from selenium import webdriver 
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import mysql.connector



# define lists we need 
sites_list = []
temp = []


# making a connection between python and mysql DATABASE and creating a cursor 
cnx = mysql.connector.connect(user="root",password="ali@grpc1",host="127.0.0.1",database="car_and_type")
cursor = cnx.cursor()


# query to make a table for storing current prices of car we want to buy 
query = ("CREATE TABLE IF NOT EXISTS type_links (id INTEGER PRIMARY KEY AUTO_INCREMENT, Link TEXT UNIQUE NOT NULL);")
cursor.execute(query)


# Replace the string 'path/to/geckodriver' with the actual path to your GeckoDriver executable
service = Service(executable_path='/snap/bin/geckodriver')
# Create a new instance of the Firefox Options class
options = Options()
# Create a new instance of the Firefox WebDriver
driver = webdriver.Firefox(service=service, options=options)
# Use the WebDriver instance to navigate to a webpage
driver.get('https://www.google.com')


# function to search google
def google_searcher(inPUT='type test'):
    # detectin google search bar and search type testing into that 
    search_bar = driver.find_element(By.NAME,'q')
    search_bar.send_keys(inPUT)
    search_bar.send_keys(Keys.ENTER)



# Function to find links on Google search results
def link_finder(func=google_searcher()):
   temp = []
   google_searcher()
   wait = WebDriverWait(driver, 10)
   elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'cite')))
   for element in elements:
       temp.append(element.text)
   return temp


# calling function and put it into a variable
temp = (link_finder())

# use regex to extract and cut the elements we want 
for var in temp:
    new_var = re.findall(r"^.*\..{2,4}" , var)
    if len(new_var) != 0:
        sites_list.append(new_var)


# insert the data we scraped into database 
for item in sites_list:
    item = ''.join(item)
    item = str(item)
    query = ("INSERT IGNORE INTO type_links (link) VALUES (\'%s\')" %  item)
    cursor.execute(query)
    cnx.commit()
    
# congratulations , you made it 
driver.close()