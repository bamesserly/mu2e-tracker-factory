// jfMeter.ino
//
// Cole Kampa, Aina Zulkifli, Luiz Fernando Andrade, Nick Elscott, Jean-Francois
// Caron
//
// v2.1
//
// description: used for measuring pin-pin and straw-straw resistances in the
// completed panels hardware: at-08 buzzer, 150 Ohm reference resistor, LCD
// Shield,  2 Probes, 1 Button(Main)
//
//
// pin chart:
// buzzer: + pin to dig12, gnd to gnd --- OK
// ohmmeter: probe 1 (black banana jack) to +5V, probe 2 (red banana jack) to
// A0/ reference resistor:150 ohm main button: + pin to dig3, gnd to gnd.
//
//
// How to use it:
// Change position with: LEFT(-1) and RIGHT(+1) buttons and UP(48) and DOWN(0)
// buttons. Switch between wire and straw with: SELECT button. Take measurement
// with: MAIN button(attached to red probe) Measurement order: Straw -> Wire

#include <Adafruit_RGBLCDShield.h>
#include <Wire.h>
#include <avr/interrupt.h>
#include <math.h>
#include <utility/Adafruit_MCP23017.h>

// Define pin numbers
#define mainButton 3  // pin for the measurement button, PCINT19, in Port D
#define buzzerPin 12  // set to an output pin below
#define ADCPin 0      // no need to declare input/output for analog pins
#define ledPin 13     // set a pin for the LED indicator

// Uncomment this if you want to silence the beeps.
//#define DISABLEBEEP

// Initialize object for lcd
Adafruit_RGBLCDShield lcd = Adafruit_RGBLCDShield();

// Number of straw/wire positions.
const int max_count = 96;

float strawMeasurements[max_count];
float wireMeasurements[max_count];
int counter = 0;           // keeps track of the straw/wire index
bool at_wire = false;      // keeps track of whether we are at a wire or a straw
bool straws_only = false;  // only measure straws

// This flag is set when the mainButton gets pushed, in an interrupt.
volatile bool buttonPushed = false;

// These values are used to prevent high-rate button pushes.
unsigned long last_button_time = 0;
const unsigned long button_timeout = 100000;  // microseconds

// This struct is made to hold the parameters of a beep.
struct Beep {
  int freq;  // Frequency of beep (Hz)
  int num;   // Number of beeps
  int dur;   // Duration of each beep (ms)
};

// Now I define three beeps for use in the program.
const Beep low_beep{
    200, 3, 100};  // Beep for a measurement that is below the acceptable range.
const Beep high_beep{
    500, 3, 100};  // Beep for a measurement that is above the acceptable range.
const Beep unstable_beep{300, 3,
                         100};  // Beep for a measurement with large variance.
const Beep good_beep{300, 1, 500};  // Beep that is within the acceptable range.

const int num_meas = 100;  // number of measurements to make
// delay (milliseconds) between measurements...total measurement time should be
// ~ num_meas * meas_delay
const int meas_delay = 3;
const float resistance_ref = 149.8;  // value of reference resistor in ohms

// Constants for resistance ranges.
// Wire resistances must be within a certain fractional range of these values.
// NOTE: the numbers are written with decimal places, but to save memory I am
// using unsigned char Unsigned char ranges from 0-255, so this is OK here, but
// make sure to use a float for calculations.
const unsigned char wires_nominal[max_count] = {
    149.02, 148.57, 148.12, 147.66, 147.20, 146.73, 146.25, 145.77, 145.29,
    144.79, 144.30, 143.79, 143.28, 142.77, 142.25, 141.72, 141.19, 140.65,
    140.10, 139.55, 138.99, 138.42, 137.85, 137.27, 136.68, 136.09, 135.49,
    134.88, 134.27, 133.64, 133.01, 132.38, 131.73, 131.08, 130.42, 129.75,
    129.07, 128.38, 127.68, 126.98, 126.27, 125.54, 124.81, 124.07, 123.32,
    122.56, 121.78, 121.00, 120.21, 119.40, 118.59, 117.76, 116.92, 116.07,
    115.20, 114.33, 113.44, 112.53, 111.61, 110.68, 109.73, 108.77, 107.79,
    106.80, 105.79, 104.76, 103.71, 102.64, 101.56, 100.45, 99.32,  98.17,
    97.00,  95.80,  94.58,  93.33,  92.06,  90.75,  89.41,  88.04,  86.64,
    85.19,  83.71,  82.19,  80.62,  79.00,  77.32,  75.59,  73.80,  71.93,
    69.99,  67.96,  65.83,  63.59,  61.21,  58.69};
const float wires_range = 0.2;  // Must be within 20%.
const float straws_range =
    1.0;  // Straws must be within 100% of the wire nominal value (ad-hoc)
const float max_variance = 10;  // highest acceptble variance of any measurement
                                // sequence (ADC counts squared)

