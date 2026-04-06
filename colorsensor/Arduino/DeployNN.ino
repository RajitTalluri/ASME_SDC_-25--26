#include <Bluepad32.h>
#include <ESP32Servo.h>

ControllerPtr myController;

// DEADZONES
int leftStickDzone = 50; // adjust as needed
int rightStickDzone = 50; // adjust as needed
int leftTriggerDzone = 50; // adjust as needed
int rightTriggerDzone = 50; // adjust as needed

// DRIVETRAIN - L298n MOTOR COTNROL
int LFmotorpin1 = 1; // In 1 pin
int LBmotorpin2 = 2; // In 2 pin
int LmotorENA = 3; // PWM, 3 pin

int RFmotorpin1 = 4; // In 3 pin
int RBmotorpin2 = 5; // In 4 pin
int RmotorENA = 6; // PWM, 6 pin (21)

int Collectionmotorpin1 = 15; // In 5 pin
int Collectionmotorpin2 = 16; // In 6 pin
int CollectionmotorENA = 17; // PWM 3 pin
int CollectionmotorSpeed = 255; // adjust as needed

// SERVOS
Servo grabberServo;
int grabberServoPin = 21; // find compatible pin
Servo sorterServo;
int sorterServoPin = 47; // find compatible pin


// MOTOR HELPER FUNCTIONS
void ALLMotorSTOP(int maxSpeed) {
  digitalWrite(LFmotorpin1, LOW);
  digitalWrite(LBmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed);
  
  digitalWrite(RFmotorpin1, LOW);
  digitalWrite(RBmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed);
}


void leftPIVOT(int pivotSpeed) {
  digitalWrite(LFmotorpin1, HIGH); // L backward
  digitalWrite(LBmotorpin2, LOW);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(RFmotorpin1, HIGH); // R forward
  digitalWrite(RBmotorpin2, LOW);
  analogWrite(RmotorENA, pivotSpeed);
}


void rightPIVOT(int pivotSpeed) {
  digitalWrite(LFmotorpin1, LOW); // L forward
  digitalWrite(LBmotorpin2, HIGH);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(RFmotorpin1, LOW); // R backward
  digitalWrite(RBmotorpin2, HIGH);
  analogWrite(RmotorENA, pivotSpeed);
}


void setMotors(int leftSpeed, int rightSpeed) {
  if (leftSpeed > leftStickDzone) {
    digitalWrite(LFmotorpin1, LOW); // L forward
    digitalWrite(LBmotorpin2, HIGH);
    analogWrite(LmotorENA, leftSpeed);
  } else if (leftSpeed < -leftStickDzone) {
    digitalWrite(LFmotorpin1, HIGH); // L backward
    digitalWrite(LBmotorpin2, LOW);
    analogWrite(LmotorENA, -leftSpeed);
  } else {
    digitalWrite(LFmotorpin1, LOW);
    digitalWrite(LBmotorpin2, LOW);
    analogWrite(LmotorENA, 0);
  }


  if (rightSpeed > rightStickDzone) {
    digitalWrite(RFmotorpin1, HIGH); // R forward
    digitalWrite(RBmotorpin2, LOW);
    analogWrite(RmotorENA, rightSpeed);
  } else if (rightSpeed < -rightStickDzone) {
    digitalWrite(RFmotorpin1, LOW); // R backward
    digitalWrite(RBmotorpin2, HIGH);
    analogWrite(RmotorENA, -rightSpeed);
  } else {
    digitalWrite(RFmotorpin1, LOW);
    digitalWrite(RBmotorpin2, LOW);
    analogWrite(RmotorENA, 0);
  }
}


void onConnectedController(ControllerPtr ctl) {
  myController = ctl;
  Serial.println("Xbox controller connected");
}


void onDisconnectedController(ControllerPtr ctl) {
  myController = nullptr;
  Serial.println("Controller disconnected");
}


