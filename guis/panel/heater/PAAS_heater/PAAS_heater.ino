#include <Adafruit_MAX31865.h>
#include <avr/wdt.h>

#include "FastPwm.h"  // Fast PWM output to pins 13 and 10

// RTD
#define RREF 430.0
#define RNOMINAL_PTCO2 100.0  // nominal PT100 RTD resistance at 0C
#define RNOMINAL_PTCO 100.0
// MAX31865 amplifier pins CS,SD1,SD0,CLK
Adafruit_MAX31865 maxamp = Adafruit_MAX31865(4, 3, 2, 5);   // PTCO
Adafruit_MAX31865 maxamp2 = Adafruit_MAX31865(9, 8, 7, 6);  // PTCO2

// temperature settings PAAS-A / PAAS-B / PAAS-C
// no default temperature setpoint: user must select in python interface
float setpointA = 0.0;  // [degrees C]
float setpointB = 0.0;
float setpointC = 0.0;
int valA = 255;
int valB = 255;
float Pa = 5.0;
float Pb = 5.0;
float tempA;
float temp2;
float initial_temp2;
float usrsp;  // user choice setpoint temperature

// Save key metrics in case monitor crashes
float tempA_max = -99;               // max temp
uint32_t tempA_max_timestamp = 0;    // time at which max temp was reached
uint32_t tempA_setpt_timestamp = 0;  // time setpoint was reaches
uint32_t tempA_first_60_timestamp = 0;
uint32_t tempA_first_55_timestamp = 0;
uint32_t tempA_first_50_timestamp = 0;
uint32_t tempA_first_45_timestamp = 0;
uint32_t tempA_first_40_timestamp = 0;
uint32_t tempA_first_30_timestamp = 0;
uint32_t tempA_last_60_timestamp = 0;
uint32_t tempA_last_55_timestamp = 0;
uint32_t tempA_last_50_timestamp = 0;
uint32_t tempA_last_45_timestamp = 0;
uint32_t tempA_last_40_timestamp = 0;
uint32_t tempA_last_30_timestamp = 0;

float temp2_max = -99;
uint32_t temp2_max_timestamp = 0;
uint32_t temp2_setpt_timestamp = 0;
uint32_t temp2_first_60_timestamp = 0;
uint32_t temp2_first_55_timestamp = 0;
uint32_t temp2_first_50_timestamp = 0;
uint32_t temp2_first_45_timestamp = 0;
uint32_t temp2_first_40_timestamp = 0;
uint32_t temp2_first_30_timestamp = 0;
uint32_t temp2_last_60_timestamp = 0;
uint32_t temp2_last_55_timestamp = 0;
uint32_t temp2_last_50_timestamp = 0;
uint32_t temp2_last_45_timestamp = 0;
uint32_t temp2_last_40_timestamp = 0;
uint32_t temp2_last_30_timestamp = 0;

float setpoint2;
char paas2 = 'x';              // placeholder for user choice of 2nd PAAS type
const int32_t wait = 8;        // time between data points [seconds]
const int32_t holdtime = 300;  // [minutes] time to hold temperature at setpoint
int32_t holdstart;
uint8_t do_increase_temperature = 1;

void setup() {
  Serial.begin(2000000);
  // don't wait indefinitely for serial, which would prevent WDT reset
  while (!Serial.available() && millis() < 10000) {
    delay(100);
  }
  FastPwmSetup();
  maxamp.begin(MAX31865_2WIRE);
  maxamp2.begin(MAX31865_2WIRE);
  // wdt_enable(WDTO_2S);
  initial_temp2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
}

