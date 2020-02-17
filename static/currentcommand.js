// Visualization API with the 'corechart' package.
var recurringhandle = null;  //can be used to delete recurring function if you want
recurringhandle = setInterval(get_current_command, 1000);

//THis recurring function gets data using JSON
function get_current_command() {
    JSONrequest('/getcurrentcommand','POST', writecurrentcommand); //Once data is received it is passed to the writecurrentcommand
}

//with received json data, send to page
function writecurrentcommand(results) {
    document.getElementById('message').innerHTML = results.currentcommand;
}
