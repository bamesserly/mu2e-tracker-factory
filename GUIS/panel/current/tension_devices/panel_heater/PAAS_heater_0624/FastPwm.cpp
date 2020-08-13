#include "FastPwm.h"
void FastPwmSetup() {
	// Set timer to asynchronous input, divide by 1.5 (too fast otherwise)
	byte pllfrq = PLLFRQ;
	pllfrq &= 0b11001111;
	pllfrq |= 0b00100000;
	PLLFRQ = pllfrq;
	// Using only 8 bits so zero shared upper 2 bit register
	TC4H = 0;

  byte tccr4a;
	tccr4a = 0b10000010 |   // COM4A1..0 = 10 (clear on match), OC4A pin connected
             0b00100001;    	// COM4B1..0 = 10 (clear on match), OC4B pin connected
	TCCR4A = tccr4a;
	// No inversion, no prescale, start TC4
	TCCR4B = 0b00000001;
	// Set COM4 shadow bits same as non-shadow
	TCCR4C = 0b11110000 & tccr4a;
	// Diable various fault interupts, set mode to fast PWM
	TCCR4D = 0;
	// No lock, no enhanced mode
	TCCR4E = 0;
	// Cycle at 255
	OCR4C = 255;
	// Zero duty cycle on A and B
	OCR4A = 0;
	OCR4B = 0;
	// No interrupts
	TIMSK4 = 0;
  // TIMER4 COM pins as output
  pinMode(10,OUTPUT);
	pinMode(13,OUTPUT);
}

void FastPwm(byte dutyA, byte dutyB) {
	OCR4A = dutyA;
	OCR4B = dutyB;
}
