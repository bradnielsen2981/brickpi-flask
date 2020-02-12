from flask import Flask, render_template, jsonify, request
import logging #allow loggings
import time, sys, json
import brickpiinterface #imports the grove functionality that you define
from databaseinterface import DatabaseHelper
from datetime import datetime

#Global Variables
app = Flask(__name__)
log = app.logger #sets up a log (log.info('message') or log.error('Testing'))
robot = brickpiinterface.Robot()
POWER = 30 #constant power/speed
if robot.get_battery() < 6:
    sys.exit()
database = DatabaseHelper('firefighting.sqlite')
CurrentCommand = "none"


#request handlers ---------------------------------------------
@app.route('/')
def home():
    results = None
    return render_template("index.html", data = None, voltage = robot.get_battery())

@app.route('/map')
def map():
    return render_template('map.html')

#start path finding
@app.route('/start', methods=['GET','POST'])
def start():
    robot.CurrentCommand = "start"
    return jsonify({ "message":"starting" }) #jsonify take any type and makes a JSON 

#demonstrates how to get all the data from an SQLITE database
@app.route('/getdata', methods=['GET','POST'])
def getdata():
    results = database.ViewQueryHelper("SELECT * FROM ???")
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row Object

#returns what the robot is currently doing
@app.route('/getcurrentcommand', methods=['GET','POST'])
def getcurrentcommand():
    return jsonify({"currentcommand":robot.CurrentCommand})

#stop robot
@app.route('/stop', methods=['GET','POST'])
def stop():
    robot.CurrentCommand = "stop"
    robot.stop_all()
    return jsonify({ "message":"stopping" })

#Get temperature calues
@app.route('/gettemphumidity', methods=['GET','POST'])
def gettemphumidity():
    temp = None; humidity = None
    return jsonify({ "Temperature":temp, "Humidity":humidity })

#Shutdown the web server
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    robot.safe_exit()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({ "message":"shutting down" }) 

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..