from flask import Flask, render_template, jsonify, redirect, request, session, flash
import logging #allow loggings
import time, sys, json
import brickpiinterface #imports the grove functionality that you define
from databaseinterface import DatabaseHelper
from datetime import datetime

#Global Variables
app = Flask(__name__)
SECRET_KEY = 'my random key can be anything'
app.config.from_object(__name__) #Set app configuration using above SETTINGS
log = app.logger #sets up a log (log.info('message') or log.error('Testing'))
robot = brickpiinterface.Robot(app.logger)
POWER = 30 #constant power/speed
if robot.get_battery() < 6:
    robot.safe_exit()
database = DatabaseHelper('test.sqlite')

#Request Handlers ---------------------------------------------
#home page and login
@app.route('/', methods=['GET','POST'])
def index():
    if 'userid' in session:
        return redirect('./home') #no form data is carried across using 'dot/'
    if request.method == "POST":  #if form data has been sent
        email = request.form['email']   #get the form field with the name 
        password = request.form['password']
        userdetails = database.ViewQueryHelper("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        if userdetails[0] != None:  #user exists
            row = userdetails[0] #userdetails is a list of dictionaries
            session['userid'] = row['userid']
            session['username'] = row['username']
            session['permission'] = row['permission']
            return redirect('./home')
        else:
            flash("Sorry no user found, password or username incorrect")
    else:
        flash("No data submitted")
    return render_template('index.html')

#home page
@app.route('/home')
def home():
    results = None
    return render_template("home.html", data = results, voltage = robot.get_battery())

#dashboard
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

#get all stats and return through JSON
@app.route('/getallstats', methods=['GET','POST'])
def getallstats():
    stats = robot.get_all_sensors()
    return jsonify(stats)

#map or table of fire and path data
@app.route('/map')
def map():
    results = None
    return render_template('map.html')

#start path finding
@app.route('/start', methods=['GET','POST'])
def start():
    robot.CurrentCommand = "start"
    duration = None
    while (robot.CurrentCommand != "stop"):
        duration = robot.move_power_untildistanceto(POWER,10)
    return jsonify({ "message":"starting", "duration":duration }) #jsonify take any type and makes a JSON 

#creates a route to get all the event data
@app.route('/getallusers', methods=['GET','POST'])
def getallusers():
    results = database.ViewQueryHelper("SELECT * FROM users")
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row

#returns what the robot is currently doing
@app.route('/getcurrentcommand', methods=['GET','POST'])
def getcurrentcommand():
    return jsonify({"currentcommand":robot.CurrentCommand})

#stop current process
@app.route('/stop', methods=['GET','POST'])
def stop():
    robot.stop_all()
    return jsonify({ "message":"stopping" })

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
