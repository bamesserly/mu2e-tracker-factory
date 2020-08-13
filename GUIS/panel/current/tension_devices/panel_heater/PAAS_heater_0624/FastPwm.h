#ifndef FastPwm_h
#define FastPwm_h 01Sep19
#include "Arduino.h"

void FastPwmSetup();
void FastPwm(const byte dutyA, const byte dutyB = 0);

#endif