#include <Servo.h>

static const int servoPin = 13;

Servo servo1;
boolean stopper = 1;
int counter = 0;

void setup() {
    Serial.begin(115200);
    servo1.attach(servoPin);
}

void loop() {

  if (stopper==0){

    for(int posDegrees = 0; posDegrees <= 180; posDegrees++) {
        servo1.write(posDegrees);
        Serial.println(posDegrees);
        delay(20);
    }

    for(int posDegrees = 180; posDegrees >= 0; posDegrees--) {
        servo1.write(posDegrees);
        Serial.println(posDegrees);
        delay(20);
    }
    counter+=1;
    
    if (counter>3){
      stopper=1;
    }

    Serial.print(F("The counter is: "));
    Serial.write(counter);

  }
}