//#include <ESP32Servo.h>
#include <Bluepad32.h>

ControllerPtr myController = nullptr;  // initialze controller pointer to None

// callback to assign controller pointer location, for controller connection
void onConnected(ControllerPtr ctl) {
  if (myController == nullptr) {
    Serial.println("Controller Connected");
    myController = ctl;
  }
}

void onDisconnected(ControllerPtr ctl) {
    if (myController == ctl) {
        Serial.println("Controller Disconnected");
        myController = nullptr;
    }
}

void setup() {
    Serial.begin(115200);
    BP32.setup(&onConnected, &onDisconnected); // tells library exact address of functions
}

// Receives controller data and processes the inputs
void loop() {
    BP32.update(); // checks for bluetooth data packets
    if (myController && myController->isConnected()) { // Pass myController to function
        processInputs(myController);
    }
    delay(10); // 10ms delay
}

void processInputs(ControllerPtr ctl) {
    // DIGITAL BUTTONS
    if (ctl->a())
        Serial.println("Button A Pressed");
    if (ctl->b())
        Serial.println("Button B Pressed");
    if (ctl->x())
        Serial.println("Button X Pressed");
    if (ctl->y())
        Serial.println("Button Y Pressed");
    

    // ANALOG JOYSTICKS (-511 to 511)
    int32_t stickX = ctl->axisX();
    int32_t stickY = ctl->axisY();

    // TRIGGERS (Brake and Throttle) (0 to 1023)
    int32_t leftTrigger = ctl->brake();    // LT
    int32_t rightTrigger = ctl->throttle(); // RT

    if (leftTrigger > 0 || rightTrigger > 0) {
        Serial.printf("Triggers: LT=%d, RT=%d\n", leftTrigger, rightTrigger);
    }

    // DPAD
    uint8_t dpad = ctl->dpad();
    if (dpad & DPAD_UP) Serial.println("DPAD Up");
    if (dpad & DPAD_DOWN) Serial.println("DPAD Down");
    if (dpad & DPAD_RIGHT) Serial.println("DPAD Right");
    if (dpad & DPAD_LEFT) Serial.println("DPAD Left");
}