#include <Bluepad32.h>

ControllerPtr myController;

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

  int leftDeadzone = 50; \\adjust as needed
  int rightDeadzone = 50; \\adjust as needed
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

  if (abs(lx) > leftDeadzone || abs(ly) > leftDeadzone) {  
    Serial.print("Left Stick X: "); Serial.print(lx);
    Serial.print(" Y: "); Serial.println(-ly);
  }
  if (abs(rx) > rightDeadzone || abs(ry) > rightDeadzone) {
    Serial.print("Right Stick X: "); Serial.print(rx);
    Serial.print(" Y: "); Serial.println(-ry);
  }

  delay(100);
}