void loop() {
  // get updates from python interface if connected.
  // any not-empty write command to the serial connection triggers this.
  if (Serial.available()) {
    Serial.println(
        "Enter second PAAS type (B or C) or enter 0 if heating PAAS-A only");
    char usrkey[5];  // user choice of 2nd PAAS type and temperature setpoint
    byte len = Serial.readBytesUntil(
        '\n', usrkey, sizeof(usrkey));  // read bytes into usrkey until newline
    // paas2=usrkey[0];
    // usrsp=usrkey[1:];  ...
    usrkey[len] = 0;
    char *pKbd = usrkey;
    paas2 = *pKbd;
    pKbd++;
    usrsp = atof(pKbd);
    if (abs(usrsp - setpointA) >
        5) {  // new setpoint from python interface either 36C or 55C / software
              // timer fixed
      do_increase_temperature =
          1;  // resets holdstart to get full holdtime at new setpoint
      setpointA = min(usrsp, 52);
      if(setpointA!=52) { setpointA = 36; }
      // setpointB based on PAAS-B correction for temperature difference at RTD
      // location vs. bulk surface
      if (setpointA > 36) {
        setpointB = 50;
      } else {
        setpointB = 35.9;
      }
      // setpointC based on PAAS-C correction for temperature difference at RTD
      // location vs. under baseplate
      setpointC = min(setpointA, 50);
    }
  }
  // control heat cycle
  // with 2nd PAAS type set, heater control will run with or without connection
  // to python interface
  if (paas2 == 'b' | paas2 == 'c' | paas2 == '0') {
    if (paas2 == 'b')
      setpoint2 = setpointB;
    else
      setpoint2 =
          setpointC;  // heat cycle for PAAAS-A alone does not use setpoint2
    // wdt_enable(WDTO_2S); // measurements and PWM values take about 332ms
    static uint32_t start;
    uint32_t now = millis();
    int32_t hasBeen = now - start;
    if (hasBeen > 1000 * wait) {
      display_status();
      if (do_increase_temperature == 1) {  // increase temperature
        tempA = maxamp.temperature(RNOMINAL_PTCO, RREF);
        // start hold phase - protect against unphysical temps
        if (tempA > setpointA && tempA < 100) {
          holdstart = millis();
          do_increase_temperature = 0;  // hold temperature
        }
        temp_control();
        start = now;
      } else {  // hold temperature at setpoint
        if ((millis() - holdstart) / 60000 < holdtime) {
          // control temperature as in do_increase_temperature 1
          display_status();
          temp_control();
          start = now;
        } else {
          // shut off power
          display_status();
          Serial.println("Timer has shut off power");
          FastPwm(0, 0);
          start = now;
        }
      }
    }
    delay(10);
    // wdt_reset();
    delay(100);  // does not wait indefinitely for serial availability
  }
}

void temp_control() {
  tempA = maxamp.temperature(RNOMINAL_PTCO, RREF);
  if (paas2 != '0') {
    float dT;
    temp2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
    if (paas2 == 'c') {
      // PAAS-C correction: RTD placed in corner measures lower temperature than
      // under baseplate at 55C
      dT = tempA - temp2 - 5.0 * (tempA / setpointA);  // experimental
    }
    if (paas2 == 'b') {
      // PAAS-B correction: RTD placed in corner measures lower temperature than
      // bulk surface at 55C
      dT = tempA - temp2 -
           4.5 * (max(0, temp2 - 36) / 16);  // experimental: with cube foam
      if (setpointB < 36) {  // try to get faster rise to 36C by altering where
                             // feedback constraint applies
        // 0130. adding condition on temp2 to prevent heating if B not plugged
        // in
        if (tempA < 31 && temp2 > initial_temp2 + 2) {
          dT = 0;
        } else {
          dT = tempA - temp2 - 5.0 * (max(0, temp2 - 20) / 14);
        }
      }
      // Heat to 55:
      // Heat A and B at full blast unless TA>=46 && (TB<40 || TA>44), in
      // which case use the default dT.
      if (setpointA > 50) {
        if (tempA >= 46 && (temp2 < 40 || temp2 > 44)) {
          ;
        } else
          dT = 0;
      }
    }
    if (dT < 0 && valA == 255)
      valB += int(round(Pb * dT));  // -> slow the heating of B
    else if (dT > 0 && valB == 255)
      valA -= int(round(Pa * dT));  // -> slow the heating of A
    else {
      valA += int(round(Pa * (setpointA - tempA)));
      valB += int(round(Pb * (setpoint2 - temp2)));
    }
  } else {  // PAAS-A only -> no temperature difference to consider
    valA += int(round(Pa * (setpointA - tempA)));
    valB = 0;
  }
  valA = max(0, min(255, valA));
  valB = max(0, min(255, valB));
  Serial.print("valA: ");
  Serial.println(valA);
  Serial.print("valB: ");
  Serial.println(valB);
  FastPwm(valA, valB);
}

