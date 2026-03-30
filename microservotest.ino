#include <Servo.h>

Servo s;

const int SERVO_PIN = 2;

// Adjust these if your servo orientation is different:
const int CENTER = 90;
const int LEFT   = 0;    // 90° left from center
const int RIGHT  = 180;  // 90° right from center

void setup() {
  s.attach(SERVO_PIN);
  s.write(CENTER);
  delay(500);

  // Optional: open Serial Monitor at 9600 baud if you want
  // to type L or R to move the servo.
  Serial.begin(9600);
  Serial.println("Type L for left, R for right, C for center");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == 'L' || cmd == 'l') {
      s.write(LEFT);
      delay(500);
    } 
    else if (cmd == 'R' || cmd == 'r') {
      s.write(RIGHT);
      delay(500);
    }
    else if (cmd == 'C' || cmd == 'c') {
      s.write(CENTER);
      delay(500);
    }
  }
}
