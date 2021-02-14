$fn = 100; 

module display_cut(){
    width = 72;
    height = 25;
    depth = 7;
    translate([-width/2, -height/2, 0]) cube([width, height, depth]);

    border = 8;
    top_width = width + 2*border;
    top_height = height + 2*border;
    top_thick = 10;
    translate([-top_width/2, -top_height/2, depth]) cube([top_width, top_height, top_thick]);

    step = 5;
    step_width = width-4;
    step_height = height-4;
    translate([-top_width/2, -step_height/2, step]) cube([top_width, step_height, top_thick]);
    translate([-step_width/2, -top_height/2, step]) cube([step_width, top_height, top_thick]);
}

module reader_dent(){
    width = 60 + 1;
    height = 40 + 1;
    depth = 1.6;
    pin_depth = 4;
    pin_width = 11;
    translate([-width/2, -height/2, -depth]) cube([width, height, depth]);
    translate([-width/2, -height/2, -pin_depth]) cube([pin_width, height, pin_depth]);
    translate([width/2-pin_width, -height/2, -pin_depth]) cube([pin_width, height, pin_depth]);
}

module case_front()
{
    wall = 8;
    inner_width = 110;
    width = inner_width + 2*wall;
    inner_height = 100;
    height = inner_height + 2*wall;
    depth = 60;
    
    difference(){
        translate([-width/2, -height/2, 0]) cube([width, height, depth]);
        translate([-inner_width/2, -inner_height/2, wall]) cube([inner_width, inner_height, depth-wall+0.01]);
        translate([0, 26, -0.01]) display_cut();
        translate([0, -20, 8.01]) reader_dent();
    }
}

case_front();

/*
difference(){
    translate([-40, -75, 0]) cube([80, 150, 30]);
    translate([-32, -67, 8]) cube([64, 134, 23]);
    translate([-25, 40, -1]) cube([50, 15, 10]);
    translate([-30, 38, 5]) cube([60, 19, 5]);
}

*/
