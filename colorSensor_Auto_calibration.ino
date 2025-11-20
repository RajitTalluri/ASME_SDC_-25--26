const int S0 = 8;
const int S1 = 9;
const int S2 = 10;
const int S3 = 11;
const int signal = 12;

// Calibration variables
int redMin = 9999, redMax = 0;
int greenMin = 9999, greenMax = 0;
int blueMin = 9999, blueMax = 0;

bool calibrated = false;

void setup() {
  pinMode(S0,OUTPUT);
  pinMode(S1,OUTPUT);
  pinMode(S2,OUTPUT);
  pinMode(S3,OUTPUT);
  pinMode(signal,INPUT);
  
  digitalWrite(S0,HIGH);
  digitalWrite(S1,LOW);
  
  Serial.begin(9600);
  
  // Calibration sequence
  Serial.println("=== CALIBRATION MODE ===");
  Serial.println("Point sensor at WHITE surface...");
  delay(3000);
  
  calibrateWhite();
  
  Serial.println("\nNow point sensor at BLACK surface...");
  delay(3000);
  
  calibrateBlack();
  
  Serial.println("\n=== CALIBRATION COMPLETE ===");
  Serial.println("Min/Max values:");
  Serial.print("Red: "); Serial.print(redMin); Serial.print("-"); Serial.println(redMax);
  Serial.print("Green: "); Serial.print(greenMin); Serial.print("-"); Serial.println(greenMax);
  Serial.print("Blue: "); Serial.print(blueMin); Serial.print("-"); Serial.println(blueMax);
  Serial.println("\nStarting measurements...\n");
  
  calibrated = true;
  delay(2000);
}

void calibrateWhite() {
  for(int i = 0; i < 10; i++) {
    digitalWrite(S2,LOW); digitalWrite(S3,LOW);
    int r = pulseIn(signal, LOW);
    
    digitalWrite(S2,HIGH); digitalWrite(S3,HIGH);
    int g = pulseIn(signal, LOW);
    
    digitalWrite(S2,LOW); digitalWrite(S3,HIGH);
    int b = pulseIn(signal, LOW);
    
    if(r < redMin) redMin = r;
    if(g < greenMin) greenMin = g;
    if(b < blueMin) blueMin = b;
    
    Serial.print(".");
    delay(100);
  }
}

void calibrateBlack() {
  for(int i = 0; i < 10; i++) {
    digitalWrite(S2,LOW); digitalWrite(S3,LOW);
    int r = pulseIn(signal, LOW);
    
    digitalWrite(S2,HIGH); digitalWrite(S3,HIGH);
    int g = pulseIn(signal, LOW);
    
    digitalWrite(S2,LOW); digitalWrite(S3,HIGH);
    int b = pulseIn(signal, LOW);
    
    if(r > redMax) redMax = r;
    if(g > greenMax) greenMax = g;
    if(b > blueMax) blueMax = b;
    
    Serial.print(".");
    delay(100);
  }
}

void loop() {
  if(!calibrated) return;
  
  // Read raw frequencies
  digitalWrite(S2,LOW); digitalWrite(S3,LOW);
  int redFreq = pulseIn(signal, LOW);
  
  digitalWrite(S2,HIGH); digitalWrite(S3,HIGH);
  int greenFreq = pulseIn(signal, LOW);
  
  digitalWrite(S2,LOW); digitalWrite(S3,HIGH);
  int blueFreq = pulseIn(signal, LOW);
  
  // Map to 0-255 (inverted: low freq = bright = 255)
  int redValue = map(redFreq, redMin, redMax, 255, 0);
  int greenValue = map(greenFreq, greenMin, greenMax, 255, 0);
  int blueValue = map(blueFreq, blueMin, blueMax, 255, 0);
  
  // Constrain
  redValue = constrain(redValue, 0, 255);
  greenValue = constrain(greenValue, 0, 255);
  blueValue = constrain(blueValue, 0, 255);
  
  // Print CSV format
  Serial.print(redValue);
  Serial.print(",");
  Serial.print(greenValue);
  Serial.print(",");
  Serial.println(blueValue);
  
  delay(500);
}
```

**How to use:**
1. Upload code
2. Open Serial Monitor
3. Immediately point at **white paper** (wait 3 seconds)
4. Then point at **black paper** (wait 3 seconds)
5. Done! Now it outputs calibrated RGB values

---

## **Expected Results After Calibration**
```
White paper:  255, 255, 255 (or close to it)
Black paper:  0, 0, 0 (or close to it)
Red marker:   255, 50, 30
Green marker: 30, 255, 40
Blue marker:  40, 60, 255