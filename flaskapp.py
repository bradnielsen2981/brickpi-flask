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
DEVIATION = -0.5 #value accounting for motor deviations
DISTANCETO = 20 #Stopping distance
MOF = 2 #Turning margin of error

#Server intialize
app = Flask(__name__)
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS

#Connect to database
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
    #Local variables
    state = "login"

    #if user is already logged in (userid in session), redirected to missioncontrol
    '''if 'userid' in session:
        return redirect('./missioncontrol') #no form data is carried across using 'dot/'
    '''
    #post methods, mainly for forms
    if request.method == "POST":  #if form data has been sent
        '''
        #defines status as either login or signup
        if request.form['form-name'] == "login-form":
            status = "login"
        elif request.form['form-name'] == "signup";
            status = "signup"

        #Login form
        #if state == "login": #login form submitted
            '''
            '''
            # TODO - need to make sure only one user is able to login at a time...
            if len(session["userid"]) >= 1:
                message = "System already being controlled, logout and try again."
                return jsonify({"message" = message})
            '''
            '''
            username = request.form['username'] #getting form fields
            password = request.form['password']
            userdetails = database.ViewQueryHelper("SELECT * FROM users WHERE username=? AND password=?",(username,password)) #getting user details
            if len(userdetails) != 0:  #rows have been found where username and password match
                row = userdetails[0] #userdetails is a list of dictionaries
                session['userid'] = row['userid']
            #if have time put in role/permission select statement, put roles into session (cookie) dictionary
            return redirect('./missioncontrol')
        else:
            flash("Sorry no user found, password or username incorrect")
        '''
        '''
        #Signup form
        # if state == "signup": #signup form submitted
            #Local variables
            active = True #activation variable for whether or not data entry committed
            userdetails = get_all_users() #gets all user data
            row = userdetails[0] #sets row as user data

            #processing signup form data fields
            name = request.form['name']
            surname = request.form['surname']
            username = request.form['username']
            password = request.form['password']
            password_confirm = request.form['password_confirm']
            

            #checking if password and password confirmation match
            if password != password_confirm:
                status = False
                return jsonify{"message":message}

            #checking if username/account already taken
            if username == row['username']:
                message = "Username is already taken, please enter a different username."
                status = False
                return jsonify{"message":message}

            #new user database entry/puts in user roles
            if status == True:
                new_user_entry()
                user_role_entry()
            
    else:
        flash("No data submitted")
    '''
    return render_template('home.html')


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

@app.route('/forward', methods=['GET','POST'])#Moves robot foward
def forward():
    message = None    
    if ROBOTENABLED:
        #Local Variables
        distance_start = robot.get_ultra_sensor() #get ultra sensor for starting distance to obstacle
        #results = None #don't need right now
        #process_occurred = False #don't think i need this --> for proofing valid process occurred
        '''
        #Full Manual Control
        if session[control_type] == "manual_control":
            message = 'Manual forward.'
            while True:
                robot.move_power(POWER,DEVIATION) #should move forward until while loop broken, intended to be when arrorws held down, etc
                break
        '''
        '''
        #Auto Action Control --> robot moved forward until variable limit reached
        elif session[control_type] == "auto_control"
            message = 'Auto forward.'
            #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime}
            collisiondata = robot.move_power_untildistanceto(POWER, DISTANCETO, DEVIATION) #robot moves forward until object detected within specified distance
        '''
        ''' database stuff
        distance_traversed = robot.get_traversed_distance(distance_start)
        #if distance_traversed > 1: #checking if distance greater than 1 to account for invalid processes, assumed to be less than 1
            #process_occurred = True
        if process_occurred = True:
            results = robot.get_all_sensors()
            battery = results[battery]
            colour = results[colour]
            tir = results[thermal]
            acceleration = results[acceleration]
            gyro = results[gyro]
            compass = results[compass]
            temperature = results[temperature]
        database.ModifyQueryHelper('INSERT INTO blah blah blah', (Pram1,Pram1,Pram1)) #Database Entry
    '''
        message = 'Auto forward.'
        #collisiondata = {"collisiontype":collisiontype,"elapsedtime":elapsedtime}
        collisiondata = robot.move_power_untildistanceto(POWER, DISTANCETO, DEVIATION) #robot moves forward until object detected within specified distance
    
    else:
        message = 'Robot not enabled.'
    return jsonify({"Message":message, "collision data":collisiondata})


@app.route('/backward', methods=['GET','POST'])#Moves robot backwards
def backwards():
    message = None
    if ROBOTENABLED:
        #Local Variables
        distance_start = robot.get_ultra_sensor()
        '''
        #Full Manual Control
        if session[control_type] == "manual_control":
            message = 'Manual reverse.'
            while True:
                robot.move_power(-POWER,-DEVIATION)
            distance_traversed = robot.get_traversed_distance(distance_start)
        '''
        '''
        #Auto Action Control
        elif session[control_type] == 'auto_control':
            message = 'Turning around.'
            robot.rotate_power_degrees_IMU(TPOWER, 180, MOF)
        '''
        message = 'Auto turning around, 180 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, 180, MOF) #rotates robot 180 degrees, turning around
   
    else:
        message = 'Robot not enabled.'
    return jsonify({"message": message})


@app.route('/t_right', methods=['GET','POST'])#Rotates robot right
def t_right():
    message =''
    if ROBOTENABLED:
        '''
        #Full Manual Control
        if session[control_type] = 'manual_control':
            message = 'Manual right turn.'
            heading_start = robot.get_compass_IMU()
            while True:
                robot.rotate_power(RTPOWER)
            heading_traversed = robot.get_rotated_heading(heading_start)
        '''
        '''
        #Auto Action Control
        elif session[control_type] == 'auto_control':
            message = 'Auto right turn, 90 degrees.'
            robot.rotate_power_degrees_IMU(RTPOWER, 90, MOF)
        '''
        message = 'Auto right turn, 90 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, 90, MOF)

    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})


@app.route('/t_left', methods=['GET','POST'])#Rotates robot left
def t_left():
    message = ''
    if ROBOTENABLED:
        '''
        #Full Manual Control
        if session[control_type] == 'manual_control':
            message = 'Manual left turn.'
            heading_start = robot.get_compass_IMU()
            while True:
                robot.rotate_power(LTPOWER)
            heading_traversed = robot.get_rotated_heading(heading_start)
        '''
        '''
        #Auto Control
        elif session[control_type] == 'auto_control':
            message = 'Auto left turn, -90 degrees.'
            robot.rotate_power_degrees_IMU(LTPOWER, -90, MOF)
        '''
        message = 'Auto left turn, -90 degrees.'
        robot.rotate_power_degrees_IMU(TPOWER, -90, MOF)

    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})


#Claw Handlers

@app.route('/claw_open', methods=['GET','POST'])#Opens robot claw
def claw_open():
    message = ''
    if ROBOTENABLED:
        robot.open_claw()
        message = 'Claw opening.'
    else:
        message = 'Robot not enabled.'
    return jsonify({"message": message})


@app.route('/claw_close', methods=['GET','POST'])#Closes claw
def claw_close():
    message = ''
    if ROBOTENABLED:
        robot.close_claw()
        message = 'Close claw.'
    else:
        message = 'Robot not enabled.'
    return jsonify({"message":message})



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
