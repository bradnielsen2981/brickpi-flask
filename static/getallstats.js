var recurringhandle = null;  //can be used to delete recurring function if you want
recurringhandle = setInterval(get_all_stats, 1000);


//THis recurring function gets data using JSON
function get_all_stats() {
    JSONrequest('/getallstats','POST', draw_stats); //Once data is received it is passed to the drawchart function
}

//with received json data, draw the chart using tempate literals ${results.battery}
//results contains all the variables: battery, compass etc
function draw_stats(results) {
    document.getElementById('sbattery').innerHTML = String(results.battery);
    document.getElementById('scolour').innerHTML = String(results.colour);
    document.getElementById('sultrasonic').innerHTML = String(results.ultrasonic);
    document.getElementById('sthermal').innerHTML = String(results.thermal);
    document.getElementById('sacceleration').innerHTML =String(results.acceleration);
    document.getElementById('scompass').innerHTML = String(results.scompass);
    document.getElementById('sgyro').innerHTML = String(results.sgyro);
    document.getElementById('stemperature').innerHTML = String(results.temperature);
    document.getElementById('sorientation').innerHTML = String(results.orientation);
}
