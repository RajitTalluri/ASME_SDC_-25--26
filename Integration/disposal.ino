#define ENABLE 5 // PWM 5 on Arduino
#define DIRA 3
#define DIRB 4

// PWM pins assigned to left/right buttons
#define BTN_RIGHT 6
#define BTN_LEFT 7 

void setup() {
  pinMode(ENABLE, OUTPUT);
  pinMode(DIRA, OUTPUT);
  pinMode(DIRB, OUTPUT);

  pinMode(BTN_RIGHT, INPUT);
  pinMode(BTN_LEFT, INPUT);

  Serial.begin(9600);
}

void loop() {
  if (digitalRead(BTN_RIGHT) == HIGH) {
    // Spin forward
    digitalWrite(DIRA, HIGH);
    digitalWrite(DIRB, LOW);
    analogWrite(ENABLE, 250); // speed 0–255
  }
  else if (digitalRead(BTN_LEFT) == HIGH) {
    // Spin reverse
    digitalWrite(DIRA, LOW);
    digitalWrite(DIRB, HIGH);
    analogWrite(ENABLE, 250); // speed 0–255
  }
  else {
    // Stop motor
    analogWrite(ENABLE, 0);
  }
}