void setup() {
  Serial.begin(115200);
  delay(2000);
  BP32.setup(&onConnectedController, &onDisconnectedController);
  BP32.forgetBluetoothKeys();
  Serial.println("Waiting for controller...");

  pinMode(LFmotorpin1, OUTPUT);
  pinMode(LBmotorpin2, OUTPUT);
  pinMode(LmotorENA, OUTPUT);
  pinMode(RFmotorpin1, OUTPUT);
  pinMode(RBmotorpin2, OUTPUT);
  pinMode(RmotorENA, OUTPUT);
  pinMode(Collectionmotorpin1, OUTPUT);
  pinMode(Collectionmotorpin2, OUTPUT);
  pinMode(CollectionmotorENA, OUTPUT);
  ALLMotorSTOP(0);

  grabberServo.attach(grabberServoPin);
  grabberServo.write(90);
  sorterServo.attach(sorterServoPin); 
  sorterServo.write(90);
}


void loop() {
  BP32.update();

  if (!myController || !myController->isConnected()) {
    Serial.println("Controller not connected");
    delay(1000);
    return;
  }

  // Buttons
  if (myController->a())          Serial.println("A");
  if (myController->b())          Serial.println("B");
  if (myController->x())          Serial.println("X");
  if (myController->y())          Serial.println("Y");
  if (myController->l1()) {
    grabberServo.write(0); // Move grabber servo to 0 degrees (open)
    Serial.println("LB");
  }
  if (myController->r1()) {
    grabberServo.write(180); // Move grabber servo to 180 degrees (close)
    Serial.println("RB");
  }
  if (myController->l2())         Serial.println("LT");
  if (myController->r2())         Serial.println("RT");
  if (myController->thumbL())     Serial.println("Left Stick Click");
  if (myController->thumbR())     Serial.println("Right Stick Click");

  // DPad
  uint8_t dpad = myController->dpad();
  if (dpad & DPAD_UP) {
      digitalWrite(Collectionmotorpin1, HIGH); // Collection forward
      digitalWrite(Collectionmotorpin2, LOW);
      analogWrite(CollectionmotorENA, CollectionmotorSpeed);
      Serial.println("DPad Up");
  }    
  if (dpad & DPAD_DOWN) {
    digitalWrite(Collectionmotorpin1, LOW); // Collection backward
    digitalWrite(Collectionmotorpin2, HIGH);
    analogWrite(CollectionmotorENA, CollectionmotorSpeed);
    Serial.println("DPad Down");
  }
  if (dpad & DPAD_LEFT) {
    sorterServo.write(0); // Move sorter servo to 0 degrees (left)
    Serial.println("DPad Left");
  }
  if (dpad & DPAD_RIGHT) {
    sorterServo.write(180); // Move sorter servo to 180 degrees (right)
    Serial.println("DPad Right");
  }
  if (myController->miscHome())   Serial.println("Xbox Button");
  if (myController->miscStart())  Serial.println("Start/Menu");
  if (myController->miscSelect()) Serial.println("Select/View");

  // Analog sticks (only print if moved)
  int lx = myController->axisX();
  int ly = myController->axisY();
  int rx = myController->axisRX();
  int ry = myController->axisRY();

  // Drivetrain Pivots - LT and RT triggers for gradual speed control
  int lt = map(myController->brake(), 0, 1023, 0, 255); // Get LT trigger value (0-1023)
  int rt = map(myController->throttle(), 0, 1023, 0, 255); // Get LT trigger value (0-1023)

  if (lt > leftTriggerDzone) {  // LT trigger with deadzone
    leftPIVOT(lt);
  } else if (rt > rightTriggerDzone) {  // RT trigger with deadzone
    rightPIVOT(rt);
  } else if (abs(lx) > leftStickDzone || abs(ly) > leftStickDzone) {
      // Map sticks to -255 to 255 first
      int mappedY = map(ly, -512, 512, 255, -255); // inverted Y
      int mappedX = map(lx, -512, 512, -255, 255);
      int leftSpeed  = constrain(mappedY + mappedX, -255, 255);
      int rightSpeed = constrain(mappedY - mappedX, -255, 255);
    setMotors(leftSpeed, rightSpeed);
  } else {
    ALLMotorSTOP(0);
  }

  /*
  if (abs(lx) > leftDeadzone || abs(ly) > leftDeadzone) {  
    Serial.print("Left Stick X: "); Serial.print(lx);
    Serial.print(" Y: "); Serial.println(-ly);
  } */
  if (abs(rx) > rightStickDzone || abs(ry) > rightStickDzone) {
    Serial.print("Right Stick X: "); Serial.print(rx);
    Serial.print(" Y: "); Serial.println(-ry);
  }

  delay(100);
} 