// This function returns -1/0/1 if the resistance is below/within/above the
// valid range for the wire or straw at the given index.
int check_resistance(float resistance, int index, bool wire) {
  float range;
  if (wire)
    range = wires_range;
  else
    range = straws_range;

  float upper = wires_nominal[index] * (1 + range);
  float lower = wires_nominal[index] * (1 - range);

  if (resistance < lower)
    return -1;
  else if (resistance > upper)
    return 1;
  else
    return 0;
}

char inByte;  // variable to store serial input from user or python code

float amb_resistance;

void setup() {
  // Set the lcd screen
  lcd.begin(16, 2);
  lcd.print(F("Mu2e Panel QC"));
  lcd.setCursor(0, 1);
  lcd.print(F("ResistanceTester"));
  lcd.cursor();
  lcd.blink();

  // Continue setting up while LCD welcome screen is shown.

  // Set pins for buzzer and probe button.
  pinMode(buzzerPin, OUTPUT);  // set buzzer (digital pin 12) to an output pin
  pinMode(mainButton, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);  // set pin 13 as output

  // Enable "pin-change interrupt" on pin mainButton.
  cli();                 // Disable interrupts.
  PCICR |= 0b00000100;   // turn on port 4/port D?
  PCMSK2 |= 0b00001000;  // turn on pin 8?
  sei();                 // Re-enable interrupts.

  // Initialize the measurement arrays.
  for (int i = 0; i < max_count; i++) {
    wireMeasurements[i] =
        0.0 /
        0.0;  // Initializing to NaN to differentiate 0.0 ohms from blanks.
    strawMeasurements[i] = 0.0 / 0.0;
  }

  Serial.begin(115200);  // start the USB serial connection

  // Parse straws-only mode
  // Wait up to 3 seconds for input from the python prog
  while (!Serial.available() && millis() < 3000) {
  }
  char straw_mode = Serial.read();  // 's' will trigger straws-only mode
  if (straw_mode == 's') {
    straws_only = true;
  }

  Serial.print(F("# Position, wire/straw, ADC values..., resistance, PASS?\n"));

  // Delay a little bit, so the welcome screen is visible to humans.
  delay(1000);
  lcd.clear();
  draw_LCD();
}

void loop() {
  ambient_resistance();

  // This flag can be set in multiple places to make a measurement happen.
  bool do_measurement = false;

  // buttonPushed gets set in the interrupt when the probe button is pushed.
  if (buttonPushed) {
    // Only react to buttonPushed if it hasn't been pushed in button_timeout.
    unsigned long now = micros();
    if ((now - last_button_time) > button_timeout) {
      do_measurement = true;
      last_button_time = now;
    }
  }

  if (Serial.available() > 0) {
    inByte = Serial.read();  // reads the incoming data, an 'r' will trigger a
                             // measurement.
    if (inByte == 'r') {
      do_measurement = true;
    }
  }

  // Read built-in buttons on the LCD shield.
  uint8_t buttons = lcd.readButtons();

  if (buttons)  // check to see if LCD buttons were pressed.
  {
    // Only react to buttons if they haven't been pushed in button_timeout.
    unsigned long now = micros();
    if ((now - last_button_time) > button_timeout) {
      if (buttons & (BUTTON_UP | BUTTON_DOWN | BUTTON_LEFT | BUTTON_RIGHT)) {
        at_wire = false;
      }
      if (buttons & BUTTON_UP) {
        counter = max_count / 2;
      }
      if (buttons & BUTTON_DOWN) {
        counter = 0;
      }
      if (buttons & BUTTON_LEFT) {
        // Decrement counter, but wrap back up to max_count from zero.
        counter = counter - 1;
        counter = (counter < 0) ? (max_count - 1) : counter;
      }
      if (buttons & BUTTON_RIGHT) {
        // Increment counter, but wrap back to zero after max_count.
        counter = (counter + 1) % max_count;
      }

      if (buttons & BUTTON_SELECT) {
        at_wire = !at_wire;
      }
      lcd.clear();
      draw_LCD();
      last_button_time = now;
    }
  }

  if (do_measurement) {
    bool valid = manage_measurement();
    draw_LCD();
    if (at_wire) {  // Give enough time for the users to see the screen before
                    // it changes to the next counter.
      delay(1000);
    }

    // check_resistance returns -1/0/+1 for below/within/above valid resistance
    // range.
    // bool valid = !bool(check_resistance(resistance, counter, at_wire));

    if (valid) {
      if (straw_mode) {
        counter = (counter + 2) % max_count;  // in straw mode, increment by 2
      } else {
        counter =
            (counter + at_wire) %
            max_count;  // increase counter if we're at_wire, wrap from 95 to 0.
        at_wire = !at_wire;  // Toggle at_wire
      }
    }
    lcd.clear();
    draw_LCD();

    buttonPushed = false;
  }
}  // ends the loop

void ambient_resistance() {
  digitalWrite(ledPin, LOW);
  unsigned int amb_rawADC = analogRead(ADCPin);
  amb_resistance = resistance_ref * (1023 / (1.0 * amb_rawADC) - 1);

  if (amb_rawADC != 0 and amb_rawADC != 1023) {
    digitalWrite(ledPin, HIGH);
  }

  draw_LCD();
  delay(250);
}

