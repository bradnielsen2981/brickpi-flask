var recurringhandle = null;  //can be used to delete recurring function if you want
recurringhandle = setInterval(get_map_data, 3000);

//THis recurring function gets data using JSON
function get_map_data() {
    JSONrequest('/getevents','POST', draw_map); //Once data is received it is passed to the drawchart function
}

//with received json data, draw the chart
function draw_map(results) {
    //set drawing and origin of canvas
    results.forEach(draw_event);
}

//draw a specific event
function draw_event(eventobj, index, array) {
    console.log(eventobj.eventtype);
}
