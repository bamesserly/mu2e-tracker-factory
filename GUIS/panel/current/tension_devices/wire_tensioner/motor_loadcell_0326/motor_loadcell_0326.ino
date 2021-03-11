#include "HX711.h"
#include "Portecap.h"

#define loadDAT 7  //data
#define loadCLK 6  //clock

#define ref_mass_50 49.9495     // 50 gram reference mass
#define ref_mass_100 100.095    // 100 gram reference mass

char user_input;          // used for serial input
float pretension=120.0;   // default tension to work harden wire
float tension1=82.0;      // default tension applied to wire after pretensioning
int motor_minimum=72;     // motor minimum position (approx.)
int motor_maximum=4000;   // motor maximum position (approx.)
int set_motor;            // used for storing motor position 
int tare50 = 1;           // default tare with 50g mass, set tare50 to "0" for tare at 0g

HX711 scale(loadDAT, loadCLK);
float calib_factor = 9640.0;  // default load cell calibration factor 
long tension; 
HX711 load_cell;
Portecap motor;

void setup() {
  motor.Reset();
  Serial.begin(9600); 
  load_cell.begin(loadDAT, loadCLK);
  load_cell.set_scale(calib_factor);
  load_cell.tare();
}

void loop() {
  static char cmd = 0;
  const int Steps = 1;
  while (Serial.available()){
    char kbdBuf[100];
    byte len = Serial.readBytesUntil('\n',kbdBuf,sizeof(kbdBuf));
    if (!len)
      display_status();  
    kbdBuf[len]=0; 
    char *pKbd = kbdBuf;
    cmd = *pKbd;  // command character
    pKbd++;
    short val = atoi(pKbd);
    float set_tension = tension1;
    
    switch (cmd){
      case 'p':   // work harden wire with pretension cycle(s)
        if (val != 0)pretension=val;   // override default tension if value is specified
        for (int i=1; i--;){ 
          motor.Power(1);
          motor.SetDir("PULL");
          motor.SetStep(1);
          while ((load_cell.get_units()+tare50*ref_mass_50)<(pretension-2.0) && motor.Position()<motor_maximum){
            motor.Step((pretension-(load_cell.get_units()+tare50*ref_mass_50))/4); // four steps to get to approx. tension
          }
          //display_status(); // custom display status so GUI can record pretension value - see below
          while ((load_cell.get_units()+tare50*ref_mass_50)<pretension && motor.Position()<motor_maximum){
            motor.SetStep(4);
            motor.Step(1);
          }
          //display_status(); // custom display status so GUI can record pretension value
          Serial.print(motor.Position()+'\t');
          Serial.print('\t');
          Serial.println(load_cell.get_units()+tare50*ref_mass_50, 4);
          delay(10000);
          //motor.Reset();
        }
        break;
      case 't':  // push or pull to set tension
        if (val != 0)set_tension=val; // override default tension if value is specified
        tensionwire(set_tension);
        set_motor = motor.Position();  // save motor position
        break;
      case 'm':  // push or pull to specified motor position
        if (val != 0)set_motor=val; // override default position if value is specified
        motor.Power(1);
        motor.SetStep(1);
        if (set_motor<motor_minimum || set_motor>motor_maximum){
          Serial.println("target motor position out of range");
        }
        else if (motor.Position()>set_motor){
          motor.SetDir("PUSH");
          motor.Step((motor.Position()-set_motor)/8);
          delay(500);  // waiting for motor to move
        }
        else if (motor.Position()<set_motor){
          motor.SetDir("PULL");
          motor.Step((set_motor-motor.Position())/8);
          delay(500);  // waiting for motor to move
        }
        display_status();
        break;
      case '*':
          user_input = 0;
          while (user_input !='Q') {
            display_status();
            for (int i=60; i--; ) {
              user_input = Serial.read();
              if (user_input =='Q')
                break;
              delay(1000);
            }
          }
          Serial.println("End continuous query");
          break;
      case 'r': 
        motor.Reset();
        break;
      case 'z':  // tare load cell [0311: default tare using 50g mass]
        if (val != 0) tare50=0; // override default tare at 50g
        else tare50=1;
        load_cell.tare();
        break;
      case 's':  // set updated calibration factor
        calib_factor = adjust_calib(calib_factor);
        load_cell.set_scale(calib_factor);
        Serial.print("calibration_factor "); 
        Serial.println(calib_factor);
        break;
      case 'c':  // send python the current calibration factor
        Serial.print("calibration_factor "); 
        Serial.println(calib_factor);
        break;
      default:
        break;     
    }
  }
}


