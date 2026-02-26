#include <Bluepad32.h>

ControllerPtr myController;

// DEADZONES
int leftDeadzone = 50; // adjust as needed
int rightDeadzone = 50; // adjust as needed


// DRIVETRAIN - L298n MOTOR COTNROL
int pivotSpeed = 200; // Adjust as needed (0-255)

int Lmotorpin1 = 5;
int Lmotorpin2 = 6;
int LmotorENA = 7; // PWM pin

int Rmotorpin1 = 15;
int Rmotorpin2 = 16;
int RmotorENA = 17; // PWM pin

// MOTOR HELPER FUNCTIONS
void ALLMotorSTOP(int maxSpeed) {
  digitalWrite(Lmotorpin1, LOW);
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed);

  digitalWrite(Rmotorpin1, LOW);
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed);
}

void leftPIVOT(int pivotSpeed) {
  digitalWrite(Lmotorpin1, LOW); // L backward
  digitalWrite(Lmotorpin2, HIGH);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, pivotSpeed);
}

void rightPIVOT(int pivotSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, pivotSpeed);

  digitalWrite(Rmotorpin1, LOW); // R backward
  digitalWrite(Rmotorpin2, HIGH);
  analogWrite(RmotorENA, pivotSpeed);
}

void setMotors(int leftSpeed, int rightSpeed) {
  if (leftSpeed > 50) {
    digitalWrite(Lmotorpin1, HIGH); // L forward
    digitalWrite(Lmotorpin2, LOW);
    analogWrite(LmotorENA, leftSpeed);
  } else if (leftSpeed < -50) {
    digitalWrite(Lmotorpin1, LOW); // L backward
    digitalWrite(Lmotorpin2, HIGH);
    analogWrite(LmotorENA, -leftSpeed);
  } else {
    digitalWrite(Lmotorpin1, LOW);
    digitalWrite(Lmotorpin2, LOW);
    analogWrite(LmotorENA, 0);
  }

  if (rightSpeed > 50) {
    digitalWrite(Rmotorpin1, HIGH); // R forward
    digitalWrite(Rmotorpin2, LOW);
    analogWrite(RmotorENA, rightSpeed);
  } else if (rightSpeed < -50) {
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
  ALLMotorSTOP(0);
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
  if (myController->l1())         Serial.println("LB");
  if (myController->r1())         Serial.println("RB");
  if (myController->l2())         Serial.println("LT");
  if (myController->r2())         Serial.println("RT");
  if (myController->thumbL())     Serial.println("Left Stick Click");
  if (myController->thumbR())     Serial.println("Right Stick Click");

  // DPad
  uint8_t dpad = myController->dpad();
  if (dpad & DPAD_UP)    Serial.println("DPad Up");
  if (dpad & DPAD_DOWN)  Serial.println("DPad Down");
  if (dpad & DPAD_LEFT)  Serial.println("DPad Left");
  if (dpad & DPAD_RIGHT) Serial.println("DPad Right");

  if (myController->miscHome())   Serial.println("Xbox Button");
  if (myController->miscStart())  Serial.println("Start/Menu");
  if (myController->miscSelect()) Serial.println("Select/View");

  // Analog sticks (only print if moved)
  int lx = myController->axisX();
  int ly = myController->axisY();
  int rx = myController->axisRX();
  int ry = myController->axisRY();

  // Drivetrain Pivots
  if (myController->L1()) {
    leftPIVOT(speed);
  } else if (myController->R1()) {
    rightPIVOT(speed);
  } else if (abs(lx) > leftDeadzone || abs(ly) > leftDeadzone) {
      int leftSpeed  = constrain(map(ly + lx, -512, 512, -255, 255), -255, 255);
      int rightSpeed = constrain(map(ly - lx, -512, 512, -255, 255), -255, 255);
      setMotors(leftSpeed, rightSpeed);
  } else {
    ALLMotorSTOP(0);
  }

  /*
  if (abs(lx) > leftDeadzone || abs(ly) > leftDeadzone) {  
    Serial.print("Left Stick X: "); Serial.print(lx);
    Serial.print(" Y: "); Serial.println(-ly);
  } */
  if (abs(rx) > rightDeadzone || abs(ry) > rightDeadzone) {
    Serial.print("Right Stick X: "); Serial.print(rx);
    Serial.print(" Y: "); Serial.println(-ry);
  }

  delay(100);
} 






void forward(int maxSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed);

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed);
}

void backward(int maxSpeed) {
  digitalWrite(Lmotorpin1, LOW); // L backward
  digitalWrite(Lmotorpin2, HIGH);
  analogWrite(LmotorENA, maxSpeed);

  digitalWrite(Rmotorpin1, LOW); // R backward
  digitalWrite(Rmotorpin2, HIGH);
  analogWrite(RmotorENA, maxSpeed);
}

void smallTurnLeft(int maxSpeed, int smallTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, smallTurnSpeed); // L slower

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed); // R max speed
}

void smallTurnRight(int maxSpeed, int smallTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed); // L max speed

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, smallTurnSpeed); // R slower
}

void mediumTurnLeft(int maxSpeed, int mediumTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, mediumTurnSpeed); // L slower

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed); // R max speed
}

void mediumTurnRight(int maxSpeed, int mediumTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed); // L max speed

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, mediumTurnSpeed); // R slower
}

void bigTurnLeft(int maxSpeed, int bigTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, bigTurnSpeed); // L slower

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, maxSpeed); // R max speed
}

void bigTurnRight(int maxSpeed, int bigTurnSpeed) {
  digitalWrite(Lmotorpin1, HIGH); // L forward
  digitalWrite(Lmotorpin2, LOW);
  analogWrite(LmotorENA, maxSpeed); // L max speed

  digitalWrite(Rmotorpin1, HIGH); // R forward
  digitalWrite(Rmotorpin2, LOW);
  analogWrite(RmotorENA, bigTurnSpeed); // R slower
}