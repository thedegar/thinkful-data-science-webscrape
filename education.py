#####################################################
# Tyler Hedegard
# 6/21/2016
# Thinkful Data Science
# GDP + Education Web Scrape Project
#####################################################

from bs4 import BeautifulSoup
import requests
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt
import csv

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
    cur.execute("DROP TABLE IF EXISTS gdp")
    cur.execute("CREATE TABLE countries (country text, male number, female number, year number)")
    cur.execute("CREATE TABLE gdp (country_name text, _1999 text, _2000 text, _2001 text, _2002 text, _2003 text, _2004 text, _2005 text, _2006 text, _2007 text, _2008 text, _2009 text, _2010 text)")

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
    
# Show descriptive statistics for the education data
list = ['male','female']
for each in list:
    col = df[each]
    #plt.hist(col)
    print('Descriptive statistics for males: ')
    print('  Mean: {}'.format(col.mean()))
    print('  Median: {}'.format(col.median()))
    print('  Min: {}'.format(col.min()))
    print('  Max: {}'.format(col.max()))
    print('  Range: {}'.format(col.max()-col.min()))
    print('  Variance: {}'.format(col.var()))
    
# Collect GDP Data

with open('GDP.csv','r') as inputFile:
    next(inputFile) # skip the first two lines
    next(inputFile)
    next(inputFile)
    next(inputFile)
    header = next(inputFile)
    inputReader = csv.reader(inputFile)
    for line in inputReader:
        if line[43] == '':
            pass
        else:
            data = (line[0], line[43],  line[44], line[45], line[46], line[47], line[48], line[49], line[50], line[51], line[52], line[53], line[54])
            with con:
                cur.execute('INSERT INTO gdp (country_name, _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',data)
    
    cur.execute("select * from gdp")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    df_gdp = pd.DataFrame(rows, columns=cols)
    

    