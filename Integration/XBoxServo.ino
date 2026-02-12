#include <Bluepad32.h>
#include <ESP32Servo.h>

// Pin configuration
const int SERVO_PIN = 10;

// Only 2 positions needed
const int TRASH = 45;       // Adjust after testing
const int RECYCLE = 135;    // Adjust after testing

// Global objects
Servo gateServo;
GamepadPtr controller;

// Controller callbacks
void onConnectedController(GamepadPtr gp) {
    controller = gp;
    Serial.println("Xbox Controller Connected!");
    Serial.println("D-Pad LEFT = TRASH  |  D-Pad RIGHT = RECYCLE");
}

void onDisconnectedController(GamepadPtr gp) {
    controller = nullptr;
    Serial.println("Controller Disconnected");
}

void setup() {
    Serial.begin(115200);
    Serial.println("Trash/Recycle Sorter");
    
    // Initialize Bluepad32
    BP32.setup(&onConnectedController, &onDisconnectedController);
    BP32.forgetBluetoothKeys();
    
    // Initialize servo
    gateServo.attach(SERVO_PIN);
    gateServo.write(TRASH);  // Start at trash position
    
    Serial.println("Ready! Waiting for controller...");
}

void loop() {
    BP32.update();
    
    if (controller && controller->isConnected()) {
        
        // Get D-Pad state
        uint8_t dpad = controller->dpad();
        
        // D-Pad LEFT = TRASH
        if (dpad == 0x08) {  // DPAD_LEFT
            gateServo.write(TRASH);
            Serial.println("TRASH");
        }
        
        // D-Pad RIGHT = RECYCLE
        else if (dpad == 0x02) {  // DPAD_RIGHT
            gateServo.write(RECYCLE);
            Serial.println("RECYCLE");
        }
    }
    
    delay(15);
}
