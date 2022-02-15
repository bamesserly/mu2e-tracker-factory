// CO2 sensor readout code (expert mode)
//   Vadim Rusu -- Fermilab

#include "E2.h"
#include<SoftwareSerial.h>  //Include the Soft Serial Library

E2_Wire co2_sensor(A4,A5);
//SoftwareSerial BTSerial(0, 1);  // RX, TX --bluetooth coomunication

int ppm1,ppm2;
unsigned char state;

unsigned long old_time[8];
unsigned stat[8];
float old_readings[8];
float new_readings[8];

void setup()
{
  pinMode(10,OUTPUT);
  digitalWrite(10,HIGH);
  Serial.begin(115200);
  //  BTSerial.begin(9600);  //Start Bluetooth Serial Connection
}


void listBus(){



  for (int iaddr = 0; iaddr<8; iaddr++){
    co2_sensor.readSensorType(iaddr); //somehow the address pointer does not get reset properly. This fixes it!!!! To be looked at.
    if (co2_sensor.readSensorType(iaddr) != 0xFF){
    //Serial.print("Device at address ");
    //Serial.print (iaddr, DEC);
    //Serial.print (": ");
    //Serial.println(co2_sensor.readSensorType(iaddr),HEX);
    //Serial.println(co2_sensor.readSensorName(iaddr));
    stat[iaddr]=iaddr;
    }
    else
    {
      stat[iaddr]=-10;
    }
  }

}

void loop()
{

  char buffer[8];
    
  //while (!Serial.available());
  //Serial.setTimeout(1000000);
  //Serial.readBytesUntil('\n',buffer,8);
  //int incoming = atoi(buffer);  
  //int  incoming = 1; //Edit to check python script
  listBus();

  /*
  if (incoming == 99 ) {
    listBus();
    Serial.println("Which busId you want to change?");
    Serial.println("Please enter in an available one, or it will be in an endless loop");
    
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

    
    unsigned int bid;
    unsigned char i=0;
    do{
    if(i>0)Serial.println("Please enter an available busID:");
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    bid = atoi(buffer);  
    Serial.println(bid);
    i++;
    }while(stat[bid]!=bid);// To ensure the user enter an available busID
                           // otherwise it will be in a endless loop - Yan Ke
    
    Serial.println("Set offset for this one");
    
    while (!Serial.available());
    Serial.setTimeout(1000000);
    Serial.readBytesUntil('\n',buffer,8);
    
    int offset = atoi(buffer);  
    Serial.println(offset);

    co2_sensor.write_offset(bid, offset);

    unsigned int offset0=1;
    offset0=co2_sensor.offset_read(bid);
    Serial.print("The offset now is:");
    Serial.println(offset0);

  }
  */
  
  //else {
  
  for (int iaddr = 0; iaddr<8; iaddr++)
    {
      old_readings[iaddr]=-1;
      old_time[iaddr]=millis();
    }
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
    

    for (int iaddr = 0; iaddr<8; iaddr++)
    {
      if (stat[iaddr]==iaddr)
      {
        //delay(20);//not running continuously
        new_readings[iaddr]=co2_sensor.CO2_read(iaddr);
        if((new_readings[iaddr]!=old_readings[iaddr]&&new_readings[iaddr]!=-1)||(new_readings[iaddr]==old_readings[iaddr]&&millis()-old_time[iaddr]>18000))
        {
          old_time[iaddr]=millis();
          Serial.print(iaddr);
          Serial.print(" ");
          Serial.println(new_readings[iaddr]);
          old_readings[iaddr]=new_readings[iaddr];
        }
      }
    }
    //    Serial.println("--------");
  //}    
}

}
