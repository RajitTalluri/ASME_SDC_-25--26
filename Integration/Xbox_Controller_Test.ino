#include <Arduino.h>
#include <BLEGamepadClient.h>
#include <ESP32Servo.h>

XboxController controller;

Servo myServo;   // create servo object

void setup(void) {
// Setup ESP32 Pin 2 For Servo
    myServo.attach(2);
    myServo.write(90);

// Setup Controller
  Serial.begin(115200);
  controller.begin();
}

void loop() {
  if (controller.isConnected()) {
    XboxControlsEvent e;
    controller.read(&e);

    // If A button pressed, toggle servo
    if (e.buttonA) {
      Serial.println("A pressed");
      myServo.write(180);
      delay(500);
      myServo.write(90);
    }

  } else {
    Serial.println("controller not connected");
  }
  delay(100);
}