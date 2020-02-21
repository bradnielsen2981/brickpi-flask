var recurringhandle = null;  //can be used to delete recurring function if you want
recurringhandle = setInterval(get_all_stats, 3000);


//THis recurring function gets data using JSON
function get_all_stats() {
    JSONrequest('/getallstats','POST', draw_stats); //Once data is received it is passed to the drawchart function
}

//with received json data, draw the chart
function draw_stats(results) {
    console.log(results);
}