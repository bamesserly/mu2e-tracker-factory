// E2 interface for EE CO2 sensors

// Vadim Rusu -- Fermilab

// ToDO:
// 1) Can I use the Wire library?
// 2) Deal with read failures
// 3) Add gain function




#ifndef E2_INCLUDE_HH
#define E2_INCLUDE_HH
#include"Arduino.h"

class E2_Wire
{
private:
    int _pinSDA;
    int _pinSCL;
    char check_ack(void);
    void send_ack(void);
    void send_nak(void);
    void E2Bus_start(void); 
    void E2Bus_stop(void); 
    void E2Bus_send(unsigned char);
    void set_SDA(void);
    void clear_SDA(void);
    int read_SDA(void);
    void set_SCL(void);
    void clear_SCL(void);
    unsigned char E2Bus_read(void); 
    void EEdelay(unsigned int value);
public:
    E2_Wire(int pinSDA, int pinSCL);
    unsigned char Status(unsigned char);
    float CO2_read(unsigned char);
    int E2_Wire::offset_read(unsigned char busId);
    unsigned char read_from(unsigned char sensor, unsigned char address); // read from adress
    unsigned char write_to(unsigned char busId, unsigned char address, unsigned char data); // write to  adress
    unsigned char ReAddress(unsigned char busId, unsigned char newaddress);
    String readSensorName(unsigned char);
    char readFWVer(unsigned char busId);
    unsigned char readSensorType(unsigned char);
    unsigned char write_offset(unsigned char busId, int data); // write the offset
};


#endif
