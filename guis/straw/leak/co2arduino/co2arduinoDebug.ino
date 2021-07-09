// CO2 sensor readout code (expert mode)
//   Vadim Rusu -- Fermilab

#include "E2.h"
#include <SoftwareSerial.h>
//Include the Soft Serial Library

E2_Wire co2_sensor(A4,A5);
//SoftwareSerial BTSerial(0, 1);  // RX, TX --bluetooth coomunication

//float vco2;
int ppm1,ppm2;
unsigned char state;

unsigned char stat[8];
unsigned long old_time;
unsigned long new_time;
void setup()
{
  pinMode(10,OUTPUT);
  digitalWrite(10,HIGH);
  Serial.begin(115200);
  //  BTSerial.begin(9600);  //Start Bluetooth Serial Connection
}


void listBus(){

  for(int i=0;i<8;i++)
    {
      stat[i]=10;
    }
   //unsigned char rd;
  for (int iaddr = 0; iaddr<8; iaddr++){
    co2_sensor.readSensorType(iaddr); //somehow the address pointer does not get reset properly. This fixes it!!!! To be looked at.
    
    //rd=co2_sensor.readSensorType(iaddr);
    //Serial.print("Address: ");
    //Serial.print(iaddr);
    //Serial.print(" sensor type: ");
    //Serial.println(rd,HEX);
    if (co2_sensor.readSensorType(iaddr) != 0xFF){
    stat[iaddr]=iaddr;

    Serial.print("Device at address ");
    Serial.print (iaddr, DEC);
    Serial.print (": ");
    Serial.println(co2_sensor.readSensorType(iaddr),HEX);
    Serial.println(co2_sensor.readSensorName(iaddr)); 
    }
  }

}

void loop()
{

  char buffer[8];

  
   while (!Serial.available());
  Serial.setTimeout(1000000);
  Serial.readBytesUntil('\n',buffer,8);
  int incoming = atoi(buffer);  
  //int  incoming = 1; //Edit to check python script
  //int  incoming = 99;

  if (incoming == 99 ) {
    listBus();
    Serial.println("Which busId you want to change?");
    
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    unsigned int bid = atoi(buffer);  
    Serial.println(bid);

    Serial.println("Input address for this one");
    
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    unsigned int newadd = atoi(buffer);  
    Serial.println(newadd);

    unsigned int retc = co2_sensor.ReAddress(bid, newadd);
    Serial.println(retc);

    
  }

  else if (incoming == 98 ) listBus();

  else if (incoming == 97 ) {
    int offset = -999;
    int gain = -999;
    for (int iaddr = 0; iaddr<8; iaddr++){
      if (co2_sensor.readSensorType(iaddr) != 0xFF){
	offset = co2_sensor.read_from(iaddr,0x58) | (co2_sensor.read_from(iaddr,0x59) << 8);
	gain = co2_sensor.read_from(iaddr,0x5A) | (co2_sensor.read_from(iaddr,0x5B) << 8);

	Serial.print("Offset ");
	Serial.print(iaddr);
	Serial.print ( "  ");
	Serial.println (offset);
	Serial.print("Gain ");
	Serial.print(iaddr);
	Serial.print ( "  ");
	Serial.println (gain);
      }
    }
  }


   else if (incoming == 96 ) {

    listBus();
    Serial.println("Which busId you want to set offset for?");
    
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    unsigned int bid = atoi(buffer);  
    //unsigned int bid = 0;
    Serial.println(bid);

    Serial.println("Set offset for this one");
    
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    int offset = atoi(buffer);  
    //int offset = 100;
    Serial.println(offset);

    unsigned int retc = co2_sensor.write_offset(bid, offset);
    Serial.println(retc);
    
    //-------------------------------------------Reading code
    unsigned char readings;
     for (unsigned char iaddr = 0; iaddr<8; iaddr++){
     Serial.print("Readings for address# ");
     Serial.print(iaddr);
     Serial.print("  ");
    readings=co2_sensor.read_from(iaddr,0x08);
    readings=readings&2;
    Serial.println(readings);
     }
    
  

  }

  //else {
  old_time=millis();
  while (1) {


    
    /*
    if(Serial.available()>0) {

    int readout = Serial.readBytesUntil('\n',buffer,100);
    for (int i = 0 ; i < readout-1; i++)
      readString += buffer[i];

    delay(10);

    unsigned char addr = readString.toInt();
    */

    
    //   listBus();

    //delay(10000);
    for (int iaddr = 0; iaddr<8; iaddr++){
      if (iaddr==stat[iaddr]){
        Serial.print("Address : ");
        Serial.print(iaddr);
        Serial.print("   Reading  : ");
        Serial.print(co2_sensor.CO2_read(iaddr));
        new_time=millis();
        Serial.print(" ");
        Serial.print(new_time-old_time);
        Serial.print(" ");
        old_time=millis();
      }
    }
    Serial.println();
    //    Serial.println("--------");
  //}    
}

}
