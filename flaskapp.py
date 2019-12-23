from flask import Flask, render_template, jsonify, request
import logging #allow loggings
import grove
import brickpirobot #imports the grove functionality that you define
from datetime import datetime

#Global Variables
app = Flask(__name__)
log = app.logger #sets up a log 
#log.info('message') -- use this to log a message
#log.error("Testing") --use this to log an error

#request handlers ---------------------------------------------
@app.route('/')
def home():
    return render_template("index.html")

#start a light
@app.route('/start', methods=['GET','POST'])
def start():
    return jsonify({ "message":"starting" }) #jsonify take any type and makes a JSON 

#stop a light
@app.route('/stop', methods=['GET','POST'])
def stop():
    return jsonify({ "message":"stopping" }) 

#Get temperature calues
@app.route('/gettemphumidity', methods=['GET','POST'])
def gettemphumidity():
    [temp,humidity] = grove.read_temp_humidity_sensor_digitalport(7) #get temperature and humidity by separating out the value list returned into two variables
    return jsonify({ "Temperature":temp, "Humidity":humidity })

#Shutdown the web server
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({ "message":"shutting down" }) 

#---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

#Threaded mode is important if using shared resources e.g. sensor, each user request launches a thread.. However, with Threaded Mode on errors can occur if resources are not locked down e.g trying to access live readings - conflicts can occur due to processor lock. Use carefully..