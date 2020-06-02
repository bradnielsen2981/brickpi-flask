#Importing libraries
from flask import Flask, render_template, jsonify, redirect, request, session, flash
import logging #allow loggings
import time, sys, json
import yourrobot #import in your own robot functionality
from interfaces.databaseinterface import DatabaseHelper
from datetime import datetime

ROBOTENABLED = True #this can be used to disable the robot and still edit the webserver
POWER = 30 #constant power/speed
TPOWER = 20 #constant turning power

#Global Variables
app = Flask(__name__)
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS

#Create the Database
database = DatabaseHelper('test.sqlite')
database.set_log(app.logger) #set the logger inside the database

#Create the Robot
robot = None
if ROBOTENABLED:
    #Create Robot first. It take 4 seconds to initialise the robot, sensor view wont work until robot is created...
    robot = yourrobot.Robot()
    robot.set_log(app.logger) #set the logger inside the robot
    if robot.get_battery() < 6: #the robot motors will disable at 6 volts
        robot.safe_exit()
        ROBOTENABLED = False
    else:
        ROBOTENABLED = robot.Configured #if the robot didnt load disable robot, otherwise Robot is enabled
        robot.set_database(database) #store a handle to the database inside the robot






#-----------------HTML REQUEST HANDLERS----------------------------------#



#---Page Request Handlers---#

@app.route('/', methods=['GET','POST']) #home page and login
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


@app.route('/missioncontrol') #mission control
def missioncontrol():
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    voltage = None
    if ROBOTENABLED:
        voltage = robot.get_battery()
    return render_template("missioncontrol.html", configured = ROBOTENABLED, voltage = voltage)


@app.route('/missionhistory') #map or table of fire and path data
def missionhistory():
    if 'userid' not in session:
        return redirect('./') #no form data is carried across using 'dot/'
    results = None
    if ROBOTENABLED: #make sure robot is
        pass
    return render_template('missionhistory.html', results=results, configured = ROBOTENABLED)


@app.route('/sensorview', methods=['GET','POST'])#sensor view
def sensorview():
    if 'userid' not in session:
        return redirect('./')
    if ROBOTENABLED: #make sure robot is
        pass
    return render_template("sensorview.html", configured = ROBOTENABLED)
 


#-------------END HTML REQUEST HANDLERS----------------------------------#






#----------------JSON REQUEST HANDLERS--------------------#



#--Sensor Handlers--#

@app.route('/getallstats', methods=['GET','POST'])#get all stats and return through JSON
def getallstats():
    results=None
    if ROBOTENABLED: #make sure robot is
        results = robot.get_all_sensors()
    return jsonify(results)


@app.route('/getcalibration', methods=['GET','POST'])#Start callibration of the IMU sensor
def getcalibration():
    calibration = None
    if ROBOTENABLED:
        if not robot.Calibrated:
            calibration = robot.calibrate_imu()
    return jsonify({"calibration":calibration})


@app.route('/reconfigIMU', methods=['GET','POST'])#Reconfigure IMU sensor
def reconfigIMU():
    if ROBOTENABLED:
        robot.reconfig_IMU()
    return jsonify({"message":"reconfiguring_IMU"})



#--Actuator Handlers--#

#Traversal handlers
'''
@app.route('/foward', methods=['GET','POST'])#Moves robot foward
def forward(var,var_limit):
    message = ''
    if ROBOTENABLED:
        robot.move_power(POWER,-0.5) #use a second number if you need to correct a deviation
        database.ModifyQueryHelper('INSERT INTO blah blah blah', (Pram1,Pram1,Pram1)) #Database Entry
    return


@app.route('/backwards', methods=['GET','POST'])#Moves robot backwards
def backwards(var,var_limit):
    message =''
    if ROBOTENABLED:
        robot.move_power(-POWER,0.5)
    return


@app.route('/t.right', methods=['GET','POST'])#Rotates robot right
def t.right():
    message =''
    if ROBOTENABLED:
        robot.rotate_power(TPOWER)
    return jsonify({"message"=message})


@app.route('/t.left', methods=['GET','POST'])#Rotates robot left
def t.left():
    message = ''
    if ROBOTENABLED:
        robot.rotate_power(-1*TPOWER)
    Return jsonify({"message"=message})
'''


