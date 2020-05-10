from flask import Flask
from flask import render_template
from flask import request
import pymongo
import json
import string
from bson import ObjectId
import random

#LOGGING
import os
import sys
import logging
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

#DATA MANIPULATION
import pandas as pd
from datetime import datetime

#FOR LOCAL DB
#MONGO_URL = os.environ.get('MONGO_URL')
#if(not MONGO_URL):
#  MONGO_URL = "mongodb://localhost:27017/rest";

#FOR HEROKU DB
MONGO_URL = 'mongodb://user:password1234@ds139920.mlab.com:39920/heroku_1d254xtv?retryWrites=false'
app.config['MONGO_URI'] = MONGO_URL
mongoClient = pymongo.MongoClient(MONGO_URL)

db = mongoClient['heroku_1d254xtv']
users = db['users']
confimationCodes = db['confimationCodes']

#READING THE PREPROCESSED CSVs
#we use skip to reduce the server load due to the restrictions on file size on heroku and github.
#However we have used the entire data set in our colab notebook to run the algorithm.
skip = 50 #DEFINED FOR OPTI FILES
print('Reading CSV for 2017')
df_2017 = pd.read_csv('data/2017opti.csv')
print('Reading CSV for 2018')
df_2018 = pd.read_csv('data/2018opti.csv')
print('Reading CSV for 2019')
df_2019 = pd.read_csv('data/2019opti.csv')

dataframe_dict = {2017:df_2017, 2018:df_2018, 2019:df_2019}
#dataframe_dict = {2017: df_2017}

df_grouped_dict = {}
for year in dataframe_dict:
  print('Processing Year: ', year)
  df = dataframe_dict[year]
  df_location_grouped = df.groupby(['DOLocationID', 'DateTime']).sum()
  df_grouped_dict[year] = df_location_grouped

'''
CMD: 
  > set FLASK_APP = app.py
  > python -m flask run
'''
# We calculate the total no.of people present at the requested location in the same time duration in the previous three years.
# **Calculate the mean over the three years and divide it by 3 to follow the guidelines provided by CDC of maintaining a workforce of 33% in public places** 
# This would be the threshold of that location for the current datetime.
# If the current population of the location retrived from the database +the number of people in the request exceeds the threshold we would deny the request 
# Else we will allow the user to enter the location by sending a QR code to the user. Update the current population.
def decisionAlgorithm(location, date, entryTime, exitTime, groupSize):
  print('Decision Params: %s, %s, %s, %s, %s'%(location, date, entryTime, exitTime, groupSize))
  sTime = date + ' ' + entryTime + ':00'
  eTime = date + ' ' + exitTime + ':00'
  s = datetime.strptime(sTime, '%Y-%m-%d %H:%M:%S')
  e = datetime.strptime(eTime, '%Y-%m-%d %H:%M:%S')
  now = datetime.now()
  if(s > e or s < now):
    print('Invalid time range given')
    return(False)

  bookingCount = 0
  for user in users.find({}):
    if('history' in user and 'bookings' in user['history']):
      for booking in user['history']['bookings']:
        t = booking['Date'] + ' ' + booking['Entry Time']
        t = datetime.strptime(t, '%Y-%m-%d %H:%M')
        if(t > s and t < e):
          bookingCount += 1

  new_df_list=pd.DataFrame()
  total_count = 0
  previous_year = -1

  for year in df_grouped_dict:
    df = df_grouped_dict[year]
    df = df.reset_index()

    df['DateTime'] = pd.to_datetime(df['DateTime'])
    '''
    if previous_year != -1:
      sTime = sTime.replace(str(previous_year), str(year))
      eTime = eTime.replace(str(previous_year), str(year))
    '''
    sTime = sTime.replace(str('2020'), str(year))
    eTime = eTime.replace(str('2020'), str(year))

    mask = (df['DateTime'] >= sTime) & (df['DateTime'] < eTime)
    df = df.loc[mask]
    new_df_list.append(df)
    total_count = total_count+df.size
    previous_year = year
    
  no_of_years = len(df_grouped_dict.keys())
  mean_passenger_count = total_count/no_of_years
  threshold = int(mean_passenger_count/3) * (skip)
  print("threshhold is        --> "+str(threshold))
  print("cout at location is  --> "+str(bookingCount))
  
  decision = threshold >= bookingCount + int(groupSize)
  return(decision)

