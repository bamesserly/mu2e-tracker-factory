/* [Panel Dimensions] */
outer_radius = 810;
inner_radius = 700;
panel_thickness = 24.347;
straw_inner = 380;
straw_outer = 680;
longest_straw = 1179;
straw_thickness = 10.41;
clearance = 2;

silver = [192,192,192]/255;
white = [1,1,1];
black = [0,0,0];

panel_angle = 120;

/* [Derived Quantities] */
panel_width = outer_radius-inner_radius*sin((180-panel_angle)/2);
panel_length = outer_radius*sin(panel_angle/2)*2;
echo("Panel width",panel_width);
echo("Panel length",panel_length);

inches = 25.4;




module wedge(angle, extent=100, height=100, center=true)
  {
    module wedge_wall()
    {
      translate([0,0,(center==true ? -height/2 : 0)])
        cube([extent,0.1,height]);
    }
    
    for(r=[0:45:angle-45-1])
    {
        hull()
        {
          rotate([0,0,r]) wedge_wall(); 
          rotate([0,0,min(angle,r+45)]) wedge_wall();
        }
    }
    hull()
    {
      rotate([0,0,max(0,angle-45)]) wedge_wall();
      rotate([0,0,angle]) wedge_wall();
    }
  }

module panel_arc(thickness = panel_thickness, angle = panel_angle, center)
{
    shift = center ? [-outer_radius+panel_width/2,0,0] : [0,0,0];
    translate(shift)
    // Panel aluminium structure.
    color("Silver")
    rotate([0,0,angle/2])
    difference()
    {
        difference()
        {
            cylinder(r=outer_radius,h=thickness,center=true);
            cylinder(r=inner_radius,h=thickness*2+1,center=true);
        }
        wedge(360-angle,outer_radius*10,thickness*2+1,center=true);
    }
}

module panel(center)
{
    shift = center ? [-outer_radius+panel_width/2,0,0] : [0,0,0];
    translate(shift)
    union(){
        // Panel aluminium structure.
        difference()
        {
            color("Silver")
            rotate([0,0,60])
            difference()
            {
                difference()
                {
                    cylinder(r=outer_radius,h=panel_thickness,center=true);
                    cylinder(r=inner_radius,h=panel_thickness*2+1,center=true);
                }
                wedge(360-panel_angle,outer_radius*10,  panel_thickness*2+1,center=true);
            }
            
            translate([0,0,2000/2])
            cube([2000,2000,2000],center=true);
        }
        // Panel straw volume.
        intersection()
        {
            straw_width = straw_outer-straw_inner;
            translate([straw_inner+straw_width/2,0,0])
            {
                cube([straw_width, longest_straw, straw_thickness],center=true);
            }
            cylinder(r=inner_radius,h=panel_thickness,center=true);
        }
    }
}

$fa = 1;
inches = 25.4;

delta = 3.125;
x0 = 382.5;
label_radius = 712.70;
function y(x) = sqrt(label_radius*label_radius - x*x);
function xi(i) = x0+i*delta;
//function yi(i) = 380+2.5+i*delta;

function mystr(i) = ( i < 10 ? str(0,i) : str(i));

//projection()
//panel(center=false);
color(black)
rotate([0,0,60])
{
    
    difference()
    {
        union()
        {
        difference()
    {
        circle(r = 810);
        circle(r = 797.3);
    }
    difference()
    {
        circle(r = 712.70);
        circle(r = 700);
    }}
    projection()
    wedge(360-panel_angle,outer_radius*10,  panel_thickness*2+1,center=true);
}
}


for(i = [0:95])
{
    x = xi(i);
    for(j = [-1,1])
    {
    translate([x,j*(y(x)+20),0])
    {
        myalign = ( j == 1 ? "left" : "right");
        translate([0,-1*j*10,0])
        square([0.1,20],center=true);
        rotate([0,0,90])
        text(mystr(i),font="PT Mono",size = 2,valign = "center", halign = myalign);
    }
}
}