// E2 interface for EE CO2 sensors

// Vadim Rusu -- Fermilab

// ToDO:
// 1) Can I use the Wire library?
// 2) Deal with read failures
// 3) Add gain function



#include"Arduino.h"
#include "E2.h"


#define DELAY_FAKTOR 100 // setup clock-frequency
#define ACK 1 
#define NAK 0 



unsigned char co2_low;
unsigned char co2_high;
unsigned char co2mean_low;
unsigned char co2mean_high;
unsigned char checksum_03;
unsigned int co2_ee03 = 0;
unsigned int co2mean_ee03 = 0;
unsigned int internal_pointer_addr = 0;
float co2 = 0;
float co2mean = 0;
unsigned char information;

E2_Wire::E2_Wire(int pinSDA, int pinSCL)
{
    _pinSDA = pinSDA;
    _pinSCL = pinSCL;
}

/* Privates */
void E2_Wire::set_SDA(void) 
{
    pinMode(_pinSDA, OUTPUT);
    digitalWrite(_pinSDA, HIGH);
}
void E2_Wire::clear_SDA(void) 
{
    pinMode(_pinSDA, OUTPUT);
    digitalWrite(_pinSDA, LOW);
}

int E2_Wire::read_SDA(void) 
{
    pinMode(_pinSDA, INPUT);
    return digitalRead(_pinSDA);
}

void E2_Wire::set_SCL(void) 
{
    pinMode(_pinSCL, OUTPUT);
    digitalWrite(_pinSCL, HIGH);
}
void E2_Wire::clear_SCL(void) 
{
    pinMode(_pinSCL, OUTPUT);
    digitalWrite(_pinSCL, LOW);
}

void E2_Wire::E2Bus_start(void) // Start condition for E2 Interface
{
    set_SDA();
    set_SCL();
    EEdelay(30*DELAY_FAKTOR);
    clear_SDA();
    EEdelay(30*DELAY_FAKTOR);
}
/*-------------------------------------------------------------------------*/
void E2_Wire::E2Bus_stop(void) // Stop condition for E2 Interface
{
    clear_SCL();
    EEdelay(20*DELAY_FAKTOR);
    clear_SDA();
    EEdelay(20*DELAY_FAKTOR);
    set_SCL();
    EEdelay(20*DELAY_FAKTOR);
    set_SDA();
    EEdelay(20*DELAY_FAKTOR);
}
/*-------------------------------------------------------------------------*/
void E2_Wire::E2Bus_send(unsigned char value) // send one byte to E2 Interface
{
    unsigned char i;
    unsigned char maske = 0x80;
    for (i=8;i>0;i--)
    {
        clear_SCL();
        EEdelay(10*DELAY_FAKTOR);
        if ((value & maske) != 0)
            {set_SDA();}
        else
            {clear_SDA();}
        EEdelay(20*DELAY_FAKTOR);
        set_SCL();
        maske >>= 1;
        EEdelay(30*DELAY_FAKTOR);
        clear_SCL();
    }
    set_SDA();
}
/*-------------------------------------------------------------------------*/
unsigned char E2_Wire::E2Bus_read(void) // read one byte from E2 Interface
{
    unsigned char data_in = 0x00;
    unsigned char maske = 0x80;
    for (maske=0x80;maske>0;maske >>=1)
    {
        clear_SCL();
        EEdelay(30*DELAY_FAKTOR);
        set_SCL();
        EEdelay(15*DELAY_FAKTOR);
        if (read_SDA())
            {data_in |= maske;}
        EEdelay(15*DELAY_FAKTOR);
        clear_SCL();
    }
    return data_in;
}
/*-------------------------------------------------------------------------*/
char E2_Wire::check_ack(void) // check ack
{
    int input;
    EEdelay(30*DELAY_FAKTOR);
    set_SCL();
    EEdelay(15*DELAY_FAKTOR);
    input = read_SDA();
    EEdelay(15*DELAY_FAKTOR);
    if(input == 1)
        return NAK;
    else
        return ACK;
}
/*-------------------------------------------------------------------------*/
void E2_Wire::send_ack(void) // send ack
{
    clear_SCL();
    EEdelay(15*DELAY_FAKTOR);
    clear_SDA();
    EEdelay(15*DELAY_FAKTOR);
    set_SCL();
    EEdelay(30*DELAY_FAKTOR);
    clear_SCL();
    set_SDA();
}
/*-------------------------------------------------------------------------*/
void E2_Wire::send_nak(void) // send NAK
{
    clear_SCL();
    EEdelay(15*DELAY_FAKTOR);
    set_SDA();
    EEdelay(15*DELAY_FAKTOR);
    set_SCL();
    EEdelay(30*DELAY_FAKTOR);
    clear_SCL();
    set_SDA();
}
/*-------------------------------------------------------------------------*/
void E2_Wire::EEdelay(unsigned int value) // EEdelay- routine
    { delayMicroseconds(value); }
