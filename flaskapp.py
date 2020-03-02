from flask import Flask, render_template, jsonify, redirect, request, session, flash
import logging #allow loggings
import time, sys, json
import yourrobot #import in your own robot functionality
from interfaces.databaseinterface import DatabaseHelper
from datetime import datetime

#Create the database
database = DatabaseHelper('test.sqlite')

#Create Robot first. It take 4 seconds to initialise the robot, sensor view wont work until robot is created...
robot = yourrobot.Robot()
if robot.get_battery() < 6: #the robot motors will disable at 6 volts
    robot.safe_exit()

#Global Variables
app = Flask(__name__)
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS
robot.set_log(app.logger) #set the logger inside the robot
database.set_log(app.logger) #set the logger inside the database
POWER = 30 #constant power/speed

#Request Handlers ---------------------------------------------
#home page and login
@app.route('/', methods=['GET','POST'])
def index():
    if 'userid' in session:
        return redirect('./missioncontrol') #no form data is carried across using 'dot/'
    if request.method == "POST":  #if form data has been sent
        email = request.form['email']   #get the form field with the name 
        password = request.form['password']
        # TODO - need to make sure only one user is able to login at a time...
        userdetails = database.ViewQueryHelper("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        if len(userdetails) != 0:  #rows have been found
            row = userdetails[0] #userdetails is a list of dictionaries
            session['userid'] = row['userid']
            session['username'] = row['username']
            session['permission'] = row['permission']
            return redirect('./missioncontrol')
        else:
            flash("Sorry no user found, password or username incorrect")
    else:
        flash("No data submitted")
    return render_template('index.html')

#home page
@app.route('/missioncontrol')
def missioncontrol():
    if robot == None: #make sure robot is
        return redirect('./')
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    results = None
    return render_template("missioncontrol.html", data = results, voltage = robot.get_battery())

#dashboard
@app.route('/sensorview', methods=['GET','POST'])
def sensorview():
    if robot == None: #make sure robot is
        return redirect('./')
    if 'userid' not in session:
        return redirect('./')
    return render_template("sensorview.html")

#get all stats and return through JSON
@app.route('/getallstats', methods=['GET','POST'])
def getallstats():
    results = robot.get_all_sensors()
    return jsonify(results)

#map or table of fire and path data
@app.route('/map')
def map():
    if robot == None: #make sure robot is
        return redirect('./')
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    results = None
    return render_template('map.html', results=results)

#start robot moving
@app.route('/start', methods=['GET','POST'])
def start():
    robot.CurrentCommand = "start"
    duration = None
    while (robot.CurrentCommand != "stop"):
        duration = robot.move_power_untildistanceto(POWER,20)
    return jsonify({ "message":"starting", "duration":duration }) #jsonify take any type and makes a JSON 

#creates a route to get all the event data
@app.route('/getallusers', methods=['GET','POST'])
def getallusers():
    results = database.ViewQueryHelper("SELECT * FROM users")
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row

#Get the current command
@app.route('/getcurrentcommand', methods=['GET','POST'])
def getcurrentcommand():
    return jsonify({"currentcommand":robot.CurrentCommand})

#Start callibration of the IMU sensor
@app.route('/getcalibration', methods=['GET','POST'])
def getcalibration():
    calibration = "Not Calibrated"
    if robot.calibrate_imu():
        calibration = "Calibrated"
    return jsonify({"calibration":calibration})

#Stop current process
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

#Log a message
def log(message):
    app.logger.info(message)
    return

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..