#Complex movement
@app.route('/right', methods=['GET','POST'])#Rotates 90degrees right
def right():
    if ROBOTENABLED:
        robot.rotate_power_degrees_IMU(TPOWER, 90)
        message = "90 Degree Right Turn"
        return jsonify({"message":message})


@app.route('/left', methods=['GET','POST'])#Rotates 90 degrees left
def left():
    if ROBOTENABLED:
        robot.rotate_power_degrees_IMU(TPOWER, -90)
        message = "90 Degree Left Turn"
        return jsonify({"message"=message})


@app.route('/turnaround', methods=['GET','POST'])#Rotates robot 180 degrees, turning robot around
def turnaround():
    if ROBOTENABLED:
        robot.rotate_power_degrees_IMU(TPOWER, 180)
        message = "180 Degree Turn Around"
        return jsonify({"message"=message})


@app.route('/reverse', methods=['GET','POST'])#Rotates robot 180 degrees, keeps moving until wall detected
def reverse():
    collisiondata = None
    if ROBOTENABLED: #make sure robot is
        robot.rotate_power_degrees_IMU(TPOWER, 180)
        #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime} 
        collisiondata = move_power_time(-POWER,2,0.5) #reverse
    return jsonify({ "message":"collision detected", "collisiondata":collisiondata }) #jsonify take any type and makes a JSON


#Claw Handlers
'''
@app.route('/claw.open', methods=['GET','POST'])#Opens robot claw
def claw.open():
    message = ''
    if ROBOTENABLED:
        robot.__move_claw_targetdegrees(#put in degrees needed#)
    return jsonify({"message":message})


@app.route('claw.close', methods=['GET','POST'])#Closes claw
def claw.close():
    message = ''
    if ROBOTENABLED:
        robot.__move_claw_targetdegrees(#put in degrees needed#)
    return jsonify({"message": message})
'''


#--Database Handlers--#

'''
#Insert Handlers
@app.route('/newdata', methods=['GET','POST'])#New database entry, modular handler allowing specified entry to specfied table
def newdata():

#Select Handlers
@app.route('getdata', methods=['GET','POST'])#Gets data from db, modular handler able to get specified data from specified location
def getdata():

#Modify Handlers
@app.route('modifydata', methods=['GET','POST'])#Modifies data in db, modular handler
def modifydata():

#DeleteHandlers
@app.route('deletedata', methods=['GET','POST'])#Deletes data from db, modular handler
def deletedata():
'''


@app.route('/getallusers', methods=['GET','POST'])#creates a route to get all the user data
def getallusers():
    results = database.ViewQueryHelper("SELECT * FROM users")
    return jsonify([dict(row) for row in results]) #jsonify doesnt work with an SQLite.Row



#--Miscellaneous Request Handlers--#

@app.route('/getcurrentcommand', methods=['GET','POST'])#Get the current command from brickpiinterface.py
def getcurrentcommand():
    currentcommand = None
    if ROBOTENABLED:
        currentcommand = robot.CurrentCommand    
    return jsonify({"currentcommand":currentcommand})


@app.route('/getcurrentroutine', methods=['GET','POST'])#get the current routine from robot.py
def getcurrentroutine():
    currentroutine= None
    if ROBOTENABLED:
        currentroutine = robot.CurrentRoutine
    return jsonify({"currentroutine":currentroutine})


@app.route('/getconfigured', methods=['GET','POST'])#get the configuration status from brickpiinterface
def getconfigured():
    return jsonify({"configured":ROBOTENABLED})


@app.route('/stop', methods=['GET','POST'])#Stop current process
def stop():
    if ROBOTENABLED:
        robot.CurrentRoutine = "ready"
        robot.CurrentCommand = "stop"
        robot.stop_all()
    return jsonify({ "message":"Stopping" })


@app.route('/shutdown', methods=['GET','POST'])#Shutdown the web server
def shutdown():
    if ROBOTENABLED:
        robot.safe_exit()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({ "message":"shutting down" })


@app.route('/defaultdatahandler', methods=['GET','POST'])#An example of how to receive data from a JSON object
def defaultdatahandler():
    if request.method == 'POST':
        var1 = request.form.get('var1')
        var2 = request.form.get('var2')
    return jsonify({"message":"just an example"})



#------------END JSON REQUEST HANDLERS--------------------#



#Log a message
def log(message):
    app.logger.info(message)
    return

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..