#Return confirmation message to the user
def generateConfirmation():
  chars = string.ascii_letters + string.digits
  while(True):
    confirmationCode = '' 
    for i in range(12):
      confirmationCode += random.choice(chars)

    flag = True
    for user in users.find():
      if('bookings' in user['history']):
        for booking in user['history']['bookings']:
          if('QRCode' in booking):
            if(confirmationCode == booking['QRCode']):
              flag = False
    if(flag):
      return(confirmationCode)


@app.route('/', methods = ['GET', 'POST'])
def start():
  if(request.method == 'POST'):
    pass
  else:
    return(render_template('index.html'))

@app.route('/login', methods = ['POST'])
def login():
  number = request.form['number']
  password = request.form['password']
  for user in users.find({'number': number, 'password': password}):
    response = {"error":"False"}
    response['data'] = {}
    response['data']['name'] = user['name']
    response['data']['number'] = user['number']
    response['data']['history'] = user['history']
    responseStr = json.dumps(response)
    return(responseStr)

  return('{"error": "The credentials are incorrect"}')

@app.route('/register', methods = ['POST'])
def register():
  name = request.form['name']
  number = request.form['number']
  password = request.form['password']
  history = {} #EXTRA - WE STORE THE HISTORY OF REQUESTS AND DECISIONS FOR EACH PERSON
  userData = {'name': name, 'number':number, 'password':password, 'history':history}

  users.insert_one(userData)
  
  for user in users.find({'number': number, 'password': password}):
    response = {"error":"False"}
    response['data'] = {}
    response['data']['name'] = user['name']
    response['data']['number'] = user['number']
    response['data']['history'] = user['history']
    responseStr = json.dumps(response)
    return(responseStr)

  return('{"error": "The credentials are incorrect"}')

@app.route('/booking', methods = ['POST'])
def booking():
  number = request.form['number']
  location = request.form['location']
  date = request.form['Date']
  entryTime = request.form['Entry Time']
  exitTime = request.form['Exit Time']
  groupSize = request.form['Group Size']
  decision = decisionAlgorithm(location, date, entryTime, exitTime, groupSize)

  for user in users.find({'number': number}):
    #print('USER FOUND: ', end='')
    #print(user)

    newDoc = user
    if('bookings' not in newDoc['history']):
      newDoc['history']['bookings'] = []

    booking = {}
    booking['number'] = number
    booking['location'] = location
    booking['Date'] = date
    booking['Entry Time'] = entryTime
    booking['Exit Time'] = exitTime
    booking['Group Size'] = groupSize
    booking['Decision'] = decision
    if(decision):
      booking['QRCode'] = generateConfirmation()
    newDoc['history']['bookings'].append(booking)

    #print('DATABASE:')
    #for user in users.find():
    #  print(user['name'], user['number'], user['password'], user['history'])

    db['users'].update({'number': number}, newDoc, upsert = False)

    #print('DATABASE AFTER UPDATE:')
    #for user in users.find():
    #  print(user['name'], user['number'], user['password'], user['history'])

    if(decision):
      response = {"error":"False"}
    else:
      response = {"error":"Booking Rejected. Please try for another time slot or location."}

    response['data'] = {}
    response['data']['name'] = newDoc['name']
    response['data']['number'] = newDoc['number']
    response['data']['history'] = newDoc['history']
    responseStr = json.dumps(response)

    return(responseStr)
  return('{"error": "The user phone number does not exist in our database."}')

if __name__ == '__main__':
  app.run()
