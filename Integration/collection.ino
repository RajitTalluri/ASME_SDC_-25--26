#include <Servo.h>

Servo myServo;

const int buttonPin = 2;   // Button connected to pin 2
bool isOpen = false;       // Start closed

void setup() {
  myServo.attach(9);       // Servo signal wire on pin 9
  pinMode(buttonPin, INPUT_PULLUP);  // Button connected to GND
  myServo.write(0);        // Start closed
}

void loop() {
  if (digitalRead(buttonPin) == LOW) {  // Button pressed
    delay(200);  // Simple debounce
    if (!isOpen) {
      myServo.write(180);  // Open
      isOpen = true;
    } else {
      myServo.write(0);    // Close
      isOpen = false;
    }
    while (digitalRead(buttonPin) == LOW); // Wait until button released
  }
}