/*-------------------------------------------------------------------------*/


/* Publics*/

unsigned char E2_Wire::Status(unsigned char busId)
{
    unsigned char stat_ee03;
    E2Bus_start(); // start condition for E2-Bus
    unsigned char comm;
    comm = 0x71 | (busId<<1);
    E2Bus_send(0x71); // main command for STATUS request
    if (check_ack()==ACK)
    {
        stat_ee03 = E2Bus_read(); // read status byte
        send_ack();
        checksum_03 = E2Bus_read(); // read checksum
        send_nak(); // send NAK ...
        E2Bus_stop(); // ... and stop condition to terminate
        if (((stat_ee03 + comm) % 256) == checksum_03) // checksum OK?
            return stat_ee03;
    }
    return 0xFF; // in error case return 0xFF
}

float E2_Wire::CO2_read(unsigned char busId)
{
    co2 = -1; // default value (error code)
    E2Bus_start();
    unsigned char comm;
    comm = 0xC1 | (busId<<1);
    E2Bus_send(comm); // MW3-low request
    if (check_ack()==ACK)
    {
        co2_low = E2Bus_read();
        send_ack();
        checksum_03 = E2Bus_read();
        send_nak(); // terminate communication
        E2Bus_stop();
	if (((comm + co2_low) % 256) == checksum_03) // checksum OK?
	  {
            E2Bus_start();
	    comm = 0xD1 | (busId<<1);
            E2Bus_send(comm); // MVW3-high request
            check_ack();
            co2_high = E2Bus_read();
            send_ack();
            checksum_03 = E2Bus_read();
            send_nak(); // terminate communication
            E2Bus_stop();
	    if (((comm + co2_high) % 256) == checksum_03) // checksum OK?
	      {
                co2_ee03=co2_low+256*(unsigned int)co2_high;
                // yes-> calculate CO2 value
                co2=co2_ee03;
                // overwrite default (error) value
	  }
    }
        E2Bus_stop();
    }
    return co2;
}

int E2_Wire::offset_read(unsigned char busId)
{
	unsigned char offset_low=read_from(busId, 0x58);
	unsigned char offset_high=read_from(busId, 0x59);
	int offset=0;
	offset=offset_low|(unsigned int)(offset_high<<8);
	return offset;
}

String E2_Wire::readSensorName(unsigned char busId)
{

  char c;
  String retS;

  for (int i = 0 ; i < 10; i ++){
    c = read_from(busId,0xB0+i);
    //    delay(100);
    retS+=c;
    
  }
  return retS;


}

unsigned char E2_Wire::readSensorType(unsigned char busId)

{

  unsigned char retc = 0xFF;
  E2Bus_start();
  unsigned char comm;
  comm = 0x11 | (busId<<1);
  E2Bus_send(comm); // MV3-low request
  if (check_ack()==ACK)
    {
      retc = E2Bus_read();
      send_ack();
      checksum_03 = E2Bus_read();
      send_nak(); // terminate communication
      E2Bus_stop();
      if (((comm + retc) % 256) != checksum_03) retc = 0xFF;
    }
  return retc;

}

