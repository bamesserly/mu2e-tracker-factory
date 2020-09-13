#include <Adafruit_MAX31865.h>
#include "FastPwm.h"  // Fast PWM output to pins 13 and 10
#include <avr/wdt.h>

// RTD 
#define RREF      430.0  
#define RNOMINAL_PTCO2 100.0 // nominal PT100 RTD resistance at 0C
#define RNOMINAL_PTCO 100.0  
// MAX31865 amplifier pins CS,SD1,SD0,CLK
Adafruit_MAX31865 maxamp = Adafruit_MAX31865(4, 3, 2, 5);  // PTCO
Adafruit_MAX31865 maxamp2 = Adafruit_MAX31865(9, 8, 7, 6);  // PTCO2

// temperature settings PAAS-A / PAAS-B / PAAS-C
float setpointA = 55.0; // [degrees C]
float setpointB = 43.6;
float setpointC = 50.0; 
int valA=255;
int valB=255;
float Pa=5.0;  
float Pb=5.0;  
float tempA;
float temp2;
float usrsp;  // [0724] user choice setpoint temperature 

float setpoint2;  
char paas2='x'; // placeholder for user input
const int32_t wait = 8; // time between data points [seconds]
const int32_t holdtime = 300; // [minutes] time to hold temperature at setpoint
int32_t holdstart;
uint8_t state=0;

void setup() {
  Serial.begin(2000000);
  // don't wait indefinitely for serial, which would prevent WDT reset
  while (!Serial.available() && millis()<10000) {
    delay(100);
  }
  FastPwmSetup();
  maxamp.begin(MAX31865_2WIRE);
  maxamp2.begin(MAX31865_2WIRE);
  //display_status();
  //wdt_enable(WDTO_2S); 
}

void loop() {
  while (Serial.available() && (paas2!='b' && paas2!='c' && paas2!='0')){ // only collects paas2 once
    Serial.println("Enter second PAAS type (B or C) or enter 0 if heating PAAS-A only");
    char usrkey[5];  // character array to get paas2 and user choice setpoint 
    byte len = Serial.readBytesUntil('\n',usrkey,sizeof(usrkey));  // read bytes into usrkey until hit enter
    usrkey[len]=0; 
    char *pKbd = usrkey; 
    paas2 = *pKbd;  
    pKbd++; 
    usrsp = atof(pKbd); 
    if (usrsp<=55 && usrsp>0){  // limit to 55C; sp>0 checks if value collected from user input
      if (usrsp!=setpointA){  //new setpoint
        state=0;            // resets holdstart to get full holdtime at new setpoint
        setpointA = usrsp; 
        setpointB = min(setpointA,44);   // testing to get better match at low temp
        setpointC = min(setpointA,50);   // testing to get better match at low temp
        //setpointB = setpointA*0.87-0.73;  // approx, based on PAAS-B correction for RTD location
        //setpointC = setpointA*0.91+0.37; // approx, based on PAAS-C correction for RTD location
      }
    }
  }
  if (paas2=='b' | paas2=='c' | paas2=='0'){  // type of paas selected, do heat stuff
    if (paas2=='b') setpoint2=setpointB;
    else setpoint2=setpointC; // PA only does not use sp2
    //wdt_enable(WDTO_2S); // measurements and PWM values take about 332ms
    static uint32_t start;  
    uint32_t now = millis();  
    int32_t hasBeen = now - start;
    if (hasBeen>1000*wait){
      display_status();
      if (state==0){  // increase temperature
        tempA = maxamp.temperature(RNOMINAL_PTCO, RREF);
        if (tempA>setpointA){  // start hold phase
          holdstart = millis();
          state = 1;
        }
        temp_control();
        start = now;
      }
      else{  // hold temperature at setpoint
        if ((millis()-holdstart)/60000 < holdtime){
          // control temperature as in state 0
          display_status();
          temp_control();
          start = now;
        }
        else{
          // shut off power
          display_status();
          Serial.println("Timer has shut off power");
          FastPwm(0,0);
          start = now;
        }     
      }
    }
    delay(10);
    //wdt_reset();
  Serial.println("reseting paas2");
  paas2='x'; // python interface resends choice on next pass
  while (!Serial.available()) delay(100);
    
  }
}

void temp_control(){
  tempA = maxamp.temperature(RNOMINAL_PTCO, RREF);
  if (paas2!='0'){
    float dT;
    temp2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
    if (paas2=='c') {
      Serial.println("testing experimental code: set to PA PC");
      // expt. calib. for PAAS-C
      dT = tempA - temp2 - 5.0*(tempA/setpointA);
      //Serial.print("dT ");Serial.println(dT);  
    }
    if (paas2=='b') {
      Serial.println("testing experimental code: set to PA PB");
      // PAAS-B: correction for RTD placed in corner meas. lower temp. than bulk
      dT = tempA - temp2 - 8.0*(tempA/setpointA);  
    }
    if (dT<0 && valA==255) valB+=int(round(Pb * dT));
    else if (dT>0 && valB==255) valA-=int(round(Pa *dT));
    else {
      valA += int(round(Pa * (setpointA-tempA)));
      valB += int(round(Pb * (setpoint2-temp2)));
    }
  }
  else {  // PAAS-A only -> no temp. diff. to consider
    valA += int(round(Pa * (setpointA-tempA)));
    valB =0;
  }
  valA = max(0,min(255,valA));
  valB = max(0,min(255,valB));
  Serial.print("valA: ");Serial.println(valA);
  Serial.print("valB: ");Serial.println(valB);
  FastPwm(valA,valB); 
}

void display_status(){
  //Serial.println("PAAS-B: RTD in corner -> expect lower temperature than surface");
  //Serial.println("PAAS-C: testing calibration -> expect apparent temp. diff. up to 5C");
  Serial.print("Temperature 1 = "); Serial.println(maxamp.temperature(RNOMINAL_PTCO, RREF));
  Serial.print("Temperature 2 = "); Serial.println(maxamp2.temperature(RNOMINAL_PTCO2, RREF));
  Serial.print("Time = ");Serial.println(millis());
  Serial.print("SetpointA = ");Serial.println(setpointA); //[debug]
  Serial.print("SetpointB = ");Serial.println(setpointB);
  Serial.print("SetpointC = ");Serial.println(setpointC);
  delay(10);
}


