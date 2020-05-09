
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
  return('<h1>THIS WORKS YO</h1>')

if __name__ == '__main__':
  app.run()

from flask import Flask
from flask import render_template
from flask import request
import pymongo
import json
import string
from bson import ObjectId
import random #ONLY USED FOR PLACEHOLDER DECISION ALGORITHM

app = Flask(__name__)
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")

db = mongoClient['databaseUno']
users = db['users']
confimationCodes = db['confimationCodes']

'''
CMD: 
  > set FLASK_APP = app.py
  > python -m flask run
'''

def decisionAlgorithm(location, date, entryTime, exitTime, groupSize):
  print('Params: %s, %s, %s, %s, %s'%(location, date, entryTime, exitTime, groupSize))
  return(random.uniform(0,1) > 0.5)

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
  #print('Number: ', number)
  #print('Password: ', password)

  #print('DATABASE:')
  #for user in users.find():
  #    print(user['name'], user['number'], user['password'])

  for user in users.find({'number': number, 'password': password}):
    #print('USER FOUND: ', end='')
    #print(user)
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
  history = {} #EXTRA - WE CAN STORE HISTORY OF REQUESTS AND DECISIONS FOR EACH PERSON
  userData = {'name': name, 'number':number, 'password':password, 'history':history}
  users.insert_one(userData)
  print('REGISTERED NEW USER')
  #print('DATABASE:')
  #for user in users.find():
  #    print(user['name'], user['number'], user['password'])

  return('{"error":"False"}')

@app.route('/booking', methods = ['POST'])
def booking():
  number = request.form['number']
  location = request.form['location']
  date = request.form['Date']
  entryTime = request.form['Entry Time']
  exitTime = request.form['Exit Time']
  groupSize = request.form['Group Size']
  decision = decisionAlgorithm(location, date, entryTime, exitTime, groupSize)

  print('THE DECISION IS: %s'%(decision))

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