bool set_first_condition(const float temp, const float set_temp,
                         const uint32_t first_timestamp) {
  return is_at_temp(temp, set_temp) && first_timestamp == 0;
}

bool is_at_temp(const float temp, const float set_temp) {
  return set_temp - 1 < temp && temp < set_temp + 1;
}

void set_key_metrics(float temp_A, float temp_2, uint32_t now) {
  // Max temps
  if (tempA_max < temp_A) {  // A max temp
    tempA_max_timestamp = now;
    tempA_max = temp_A;
  }
  if (temp2_max < temp_2) {  // 2 max temp
    temp2_max_timestamp = now;
    temp2_max = temp_2;
  }

  // Last time that paas was within +/- 3 degree of its setpoint
  if (setpointA - 3 < temp_A && temp_A < setpointA + 3) {  // A set point time
    tempA_setpt_timestamp = now;
  }
  if (setpoint2 - 3 < temp_2 && temp_2 < setpoint2 + 3) {  // 2 set point time
    temp2_setpt_timestamp = now;
  }

  // First time that paas was within +- 1 degrees of 60, 55, 50, 45, 40, 30
  if (set_first_condition(temp_A, 60, tempA_first_60_timestamp))
    tempA_first_60_timestamp = now;
  if (set_first_condition(temp_A, 55, tempA_first_55_timestamp))
    tempA_first_55_timestamp = now;
  if (set_first_condition(temp_A, 50, tempA_first_50_timestamp))
    tempA_first_50_timestamp = now;
  if (set_first_condition(temp_A, 45, tempA_first_45_timestamp))
    tempA_first_45_timestamp = now;
  if (set_first_condition(temp_A, 40, tempA_first_40_timestamp))
    tempA_first_40_timestamp = now;
  if (set_first_condition(temp_A, 30, tempA_first_30_timestamp))
    tempA_first_30_timestamp = now;

  if (set_first_condition(temp_2, 60, temp2_first_60_timestamp))
    temp2_first_60_timestamp = now;
  if (set_first_condition(temp_2, 55, temp2_first_55_timestamp))
    temp2_first_55_timestamp = now;
  if (set_first_condition(temp_2, 50, temp2_first_50_timestamp))
    temp2_first_50_timestamp = now;
  if (set_first_condition(temp_2, 45, temp2_first_45_timestamp))
    temp2_first_45_timestamp = now;
  if (set_first_condition(temp_2, 40, temp2_first_40_timestamp))
    temp2_first_40_timestamp = now;
  if (set_first_condition(temp_2, 30, temp2_first_30_timestamp))
    temp2_first_30_timestamp = now;

  // Last time that paas was within +- 2 degrees of 60, 55, 50, 45, 40, 30
  if (is_at_temp(temp_A, 60)) tempA_last_60_timestamp = now;
  if (is_at_temp(temp_A, 55)) tempA_last_55_timestamp = now;
  if (is_at_temp(temp_A, 50)) tempA_last_50_timestamp = now;
  if (is_at_temp(temp_A, 45)) tempA_last_45_timestamp = now;
  if (is_at_temp(temp_A, 40)) tempA_last_40_timestamp = now;
  if (is_at_temp(temp_A, 30)) tempA_last_30_timestamp = now;

  if (is_at_temp(temp_2, 60)) temp2_last_60_timestamp = now;
  if (is_at_temp(temp_2, 55)) temp2_last_55_timestamp = now;
  if (is_at_temp(temp_2, 50)) temp2_last_50_timestamp = now;
  if (is_at_temp(temp_2, 45)) temp2_last_45_timestamp = now;
  if (is_at_temp(temp_2, 40)) temp2_last_40_timestamp = now;
  if (is_at_temp(temp_2, 30)) temp2_last_30_timestamp = now;
}