void tensionwire(float set_tension){
  if ((load_cell.get_units()+tare50*ref_mass_50)<set_tension){
      motor.Power(1);
      motor.SetDir("PULL");
      motor.SetStep(1);
      while ((load_cell.get_units()+tare50*ref_mass_50)<(set_tension-2.0) && motor.Position()<motor_maximum){
        motor.Step((set_tension-(load_cell.get_units()+tare50*ref_mass_50))/4); // steps to get to approx. tension
      }
      display_status();
      while ((load_cell.get_units()+tare50*ref_mass_50)<set_tension && motor.Position()<motor_maximum){
        motor.SetStep(8);   // get last 2 grams of tension with 1/8th motor steps
        motor.Step(1);
      }
      display_status();
    } 
    else if ((load_cell.get_units()+tare50*ref_mass_50)>set_tension){
      motor.Power(1);
      motor.SetDir("PUSH");
      motor.SetStep(1);
      while ((load_cell.get_units()+tare50*ref_mass_50)>(set_tension+2.0) && motor.Position()>motor_minimum){
        motor.Step(((load_cell.get_units()+tare50*ref_mass_50)-set_tension)/4);
      } 
      display_status();
      while ((load_cell.get_units()+tare50*ref_mass_50)>set_tension && motor.Position()>motor_minimum){
        motor.SetStep(8);
        motor.Step(1);
      }
      display_status();
    }
}

float set_step(float difference) {
  if (abs(difference) > 10.0) {
    return 1000.0;
  }
  else if (abs(difference) > 1.0) {
    return 100.0;
    //return 50.0;
  }
  else if (abs(difference) > 0.1) {
    return 10.0;
  }
  else if (abs(difference) > 0.01) {
    return 1.0;
  }
  else {
    return 0.1;
  }
}


float adjust_calib(float old_calib) {
  int i = 0;
  float new_calib = old_calib;
  load_cell.set_scale(new_calib);
  float step_size;
  float meas = load_cell.get_units();
  //float dif = meas - ref_mass;    // 0109
  float dif = meas - ref_mass_100 + ref_mass_50;  // 0109
  step_size = set_step(dif);
  while (abs(dif) > 0.005) {
    i += 1;
    if (dif > 0.0) {
      new_calib += step_size;
    }
    else {
      new_calib -= step_size;
    }
    load_cell.set_scale(new_calib);
    meas = load_cell.get_units();
    //dif = meas - ref_mass;      // 0109
    dif = meas - ref_mass_100 + ref_mass_50;    // 0109
    //set_step() decides how large of a step to make based on how far off the calibration factor is
    step_size = set_step(dif);
    
    //if we loop through more than 150 times, something is wrong. return the original calibration factor and buzz at the user 3 times
    if (i > 150) {
      Serial.print("Reading ");
      Serial.print(meas, 4);
      Serial.print(" calibration_factor "); 
      Serial.print(new_calib);
      Serial.println(" Mode ERROR");
      return old_calib;
    }
  }
  return new_calib;
}

void display_status(){
  Serial.print(motor.Position());
  Serial.print('\t');
  Serial.println(load_cell.get_units()+tare50*ref_mass_50, 4);
}
