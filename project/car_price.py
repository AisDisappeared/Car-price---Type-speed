import requests
import re
import mysql.connector
import csv 
from bs4 import BeautifulSoup

# making some lists to storing the different fields values and inserting them into database at the end
list_names = []
list_prices = []
list_gearbox = []
list_locs = []
list_performances = []
list_models = []
temp1 = []


# making a connection between python and mysql DATABASE and creating a cursor 
cnx = mysql.connector.connect(user="root",password="ali@grpc1",host="127.0.0.1",database="car_and_type")
cursor = cnx.cursor()


# query to make a table for storing current prices of car we want to buy 
query = ("CREATE TABLE IF NOT EXISTS car_info (id INTEGER PRIMARY KEY AUTO_INCREMENT, name TEXT NOT NULL ,  price TEXT UNIQUE NOT NULL , gearbox TEXT NOT NULL , location TEXT NOT NULL , PERFORMANCE FLOAT UNIQUE NOT NULL , model INT NOT NULL);")
cursor.execute(query)


# now it's time to create a request as a client to server for doing web scraping operation 
res = requests.get("https://www.hamrah-mechanic.com/cars-for-sale/")
soup = BeautifulSoup(res.text , "html.parser")


# seperating the items and different elements or fields from the content we catched
names = soup.find_all("span",attrs={"class": "carCard_header__name__ib5RB"})
prices = soup.find_all("div" , attrs={"class" : "carCard_price-container__cost__BO_Hy"})
gearbox = soup.find_all("span" , attrs={"class" : "carCard_header__subtitle__XJ7UZ"})
location = soup.find_all("span" ,attrs={"class" : "carCard_specification__item-text__2c1Ub"})



# Filling lists and inserting the elements into the lists we created and some clean working with regex and deleting additional elements

# name list
for name in names:
    list_names.append(name.text)


# models list
for model in names:
    m = re.findall(r"\d{4}" , model.text)
    m = "".join(m)
    m = int(m)
    list_models.append(m)


# price list
for price in prices:
    p = re.findall(r"\d.+ " , price.text )
    p = ''.join(p)
    if ',' in p:
        p = p.replace(',','.')
    list_prices.append((p))


# gearbox list
for ggg in gearbox:
    list_gearbox.append(ggg.text)


i = 0
# location list
for loc in location:
    l = re.findall(r"\D+" , loc.text )
    l = ''.join(l)
    if ',' in l:
        l = l.replace(',','')
        if 'KM' in l:
            l = l.replace('KM','')
        
    elif 'KM' in l:
        l = l.replace('KM','')
    if len(l) != 1:
        list_locs.append(l)
 


# performance list
for per in location:
    p = re.findall(r"\d.*" , per.text )
    p = ''.join(p)
    if 'KM' in p:
        p = p.replace('KM','')
        if ',' in p:
            p = p.replace(',','.')
    if len(p) != 0:
        p = float(p)
        list_performances.append(p)



# mix all lists together by map function and convert them a single list 
main = list(map(list , zip(list_names,list_prices,list_gearbox,list_locs,list_performances,list_models)))


# insert the data we scraped into database 
for element in main:
    query = ("INSERT IGNORE INTO car_info (name , price , gearbox , location , PERFORMANCE , model) VALUES (\'%s\' , \'%s\' , \'%s\', \'%s\' , %f , %i) " 
             % (str(element[0]),str(element[1]),str(element[2]),str(element[3]),float(element[4]) , (element[5])))
    cursor.execute(query)
    cnx.commit()

# query to catch and get all data stored at database to save them in csv file we created
query_get = ("SELECT * FROM car_info")
cursor.execute(query_get)

# open a csv file at write mode and put the all data into csv file 
with open("/home/disappeared/Desktop/project/test.csv" ,"w",newline='') as fhandle:
    writer = csv.writer(fhandle)
    columns = [i[0] for i in cursor.description]
    writer.writerow(columns)
    for row in cursor:
        writer.writerow(row)



