const int S0 = 8;
const int S1 = 9;
const int S2 = 10;
const int S3 = 11;
const int signal = 12;

void setup() {
  pinMode(S0,OUTPUT);
  pinMode(S1,OUTPUT);
  pinMode(S2,OUTPUT);
  pinMode(S3,OUTPUT);
  pinMode(signal,INPUT);
  
  digitalWrite(S0,HIGH);
  digitalWrite(S1,LOW);
  
  Serial.begin(9600);
}

void loop() {
  unsigned long red, green, blue;
  
  // Read Red
  digitalWrite(S2,LOW);
  digitalWrite(S3,LOW);
  red = pulseIn(signal,HIGH);
  
  // Read Green
  digitalWrite(S2,HIGH);
  digitalWrite(S3,HIGH);
  green = pulseIn(signal,HIGH);
  
  // Read Blue
  digitalWrite(S2,LOW);
  digitalWrite(S3,HIGH);
  blue = pulseIn(signal,HIGH);
  
  Serial.print("Red: ");
  Serial.print(red);
  Serial.print(" | Green: ");
  Serial.print(green);
  Serial.print(" | Blue: ");
  Serial.println(blue);
  
  delay(500);
}