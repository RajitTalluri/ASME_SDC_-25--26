#include <Bluepad32.h>
#include <ESP32Servo.h>

ControllerPtr myController;

// EG - extra gpio 13,12,11
// EN - enable

// DEADZONES
int leftStickDzone = 50; // adjust as needed
int rightStickDzone = 50; // adjust as needed
int leftTriggerDzone = 50; // adjust as needed
int rightTriggerDzone = 50; // adjust as needed

// DRIVETRAIN - L298n MOTOR COTNROL
int Lmotorpin1 = 5; // In 1 pin | 15
int Lmotorpin2 = 4; // In 2 pin | 16
int LmotorENA = 6; // PWM, ENA pin | 7

int Rmotorpin1 = 3; // In 3 pin | 17 
int Rmotorpin2 = 9; // In 4 pin | 2
int RmotorENA = 10; // PWM, ENB pin | 1

int Collectionmotorpin1 = 15; // In 5 pin | 5
int Collectionmotorpin2 = 16; // In 6 pin | 4
int CollectionmotorENA = 7; // PWM, ENC pin | 6
int CollectionmotorSpeed = 100; // adjust as needed 
int Disposalmotorpin1 = 17; // In 7 pin | 3
int Disposalmotorpin2 = 2; // In 8 pin | 9
int DisposalmotorENA = 1; // PWM, END pin | 10
int DisposalmotorSpeed = 255; // slower for more torque


// SERVOS
Servo grabberServo;
int grabberServoPin = 42; // S1 labeled as PWM on PCB
int grabberDeg = 90;
Servo sorterServo;
int sorterServoPin = 41; // S2 labeled as PWM on PCB
int sorterDeg = 135; 


// MOTOR HELPER FUNCTIONS
void ALLMotorSTOP(int maxSpeed) {
  digitalWrite(Lmotorpin1, LOW);
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, 0);
  
  digitalWrite(Rmotorpin1, LOW);
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, 0);
}


void leftPIVOT(int pivotSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L backward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, pivotSpeed);
}


void rightPIVOT(int pivotSpeed) {
  digitalWrite(Lmotorpin1, LOW); // L forward
  digitalWrite(Lmotorpin2, HIGH);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(Rmotorpin1, LOW); // R backward
  digitalWrite(Rmotorpin2, HIGH);
  analogWrite(RmotorENA, pivotSpeed);
}


