#include <Arduino.h>
#include "Portecap.h"

static const unsigned char stp = 12;  //a pulse to this pin tells the motor to "step"
static const unsigned char dir = 9;  //direction of motor (extend/retract)
static const unsigned char MS1 = 8;  //MS1 & 2 control step mode/size
static const unsigned char MS2 = 11;
static const unsigned char EN = 10;  //enable (low=on state)

static const signed short range = 8 * 500;	//number of steps to go from full retract to full extend
static const unsigned short badRegion = 10; // nonlinear end effect

// Motor reset.
// Call before using motor, and any time later to put the motor at the fully forward position.
// Argument:
//	0: just set up pins, do not move motor
//	<0: (default) move motor all the way forward
// 	>0: move motor forward "steps" steps
// 	In all cases, if the motor hits the upper limit, it will back up "vadRegion" steps
// Returns: always zero
signed char Portecap::Reset(short steps) {
	// Set up pins
	pinMode(stp, OUTPUT);
	pinMode(dir, OUTPUT);
	pinMode(MS1, OUTPUT);
	pinMode(MS2, OUTPUT);
	pinMode(EN, OUTPUT);
	// Set up motor
	SetStep(1);
	Power(1);
	// Default is to ignore where we think we are, and move all the way forward
	if (steps < 0) {	// Default is to ignore where we think we are
		steps = range;
		whereAmI = range;
	}
	// Move forward
	SetDir("PUSH");
	signed char atLimit = Step(steps);
	// Back up a little to avoid end effects
	SetDir("PULL");
	if (atLimit)
		Step(badRegion);
	Power(0);
	return 0;
}

// Step motor specified number of times
// Argument:
//	Number of steps to make
// Returns:
//	0: specified number of steps made
//	+1: hit upper limit before making specified number of steps
//	-1: hit lower limit before making specified number of steps
signed char Portecap::Step(short steps) {
	if (steps <= 0)
		return 0;
	signed char err = 0;
	// Make the steps by pulsing the stp pin
	for (int i = steps; i--; ) {
		if (whereAmI<0 && direction<0) {
			err = -1;
			break;
		}
		if (whereAmI>range && direction>0) {
			err = +1;
			break;
		}
		digitalWrite(stp, HIGH); //Trigger one step
		delay(1);
		digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
		delay(5);
		whereAmI += direction;
	}
	return err;
}

// Set step direction
// Argument:
//	"PUSH": move forward
//	"PULL": move backward
// Returns:
//	0: success
//	1: invalid argument, no action taken
signed char Portecap::SetDir(const char* d) {
	signed char err = 0;
	if (strcmp(d,"PULL")==0) {
		digitalWrite(dir, LOW);
		direction = stepSize;
	}
	else if (strcmp(d, "PUSH") == 0) {
		digitalWrite(dir, HIGH);
		direction = -stepSize;
	}
	else
		err = 1;
	return err;
}

signed char Portecap::Power(const char i) {
	digitalWrite(EN, i==0);
	return 0;
}

// Set step size
// Argument:
//	1: full step
//	2: 1/2 step
//	4: 1/4 step
//	8: 1/8th step
// Returns:
//	0: success
//	1: invalid argument, no action taken
signed char Portecap::SetStep(unsigned char s) {
	signed char err = 0;
	switch (s) {
	case 1:
		digitalWrite(MS1, LOW);
		digitalWrite(MS2, LOW);
		stepSize = 8;
		break;
	case 2:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, LOW);
		stepSize = 4;
		break;
	case 4:
		digitalWrite(MS1, LOW);
		digitalWrite(MS2, HIGH);
		stepSize = 2;
		break;
	case 8:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, HIGH);
		stepSize = 1;
		break;
	default:
		err = 1;
	}
	return err;
}
