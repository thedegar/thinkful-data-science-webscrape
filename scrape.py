#####################################################
# Tyler Hedegard
# 6/21/2016
# Thinkful Data Science
# UN Web Scrape
#####################################################

from bs4 import BeautifulSoup
import requests
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt

url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"

r = requests.get(url)

soup = BeautifulSoup(r.content)

myTable = soup('table')[6]

my_tbody = myTable('tbody')[3]
#header = my_tbody('tr')[3]
max_count = len(my_tbody('tr'))

# Connect to the database
con = lite.connect('UNdata.db')

with con:
    cur = con.cursor()
    # Create the countries table
    cur.execute("DROP TABLE IF EXISTS countries")
    cur.execute("CREATE TABLE countries (country text, male number, female number, year number)")

    for i in range(4,max_count): #header is td[3] so this gives all the raw data
        row = my_tbody('tr')[i]
        country = (row('td')[0].string)
        male = int(row('td')[7].string)
        female = int(row('td')[10].string)
        year = int(row('td')[1].string)
        data = (country,male,female,year)
        cur.execute("INSERT INTO countries VALUES(?,?,?,?)", data)
        
    cur.execute("select * from countries")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    
list = ['male','female']
for each in list:
    col = df[each]
    #plt.hist(col)
    print('Descriptive statistics for males: ')
    print('  Mean: {}'.format(col.mean()))
    print('  Min: {}'.format(col.min()))
    print('  Max: {}'.format(col.max()))
    print('  Range: {}'.format(col.max()-col.min()))
    print('  Variance: {}'.format(col.var()))