void display_status() {
  // Serial.println("PAAS-B: RTD in corner -> expect lower temperature than
  // surface"); Serial.println("PAAS-C: testing calibration -> expect apparent
  // temp. diff. up to 5C");
  float temp_A = maxamp.temperature(RNOMINAL_PTCO, RREF);
  float temp_2 = -99;
  if (paas2 != '0') {
    temp_2 = maxamp2.temperature(RNOMINAL_PTCO2, RREF);
  }
  uint32_t now = millis();
  set_key_metrics(temp_A, temp_2, now);
  Serial.print("Temperature 1: ");
  Serial.println(temp_A);
  Serial.print("Temperature 2: ");
  Serial.println(temp_2);
  Serial.print("Time = ");
  Serial.println(millis());
  // Serial.print("do_increase_temperature =
  // ");Serial.println(do_increase_temperature); // test for software timer fix

  Serial.print("recovery tempA_max ");
  Serial.println(tempA_max);
  Serial.print("recovery tempA_max_timestamp ");
  Serial.println(tempA_max_timestamp);
  Serial.print("recovery tempA_setpt_timestamp ");
  Serial.println(tempA_setpt_timestamp);
  Serial.print("recovery tempA_first_60_timestamp ");
  Serial.println(tempA_first_60_timestamp);
  Serial.print("recovery tempA_first_55_timestamp ");
  Serial.println(tempA_first_55_timestamp);
  Serial.print("recovery tempA_first_50_timestamp ");
  Serial.println(tempA_first_50_timestamp);
  Serial.print("recovery tempA_first_45_timestamp ");
  Serial.println(tempA_first_45_timestamp);
  Serial.print("recovery tempA_first_40_timestamp ");
  Serial.println(tempA_first_40_timestamp);
  Serial.print("recovery tempA_first_30_timestamp ");
  Serial.println(tempA_first_30_timestamp);
  Serial.print("recovery tempA_last_60_timestamp ");
  Serial.println(tempA_last_60_timestamp);
  Serial.print("recovery tempA_last_55_timestamp ");
  Serial.println(tempA_last_55_timestamp);
  Serial.print("recovery tempA_last_50_timestamp ");
  Serial.println(tempA_last_50_timestamp);
  Serial.print("recovery tempA_last_45_timestamp ");
  Serial.println(tempA_last_45_timestamp);
  Serial.print("recovery tempA_last_40_timestamp ");
  Serial.println(tempA_last_40_timestamp);
  Serial.print("recovery tempA_last_30_timestamp ");
  Serial.println(tempA_last_30_timestamp);

  Serial.print("recovery temp2_max ");
  Serial.println(temp2_max);
  Serial.print("recovery temp2_max_timestamp ");
  Serial.println(temp2_max_timestamp);
  Serial.print("recovery temp2_setpt_timestamp ");
  Serial.println(temp2_setpt_timestamp);
  Serial.print("recovery temp2_first_60_timestamp ");
  Serial.println(temp2_first_60_timestamp);
  Serial.print("recovery temp2_first_55_timestamp ");
  Serial.println(temp2_first_55_timestamp);
  Serial.print("recovery temp2_first_50_timestamp ");
  Serial.println(temp2_first_50_timestamp);
  Serial.print("recovery temp2_first_45_timestamp ");
  Serial.println(temp2_first_45_timestamp);
  Serial.print("recovery temp2_first_40_timestamp ");
  Serial.println(temp2_first_40_timestamp);
  Serial.print("recovery temp2_first_30_timestamp ");
  Serial.println(temp2_first_30_timestamp);
  Serial.print("recovery temp2_last_60_timestamp ");
  Serial.println(temp2_last_60_timestamp);
  Serial.print("recovery temp2_last_55_timestamp ");
  Serial.println(temp2_last_55_timestamp);
  Serial.print("recovery temp2_last_50_timestamp ");
  Serial.println(temp2_last_50_timestamp);
  Serial.print("recovery temp2_last_45_timestamp ");
  Serial.println(temp2_last_45_timestamp);
  Serial.print("recovery temp2_last_40_timestamp ");
  Serial.println(temp2_last_40_timestamp);
  Serial.print("recovery temp2_last_30_timestamp ");
  Serial.println(temp2_last_30_timestamp);

  delay(6);
}