float variance;  // global variable used for getting the variance out of the
                 // measure_sequence() function.

bool manage_measurement() {
  Serial.print(counter);
  Serial.print(F(", "));
  Serial.print(at_wire);
  Serial.print(F(", "));

  // Do a sequence of measurements
  // we must use long rather than int because int has a maximum value
  // of 65,536. 100 measurements could yield a value of up to 102,300!
  unsigned long adc_total = 0;
  unsigned long adc_sum_of_squares = 0;
  float adc_square_of_means;
  float adc_mean_of_squares;
  float adc_variance;
  bool good_measurement;

  int i = 0;
  // Do num_meas measurements and sum them into a total.
  while (i < num_meas) {
    unsigned int rawADC = analogRead(ADCPin);
    Serial.print(rawADC);
    Serial.print(F(", "));  // print every individual measurement to Serial.

    adc_total += rawADC;
    adc_sum_of_squares += ((unsigned long)rawADC) * ((unsigned long)rawADC);
    i++;
    delay(meas_delay);
  }

  adc_mean_of_squares = adc_sum_of_squares / (1.0 * num_meas);
  adc_square_of_means =
      (adc_total / (1.0 * num_meas)) * (adc_total / (1.0 * num_meas));
  adc_variance =
      fabs(adc_mean_of_squares - adc_square_of_means);  // variance calculation
  // variance = resistance_ref*((1023/(1.0*adc_variance)) - 1);

  // Serial.println("");
  //  Serial.println("");
  //  Serial.print("sum of squares (ADC): ");
  //  Serial.println(adc_sum_of_squares);
  //  Serial.print("mean of squares (ADC): ");
  //  Serial.println(adc_mean_of_squares);
  //  Serial.print("square of means (ADC): ");
  //  Serial.println(adc_square_of_means);
  //  Serial.print("adc variance: ");
  //  Serial.println(adc_variance);
  //  Serial.print("regular variance: ");
  //  Serial.println(variance);
  //  Serial.println("");

  float resistance = resistance_ref * (1023 / (1.0 * adc_total / num_meas) - 1);

  Serial.print(resistance);
  Serial.print(F(", "));

  // Store measurements into our arrays.
  if (at_wire == false) {
    strawMeasurements[counter] = resistance;
  } else if (at_wire == true) {
    wireMeasurements[counter] = resistance;
  }

  int lowokhigh = check_resistance(resistance, counter, at_wire);
  // Determine which beep to be used, and print status
  if (lowokhigh == -1) {  // low resistance
    beep(low_beep);
    Serial.print(F("LOW"));
    good_measurement = false;   // this is a bad measurement
  } else if (lowokhigh == 1) {  // high resistance
    beep(high_beep);
    Serial.print(F("HIGH"));
    good_measurement = false;
  } else if (adc_variance >
             max_variance) {  // for measurements with high variance
    beep(unstable_beep);
    Serial.print(F("UNSTABLE"));
    good_measurement = false;
  } else {  // if we make it this far into the loop, we know the resistance is
            // 'acceptable'
    beep(good_beep);
    Serial.print(F("PASS"));
    good_measurement = true;
  }
  Serial.print(F("\n"));

  return good_measurement;
}

void beep(const Beep& the_beep) {
// The #ifndef block here will disable this code if the DISABLEBEEP macro is set
#ifndef DISABLEBEEP
  for (int i = 0; i < the_beep.num;
       i++) {  // loop through however many times we want to beep
    tone(buzzerPin, the_beep.freq);  // turn the buzzer on at a given frequency
    delay(the_beep.dur);  // keep the buzzer on for the beep duration (in
                          // milliseconds)
    noTone(buzzerPin);    // turn the buzzer off
    delay(the_beep.dur);  // keep the buzzer off for the beep duration
  }
#endif
}

void draw_LCD() {
  lcd.setCursor(0, 0);
  lcd.print(F("P: "));
  lcd.print(counter);
  lcd.setCursor(0, 1);
  lcd.print(F("S: "));
  lcd.print(format(strawMeasurements[counter]));
  lcd.setCursor(8, 0);
  lcd.print(F("R: "));
  lcd.print(format(amb_resistance));
  lcd.setCursor(8, 1);
  lcd.print(F("W: "));
  lcd.print(format(wireMeasurements[counter]));
  // We leave the flashing cursor on top of the S or W depending on at_wire.
  lcd.setCursor(8 * at_wire, 1);
}

// This function formats a float for printing with 5 characters.
// It only works for val < 100000.
String format(float val) {
  if (isnan(val)) return String("NaN  ");
  if (isinf(val)) return String("Inf  ");

  int ndecimals = 0;
  if (val < 10) ndecimals = 3;
  if (val < 100) ndecimals = 2;
  if (val < 1000) ndecimals = 1;

  return String(val, ndecimals);
}

// Interrupt service routine for mainButton push.
ISR(PCINT2_vect) {
  // This interrupt fires on any change of the button input (LOW->HIGH or
  // HIGH->LOW), but we only want to react when it was a HIGH->LOW transition.
  if (digitalRead(3) == LOW) {
    buttonPushed = true;
  }
}
