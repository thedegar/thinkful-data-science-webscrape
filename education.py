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
import numpy as np
import statsmodels.api as sm

url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"

r = requests.get(url)

soup = BeautifulSoup(r.content)

myTable = soup('table')[6]

my_tbody = myTable('tbody')[3]
#header = my_tbody('tr')[3]
max_count = len(my_tbody('tr'))

# Connect to the database
con = lite.connect('UNdata.db')

def sqlTodf(query):
    """creates a pandas dataframe from a sql query
    assumes sqlite3 connection = con and cur = con.cursor()"""
    with con:
        cur.execute(query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=cols)

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
        
df_edu = sqlTodf("select * from countries")
    
# Show descriptive statistics for the education data
list = ['male','female']
for each in list:
    col = df_edu[each]
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
    country_list = []  # handles duplicate rows
    for line in inputReader:
        if line[43] == '' or line[0] in country_list:
            pass
        else:
            country_list.append(line[0])
            data = (line[0], line[43],  line[44], line[45], line[46], line[47], line[48], line[49], line[50], line[51], line[52], line[53], line[54])
            with con:
                cur.execute('INSERT INTO gdp (country_name, _1999, _2000, _2001, _2002, _2003, _2004, _2005, _2006, _2007, _2008, _2009, _2010) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',data)
    
df_gdp = sqlTodf("select * from gdp")
df_join = sqlTodf("select c.*, g.* from countries c join gdp g on c.country = g.country_name")
df_join['gdp'] = ''
    
#Find the gdp for the year of the education data point
for i in range(0,df_join.shape[0]):
    this = '_'+str(df_join['year'][i])
    df_join['gdp'][i] = float(df_join[this][i])
    
# Final clean data set to test with
df_test = df_join[['country','male','female','year','gdp']]
male = df_test['male']
female = df_test['female']
gdp = df_test['gdp']

# The dependent variables are male and female
y_male = male
y_female = female
# The independent variable is gdp
# converting to log.  As regular number the fit is even worse
x = np.log(np.array(gdp, dtype=float))
X = sm.add_constant(x)

male_model = sm.OLS(y_male, X)
female_model = sm.OLS(y_female, X)

f_male = male_model.fit()
f_female = female_model.fit()

# Null hypothesis is that the education level and gdp do not relate to each other
f_male.summary()
"""
Conclusion: 
  Reject the null hypothesis since p < 0.05. 
  Male education levels are impacted by the GPD of the country.
  The fit of this model is not great though with R-squared = 0.248.
  f(x) = 0.5437(log(x)) - 0.5170 
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                   male   R-squared:                       0.248
Model:                            OLS   Adj. R-squared:                  0.242
Method:                 Least Squares   F-statistic:                     46.72
Date:                Fri, 24 Jun 2016   Prob (F-statistic):           2.23e-10
Time:                        14:42:55   Log-Likelihood:                -327.83
No. Observations:                 144   AIC:                             659.7
Df Residuals:                     142   BIC:                             665.6
Df Model:                           1                                         
==============================================================================
                 coef    std err          t      P>|t|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         -0.5170      1.909     -0.271      0.787        -4.290     3.256
x1             0.5437      0.080      6.835      0.000         0.386     0.701
==============================================================================
Omnibus:                        1.467   Durbin-Watson:                   2.184
Prob(Omnibus):                  0.480   Jarque-Bera (JB):                1.077
Skew:                          -0.189   Prob(JB):                        0.584
Kurtosis:                       3.193   Cond. No.                         232.
==============================================================================
"""
f_female.summary()
"""
Conclusion: 
  Reject the null hypothesis since p < 0.05. 
  Female education levels are impacted by the GPD of the country.
  The fit of this model is also not great though with R-squared = 0.216.
  f(x) = 0.6843(log(x)) - 3.7681
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                 female   R-squared:                       0.216
Model:                            OLS   Adj. R-squared:                  0.210
Method:                 Least Squares   F-statistic:                     39.12
Date:                Fri, 24 Jun 2016   Prob (F-statistic):           4.42e-09
Time:                        14:42:56   Log-Likelihood:                -373.74
No. Observations:                 144   AIC:                             751.5
Df Residuals:                     142   BIC:                             757.4
Df Model:                           1                                         
==============================================================================
                 coef    std err          t      P>|t|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         -3.7681      2.625     -1.435      0.153        -8.958     1.421
x1             0.6843      0.109      6.254      0.000         0.468     0.901
==============================================================================
Omnibus:                        1.228   Durbin-Watson:                   2.119
Prob(Omnibus):                  0.541   Jarque-Bera (JB):                1.326
Skew:                          -0.197   Prob(JB):                        0.515
Kurtosis:                       2.742   Cond. No.                         232.
==============================================================================
"""
