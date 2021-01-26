   /*
 * vibrator
 *
 * Arduino code used for vibrating the string or straw for tension measurements.
 * 
 * created by Vadim Rusu (vrusu@fnal.gov)
 * edited 09 February 2016
 * by Lauren Yates (yatesla@fnal.gov)
 */

#include <Wire.h>
#include <stdint.h>
#define I2C_ADDRESS 0x27
                                                                                                                                                                        

const int enable = 8;
const int enabledigi = 9;
//try reversing:
//const int enable = 9;
//const int enabledigi = 8;

const int convst = 10;
const int busy = 5;
const int sdata = 4;
const int sclk = 11;
const int dbgPin = 23;

const int baudRate = 115200;
const int dataLength = 2000;

void setup()
{
  REG_ADC_MR = (REG_ADC_MR & 0xFFF0F0FF) | 0x000F0300;
  analogReadResolution(12);
  Serial.begin(baudRate); // start serial for output
  //  Serial.println("Setting up BMP085");
  Wire.begin();

  pinMode(enable, OUTPUT);    
  pinMode(enabledigi, OUTPUT);
  pinMode(convst, OUTPUT);
  pinMode(busy, INPUT);    
  pinMode(sdata, INPUT);    
  pinMode(sclk, OUTPUT);    
  pinMode(dbgPin,OUTPUT);
  digitalWrite(enabledigi, HIGH);
  digitalWrite(enable,LOW);
  digitalWrite(convst,HIGH);
  digitalWrite(sclk,LOW);
}


void startDrive(){
  digitalWrite(enable,HIGH);
}

void endDrive(){
  digitalWrite(enable,LOW);  
}

void endDigitize(){
  digitalWrite(enabledigi,LOW);  
}

void startDigitize(){
  digitalWrite(enabledigi,HIGH);
}

unsigned int readADC()
{
  unsigned int adcval = 0;
  digitalWrite(convst, LOW);
  delayMicroseconds(1);
  digitalWrite(convst, HIGH);
  delayMicroseconds(5); 

  for(int i=16; i--; )
    {
      digitalWrite(sclk,HIGH);
      unsigned int d = digitalRead(sdata);
      
      digitalWrite(sclk,LOW);
      adcval |= (d<<i);     
      //Serial.println(d);
      //Serial.println(adcval);
      //digitalWrite(sclk,LOW);
    }

  delayMicroseconds(1);
  return adcval;
}

void loop()
{
  int v=analogRead(sdata);
  //Serial.println(v);
  
  int incomingByte = 0;
  unsigned int adcreadings[dataLength];
  
  char buffer[8];
  memset(buffer, 0, 8); // Reset the value of the buffer to zero
  
  unsigned int adcval;

  
  while (!Serial.available());
  
  //  buffer = Serial.read();
  //Serial.println("I am ready");
  
  Serial.setTimeout(1000000);
  
  // Read in the incoming trigger
  Serial.readBytesUntil('\n',buffer,8);
  int incoming = atoi(buffer);
  //Serial.println(incoming);
  
  // Read in the pulse width
  Serial.readBytesUntil('\n',buffer,8);
  int pulseWidth = atoi(buffer);

  if (incoming == 4){
    Serial.println("4");
    
    //Pulse the straw
    for (int i =0; i<100; i++)
    {
      delayMicroseconds(5666);
      startDrive();
      delayMicroseconds(1000);
      // delay(100);
      endDrive();
    }
    delay(1);
    startDigitize();
    delayMicroseconds(10);
    
    for (int i = 0 ; i < dataLength; i++)
    {
      adcreadings[i] = readADC();
      delayMicroseconds(1);
    }

    endDigitize();
      
    // Now send to serial
    for (int i = 0 ; i < dataLength; i++){
      Serial.println(adcreadings[i]);
    }

  }
  else if (incoming == 5){
    Serial.println("5");
    
    Serial.print("Using a pulse of width (in microseconds): ");
    Serial.println(pulseWidth);
    
    // Pulse the straw
    startDrive();
    delayMicroseconds(pulseWidth);
    endDrive();

    delay(3); // Delay between pulse and gate
    startDigitize();
    
    delayMicroseconds(10); 

    unsigned int *pReading = adcreadings;
    unsigned int tNext = 0;
    digitalWrite(dbgPin,HIGH);
    for (int i = dataLength; i--; pReading++)
    {
      unsigned int tNow;
      while ((tNow = micros())<tNext) ;
      tNext = tNow + 120;
      *pReading = readADC();
    }
    digitalWrite(dbgPin,LOW);

    endDigitize();
    
    // Now send to serial
    for (int i = 0 ; i < dataLength; i++){      
      Serial.println(adcreadings[i]);
    }
  }

  else if (incoming == 6){
    Serial.println("6");
    
    startDigitize();
    delayMicroseconds(10);
    
    for (int i = 0 ; i < dataLength; i++)
    {
      adcreadings[i] = readADC();
      delayMicroseconds(1);
    }

    endDigitize();
    
    // Now send to serial
    for (int i = 0 ; i < dataLength; i++){
      Serial.println(adcreadings[i]);
    }

  }

}