void setMotors(int leftSpeed, int rightSpeed) {

  if (leftSpeed > leftStickDzone) {
    digitalWrite(Lmotorpin1, LOW); // L forward
    digitalWrite(Lmotorpin2, HIGH);
    analogWrite(LmotorENA, leftSpeed);
  } else if (leftSpeed < -leftStickDzone) {
    digitalWrite(Lmotorpin1, HIGH); // L backward
    digitalWrite(Lmotorpin2, LOW);
    analogWrite(LmotorENA, -leftSpeed);
  } else {
    digitalWrite(Lmotorpin1, LOW);
    digitalWrite(Lmotorpin2, LOW);
    analogWrite(LmotorENA, 0);
  }

  if (rightSpeed > rightStickDzone) {
    digitalWrite(Rmotorpin1, HIGH); // R forward
    digitalWrite(Rmotorpin2, LOW);
    analogWrite(RmotorENA, rightSpeed);
  } else if (rightSpeed < -rightStickDzone) {
    digitalWrite(Rmotorpin1, LOW); // R backward
    digitalWrite(Rmotorpin2, HIGH);
    analogWrite(RmotorENA, -rightSpeed);
  } else {
    digitalWrite(Rmotorpin1, LOW);
    digitalWrite(Rmotorpin2, LOW);
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

  pinMode(Lmotorpin1, OUTPUT);
  pinMode(Lmotorpin2, OUTPUT);
  pinMode(LmotorENA, OUTPUT);
  pinMode(Rmotorpin1, OUTPUT);
  pinMode(Rmotorpin2, OUTPUT);
  pinMode(RmotorENA, OUTPUT);
  pinMode(Collectionmotorpin1, OUTPUT);
  pinMode(Collectionmotorpin2, OUTPUT);
  pinMode(CollectionmotorENA, OUTPUT);
  pinMode(Disposalmotorpin1, OUTPUT);
  pinMode(Disposalmotorpin2, OUTPUT);
  pinMode(DisposalmotorENA, OUTPUT);
  ALLMotorSTOP(0);

  grabberServo.attach(grabberServoPin);
  grabberServo.write(grabberDeg);
  sorterServo.attach(sorterServoPin); 
  sorterServo.write(sorterDeg);
}


void loop() {
  BP32.update();

  if (!myController || !myController->isConnected()) {
    Serial.println("Controller not connected");
    delay(1000);
    return;
  }

  // Buttons
  if (myController->a()) {
    Serial.println("A");
    digitalWrite(Disposalmotorpin1, LOW); // Disposal Up
    digitalWrite(Disposalmotorpin2, HIGH);
    analogWrite(DisposalmotorENA, DisposalmotorSpeed);
  }        

  if (myController->b()) {
    {
    Serial.println("B");
    digitalWrite(Disposalmotorpin1, HIGH);
    digitalWrite(Disposalmotorpin2, LOW); // Disposal down
    analogWrite(DisposalmotorENA, DisposalmotorSpeed);
  }        
  }
  if (myController->x()) {
    digitalWrite(Disposalmotorpin1, LOW);
    digitalWrite(Disposalmotorpin2, LOW);
    Serial.println("X");
  }
  if (myController->y()) {
    digitalWrite(Collectionmotorpin1, LOW);
    digitalWrite(Collectionmotorpin2, LOW);
    Serial.println("Y"); 
  }   

  if (myController->l1()) {
    grabberDeg -= 30;
    grabberDeg = constrain(grabberDeg, 0,180);
    grabberServo.write(grabberDeg); // Move grabber servo to 0 degrees (open)
    Serial.println("LB");
  }
  if (myController->r1()) {
    grabberDeg += 30;
    grabberDeg = constrain(grabberDeg, 0,180);
    grabberServo.write(grabberDeg); // Move grabber servo to 180 degrees (close)
    Serial.println("RB");
  }
  if (myController->l2())         Serial.println("LT");
  if (myController->r2())         Serial.println("RT");
  if (myController->thumbL())     Serial.println("Left Stick Click");
  if (myController->thumbR())     Serial.println("Right Stick Click");

  // DPad
  uint8_t dpad = myController->dpad();
  if (dpad & DPAD_UP) {
      analogWrite(CollectionmotorENA, CollectionmotorSpeed);
      digitalWrite(Collectionmotorpin1, HIGH); // Collection forward
      digitalWrite(Collectionmotorpin2, LOW);
      delay(600);
      digitalWrite(Collectionmotorpin1, LOW); // Collection forward
      digitalWrite(Collectionmotorpin2, LOW);

      Serial.println("DPad Up");
  }    
  if (dpad & DPAD_DOWN) {
    analogWrite(CollectionmotorENA, CollectionmotorSpeed);
    digitalWrite(Collectionmotorpin1, LOW); // Collection backward
    digitalWrite(Collectionmotorpin2, HIGH);
    delay(350);
    digitalWrite(Collectionmotorpin1, LOW); // Collection backward
    digitalWrite(Collectionmotorpin2, LOW);
    Serial.println("DPad Down");
  }
  if (dpad & DPAD_LEFT) {
    sorterDeg -= 45;
    sorterDeg = constrain(sorterDeg, 45, 200);
    sorterServo.write(sorterDeg); // Move sorter servo to 0 degrees (left)
    Serial.println("DPad Left");
  }
  if (dpad & DPAD_RIGHT) {
    sorterDeg += 45;
    sorterDeg = constrain(sorterDeg, 45, 200);
    sorterServo.write(sorterDeg); // Move sorter servo to 180 degrees (right)
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

    mappedX = mappedX / 2;   // softer turning
    int rightSpeed  = constrain(mappedY + mappedX, -255, 255);
    int leftSpeed = constrain(mappedY - mappedX, -255, 255);

    setMotors(leftSpeed, rightSpeed);
    printf("Left Speed: %d \n Right Speed: %d \n", leftSpeed, rightSpeed);
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