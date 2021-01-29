/*************************************************** 
  This is an example for the SHT31-D Humidity & Temp Sensor

  Designed specifically to work with the SHT31-D sensor from Adafruit
  ----> https://www.adafruit.com/products/2857

  These sensors use I2C to communicate, 2 pins are required to  
  interface
 ****************************************************/
 
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

Adafruit_SHT31 sht31 = Adafruit_SHT31();
int readin = 0;

void setup() {
  Serial.begin(9600);

  while (!Serial)
    delay(10);     // will pause Zero, Leonardo, etc until serial console opens

  if (! sht31.begin(0x44)) {   // Set to 0x45 for alternate i2c addr
    Serial.println("Couldn't find SHT31");
    while (1) delay(1);
  }
}


void loop() {
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();
  
  readin = Serial.read();
  if( readin == 53 ){
    if (! isnan(t) && ! isnan(h)) {  // check if 'is not a number'
      Serial.print(t); Serial.print(','); Serial.print(h);
      Serial.println();
    } else { 
      Serial.println("NaN,NaN");
    }
  }
  delay(100);
}
