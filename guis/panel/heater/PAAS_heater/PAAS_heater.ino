#include <Adafruit_MAX31865.h>
#include "FastPwm.h"  // Fast PWM output to pins 13 and 10
#include <avr/wdt.h>

// RTD 
#define RREF      430.0  
#define RNOMINAL_PTCO2 100.0 // nominal PT100 RTD resistance at 0C
#define RNOMINAL_PTCO 100.0  
// MAX31865 amplifier pins CS,SD1,SD0,CLK
Adafruit_MAX31865 maxamp = Adafruit_MAX31865(4, 3, 2, 5);   // PTCO
Adafruit_MAX31865 maxamp2 = Adafruit_MAX31865(9, 8, 7, 6);  // PTCO2

// temperature settings PAAS-A / PAAS-B / PAAS-C
// no default temperature setpoint: user must select in python interface
float setpointA = 0.0; // [degrees C]
float setpointB = 0.0;
float setpointC = 0.0; 
int valA=255;
int valB=255;
float Pa=5.0;  
float Pb=5.0;  
float tempA;
float temp2;
float initial_temp2;
float usrsp;  // user choice setpoint temperature 
float max_temp = -9;
float time_of_max_temp = -1;

float setpoint2;  
char paas2='x'; // placeholder for user choice of 2nd PAAS type
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
	//wdt_enable(WDTO_2S); 
	initial_temp2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
}

void loop() {
	// get updates from python interface if connected
	if (Serial.available()){  
		Serial.println("Enter second PAAS type (B or C) or enter 0 if heating PAAS-A only");
		char usrkey[5];  // user choice of 2nd PAAS type and temperature setpoint
		byte len = Serial.readBytesUntil('\n',usrkey,sizeof(usrkey));  // read bytes into usrkey until newline
		// paas2=usrkey[0];
		// usrsp=usrkey[1:];  ...
		usrkey[len]=0; 
		char *pKbd = usrkey; 
		paas2 = *pKbd;  
		pKbd++; 
		usrsp = atof(pKbd); 
		if (abs(usrsp-setpointA)>5){ // new setpoint from python interface either 34C or 55C / software timer fixed
			state=0; // resets holdstart to get full holdtime at new setpoint
			setpointA = min(usrsp,52); 
			// setpointB based on PAAS-B correction for temperature difference at RTD location vs. bulk surface
			if (setpointA>34){ setpointB=50; }
			else { setpointB=33.9; }
			// setpointC based on PAAS-C correction for temperature difference at RTD location vs. under baseplate
			setpointC = min(setpointA,50); 
		}
	}
	// control heat cycle
	// with 2nd PAAS type set, heater control will run with or without connection to python interface
	if (paas2=='b' | paas2=='c' | paas2=='0'){
		if (paas2=='b') setpoint2=setpointB;
		else setpoint2=setpointC; // heat cycle for PAAAS-A alone does not use setpoint2
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
		delay(100); // does not wait indefinitely for serial availability
	}
}

void temp_control(){
	tempA = maxamp.temperature(RNOMINAL_PTCO, RREF);
	if (paas2!='0'){
		float dT;
		temp2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
		if (paas2=='c') {
			// PAAS-C correction: RTD placed in corner measures lower temperature than under baseplate at 55C
			dT = tempA - temp2 - 5.0*(tempA/setpointA);  // experimental
		}
		if (paas2=='b') {
			// PAAS-B correction: RTD placed in corner measures lower temperature than bulk surface at 55C
			dT = tempA - temp2 - 4.5*(max(0,temp2-34)/16);  // experimental: with cube foam
			if (setpointB<34){ // try to get faster rise to 34C by altering where feedback constraint applies
				// 0130. adding condition on temp2 to prevent heating if B not plugged in
				if (tempA<31 && temp2>initial_temp2+2){dT=0;}
				else {dT = tempA - temp2 - 5.0*(max(0,temp2-20)/14);}
			}
			// Heat to 55:
			// Heat A and B at full blast unless TA>=46 && (TB<40 || TA>44), in
			// which case use the default dT.
			if (setpointA>50) {
				if(tempA>=46 && (temp2<40 || temp2>44)){ ; }
				else dT=0;
			}
		}
		if (dT<0 && valA==255) valB+=int(round(Pb * dT)); // -> slow the heating of B
		else if (dT>0 && valB==255) valA-=int(round(Pa * dT)); // -> slow the heating of A
		else {
			valA += int(round(Pa * (setpointA-tempA)));
			valB += int(round(Pb * (setpoint2-temp2)));
		}
	}
	else {  // PAAS-A only -> no temperature difference to consider
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
	if(max_temp < maxamp.temperature(RNOMINAL_PTCO, RREF)){
		max_temp = maxamp.temperature(RNOMINAL_PTCO, RREF)
	}
	Serial.print("Temperature 1: "); Serial.println(maxamp.temperature(RNOMINAL_PTCO, RREF));
	Serial.print("Temperature 2: "); Serial.println(maxamp2.temperature(RNOMINAL_PTCO2, RREF));
	Serial.print("Max Temp: "); Serial.println(max_temp);
	Serial.print("Time = ");Serial.println(millis());
	//Serial.print("state = ");Serial.println(state); // test for software timer fix
	delay(10);
}