char E2_Wire::readFWVer(unsigned char busId)
{


  return read_from(busId,0x00);

}


unsigned char E2_Wire::ReAddress(unsigned char busId, unsigned char newaddress)
{


  if( newaddress > 7 ) {Serial.println("addresses only up to 7");return 0xFF;}
  unsigned char retc = write_to(busId, 0xC0, newaddress) ;
  if (retc == 0 )
    return 0;
  else
    return 0xFF;

}

unsigned char E2_Wire::write_to(unsigned char busId, unsigned char address, unsigned char data) // write to  adress
{
        unsigned char stat_ee03 = 0xFF;
        unsigned char checksum_03;
		unsigned char dma = 0x10 | (busId<<1);
	WriteAgain:
        E2Bus_start(); // start condition for E2-Bus
        E2Bus_send(dma); // main command for set pointer address
	if (check_ack()!=ACK) {
	  Serial.println("failed first");
	  E2Bus_stop();
	  goto WriteAgain;
	  return 0xFF;
	}

        E2Bus_send(address); // adress
	if (check_ack()!= ACK) {
	  Serial.println("failed second");
	  return 0xFF;
	}
                
        E2Bus_send(data); // data
	if (check_ack()!=ACK) {	  Serial.println("failed third");return 0xFF;}
                
        E2Bus_send((address + dma + data) % 256);

	if (check_ack() != ACK) {	  Serial.println("failed fourth");return 0xFF;}

        E2Bus_stop(); // ... and stop condition to terminate
	return 0;
}


unsigned char E2_Wire::write_offset(unsigned char busId, int data) // write to  adress
{

  unsigned int offset = (unsigned int) data;
  unsigned char low = (offset &0xFF);
  unsigned char high = (offset>>8) & 0xFF;
  
  write_to(busId, 0x58, low);
  write_to(busId, 0x59, high);

  Serial.println(low);
  Serial.println(high);
  
  return 0;
  
}



unsigned char E2_Wire::read_from(unsigned char busId, unsigned char address) // read from adress
{
        unsigned char stat_ee03 = 0xFF;
        unsigned char data;
        unsigned char checksum_03;
	unsigned char spa = 0x50 | (busId<<1);
	unsigned char read = 0x51 | (busId<<1);
        E2Bus_start(); // start condition for E2-Bus
        E2Bus_send(spa); //set pointer address
	if (check_ack()!=ACK) {
	  Serial.println("failed first");
	  return 0xFF;
	}

        E2Bus_send(0x00); // always zero
	if (check_ack()!= ACK) {
	  Serial.println("failed second");
	  return 0xFF;
	}
                
        E2Bus_send(address); // address
	if (check_ack()!=ACK) {	  Serial.println("failed third");return 0xFF;}
                
        E2Bus_send((address + spa) % 256);

	if (check_ack() != ACK) {	  Serial.println("failed fourth");return 0xFF;}

        E2Bus_stop(); // stop to terminate comm



//actual read
        E2Bus_start(); // start condition for E2-Bus
        E2Bus_send(read); // command for read address
        if (check_ack()!= ACK) { Serial.println("failed fifth");return 0xFF; }
        data = E2Bus_read(); // read byte
        send_ack();
        checksum_03 = E2Bus_read(); // read checksum
        send_nak(); // NAK
        E2Bus_stop(); // stop to terminate comm

	  // Serial.println(read,HEX);
	  // Serial.println(data,DEC);
	  // Serial.println(checksum_03,DEC);
	  // Serial.println("failed s");

	/*        if (((read + data) % 256) == checksum_03){
         stat_ee03 = data;
        }
	else {
	  Serial.println(read,HEX);
	  Serial.println(data,DEC);
	  Serial.println(checksum_03,DEC);
	  Serial.println("failed s");
	  }*/ //sometimes this checksum does not work...
        return data;
}       
