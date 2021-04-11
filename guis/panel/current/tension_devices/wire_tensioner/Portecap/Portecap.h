#ifdef Portecap_h
#else
#define Portecap_h 7Feb19
class Portecap {
private:
	signed short whereAmI;		// position, in 1/8th steps
	unsigned char stepSize;		// change in position per step
	signed short direction;		// above including sign for direction
public:
	signed char Reset(short steps = -1);
	signed char Step(short steps = 1);
	signed char SetDir(const char* d);
	signed char Power(const char i);
	signed char SetStep(unsigned char s);
    signed short Position() {
		return whereAmI;
	}
};
#endif
