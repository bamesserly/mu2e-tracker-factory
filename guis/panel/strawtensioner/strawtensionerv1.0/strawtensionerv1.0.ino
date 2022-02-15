//strawtensionerv1.0.ino
//          v1.0
//      Dylan Frikken
//    <frikk009@umn.edu>
//
//  this device is used to pull the straws to tension, alerting the user the straw is
//  in the acceptable range and reports the straws initial tension with uncertainty
//  
//  required libraries: "VernierLib.h" Sketch -> Include Library -> Manage Libraries.. -> search vernier
//                      "RunningAverage.h" download from https://github.com/RobTillaart/Arduino
//                       all the pin change interupt libraries -> manage libraries search pinchangeinterrupt

#include "VernierLib.h" //include Vernier functions in this sketch
#include "RunningAverage.h" //include library used to calculate averages used for slope, initial tension and uncertainty

//below section includes the necessary libraries to allow D12 to be an interuptable pin
#include <PinChangeInterrupt.h>
#include <PinChangeInterruptBoards.h>
#include <PinChangeInterruptPins.h>
#include <PinChangeInterruptSettings.h>

VernierLib Vernier; //create an instance of the VernierLib library

#define button 12 //D12 button to reset for next straw
#define buzzerpin 13 //piezo buzzer pin
#define freq_good 320 //buzz frequency (hz)

float sensorReading; //create global variable to store sensor reading
float zero; //global to hold offset to zero sensor
int buttonstate=0; 

RunningAverage x(5);   // to store x data (time) 
RunningAverage y(5);   // to store y data (analog sensor output)
RunningAverage xy(5);  // to store x*y, needed for slope calculation
RunningAverage x2(5);  // to store x*x, needed for slope calculation
RunningAverage av(25); //used to store values to determine the initial tension

float lastaverage; //global to hold the last average group to be used when the tension is released (initial straw tension)
float lastavstddev; //global to hold the last average's std dev for uncertainty
float slope=0; //global to hold slope values
char user_input; //global to hold the user input from the GUI buttons

void setup() {
  Serial.begin(9600); //setup communication to display
  Vernier.autoID(); //identify the sensor being used

//============use this section to troubleshoot calibration =========
 zero = -1.3; //change to match constant offset. value from zeroing in horizontal position
//  zero = Vernier.readSensor(); //find the offset to zero the sensor
//  Serial.print("The offset value is ");
//  Serial.print(101.97*zero);
//  Serial.println(" grams"); 
  
  pinMode(button, INPUT_PULLUP); //setup the D12 button
  pinMode(LED_BUILTIN, OUTPUT); //setup the led 
  pinMode(buzzerpin, OUTPUT); //initialize buzzer
  attachPinChangeInterrupt(button, ButtonPress, LOW); //allows pressing D12 to interrupt the loop
  
  // explicitly start averages clean  
  x.clear(); 
  y.clear();
  xy.clear();
  x2.clear();
  av.clear();
  
}//end void setup

void loop() {
  buttonstate = digitalRead(button); 
  
  sensorReading = Vernier.readSensor() - zero; //read one data value
  float yn = sensorReading *1.000;  // individual sensor lecture (y variable)
  float xn = millis() / 1000.000; // corresponding x time variable (seconds) 
  
  y.addValue(yn);          // add y variable to storing array 
  x.addValue(xn);          // add x variable to storing array
  xy.addValue(xn * yn);    // same for x*y  
  x2.addValue(xn * xn);   // same for x*x
  

  if(x2.getCount() < 5) {
//    Serial.print("filling time window... n = ");
//    Serial.println(x2.getCount()); 
  }

  else{    
    // Slope equation (simple regression):
    slope = (xy.getAverage()-(x.getAverage()*y.getAverage()))/(x2.getAverage()-(x.getAverage()*x.getAverage()));

    if( slope <= - 9.0){ //look for a downward slope from releasing the tension, this may need to be adjusted, depending on sensitivity.
        Serial.print("end");
        Serial.print(" ");
        Serial.print(101.97*lastaverage);
        Serial.print(" "); 
        Serial.println(101.97*lastavstddev);
        Serial.flush();
        noTone(buzzerpin);          
      
        while(buttonstate ==HIGH){ //this part holds the script until the user presses next straw button in GUI or presses D12
          buttonstate = digitalRead(button);
          user_input = Serial.read();
          
          if(user_input == '1'){ //if user presses next straw, clear averages and break the while loop
            x.clear(); 
            y.clear();
            xy.clear();
            x2.clear();
            av.clear();
            break;
          }
        Serial.flush();
        delay(100);
      }//end while
    }//end if slope
    
    Serial.print("reading ");
    Serial.print(101.97*sensorReading); //print data value 
    Serial.print(" "); //print a space so the string will be split
    Serial.println(101.97*lastavstddev);
    Serial.flush();
    delay(50); //this delay controls the sample rate
    
    if( sensorReading >= 6.37 && sensorReading <= 8.336){ //this range is the acceptable range for initial straw tension
      digitalWrite(LED_BUILTIN, HIGH); //turn on led when in acceptable range
      tone(buzzerpin,freq_good); //buzz while in accceptable range
    }//end if sensor reading
    
    else {  //while out of acceptable range
      digitalWrite(LED_BUILTIN, LOW);
      noTone(buzzerpin);
    }//end out of sensor range
    
    lastaverage=av.getAverage(); //store the last group of 25 average
    lastavstddev = av.getStandardDeviation(); //last 25 std dev
    av.addValue(yn);        //used to fill last 25 values
  }//end else for filling average lists

//watch for D12 button to be pressed, if pressed clear the running averages and return to the loop
  if (buttonstate== LOW){
        x.clear(); 
        y.clear();
        xy.clear();
        x2.clear();
        av.clear();
        return;
  }//end if button pressed  
   
}// end void loop

// button interrupt
void ButtonPress() {
  buttonstate = 1;
}//end void buttonpress
