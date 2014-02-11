var data = {}

json_fetch(['sections', 'timeslots', 'rooms', 'schedule_assignments'], function(){
    var window_height = window.innerHeight - 20
    $j("#directory-div").height(window_height);
    $j("#matrix-div").height(window_height);

    s = new Scheduler(data, $j("#directory-div")[0], $j("#matrix-div")[0])
    s.render()
}, 
data)
