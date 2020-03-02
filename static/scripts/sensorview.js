var recurringhandle = null; //A handle to the recurring function
recurringhandle = setInterval(get_all_stats, 1000); //start pinging the server
var bCalibration = false;

//start calibration
function start_calibration() {
    bCalibration = true;
    clearInterval(recurringhandle);
    document.getElementById('message').innerHTML = "<span class='blinking'>Callibrating</span>";
    JSONrequest('/getcalibration','POST', get_callibration_status); //send callibration request
}

//reconfigure IMU sensor
function reconfigIMU() {
    bCalibration = true;
    clearInterval(recurringhandle);
    document.getElementById('message').innerHTML = "<span class='blinking'>Reconfigure IMU</span>";
    JSONrequest('/reconfigIMU','POST', get_reconfigure_status); //send callibration request
}

//This seems to return far too quickly..
function get_callibration_status(results)
{   
    bCalibration = false;
    recurringhandle = setInterval(get_all_stats, 1000); //restart pinging server
    console.log(results.calibration);
    document.getElementById('message').innerHTML = results.calibration;
}

//This seems to return far too quickly..
function get_reconfigure_status(results)
{   
    bCalibration = false;
    recurringhandle = setInterval(get_all_stats, 1000); //restart pinging server
    console.log(results.reconfigure);
    document.getElementById('message').innerHTML = results.reconfigure;
}

//This recurring function gets data using JSON, note it cant be used while calibration
function get_all_stats() {
    if (bCalibration == false)
    {
        JSONrequest('/getallstats','POST', draw_stats); //Once data is received it is passed to the drawchart function
    }
}

//with received json data, draw the chart using tempate literals ${results.battery}
//results contains all the variables: battery, compass etc
function draw_stats(results) {
    document.getElementById('sbattery').innerHTML = String(results.battery);
    document.getElementById('scolour').innerHTML = String(results.colour);
    document.getElementById('sultrasonic').innerHTML = String(results.ultrasonic);
    document.getElementById('sthermal').innerHTML = String(results.thermal);
    document.getElementById('sacceleration').innerHTML =String(results.acceleration);
    document.getElementById('scompass').innerHTML = String(results.compass);
    document.getElementById('sgyro').innerHTML = String(results.gyro);
    document.getElementById('stemperature').innerHTML = String(results.temperature);
    document.getElementById('sorientation').innerHTML = String(results.orientation);
}
