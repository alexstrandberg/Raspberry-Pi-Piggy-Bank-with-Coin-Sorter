/*
  This sketch assumes that coin 1, will return 1 pulse, coin 2 will return 2 pulses, and so on.
 
 Coin values:
 1 = 0.01
 2 = 0.05
 3 = 0.10
 4 = 0.25
 */
 
#include <Adafruit_Fingerprint.h>
#if ARDUINO >= 100
 #include <SoftwareSerial.h>
#else
 #include <NewSoftSerial.h>
#endif

int getFingerprintIDez();

// pin #4 is IN from sensor (GREEN wire)
// pin #5 is OUT from arduino  (WHITE wire)
#if ARDUINO >= 100
SoftwareSerial mySerial(4, 5);
#else
NewSoftSerial mySerial(4, 5);
#endif

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
 
const float coinValues[4] = {
  .01, .05, .10, .25}; //Coin values goes into this array
#define pulseTimeout 275        //How many milliseconds there are from the last impulse to the coin is determined (default 275)
 
 
unsigned long lastAction = 0;   //When last action was made
unsigned long lastPulse = 0;    //When last pulse was send
int pulseCount = 0;             //How many pulses we got

unsigned long tempAction;
unsigned long tempPulse;

boolean pollFingerprint = false;
 
void setup()
{
  Serial.begin(9600);
 
  attachInterrupt(0, acceptorCount, RISING); //Digital interrupt pin 2
  attachInterrupt(1, acceptorPulse, RISING); //Digital interrupt pin 3
 
  Serial.println("Coin Acceptor ready");
  pulseCount = 0;
 
  pinMode(13, OUTPUT);
  
  finger.begin(57600);
  
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
  }
}

void loop()
{
  if (Serial.available() > 0) {
        char incoming = (char)Serial.read();
        if (incoming=='F') {
          pollFingerprint = true;
          Serial.println("FINGERPRINT MODE");
        }
        else if (incoming=='C') {
          pollFingerprint = false;
          Serial.println("COIN MODE");
        }
  }
  
  tempAction = lastAction;
  tempPulse = lastPulse;
  
  if (!pollFingerprint) {
    if (millis() - lastPulse >= pulseTimeout && pulseCount > 0 || pulseCount >= 4)
    {
      if (tempAction != lastAction || tempPulse != lastPulse) return; //Check if interrupt has fired since loop started, wait for next cycle if it has
     
      if (coinValues[pulseCount-1]==.01) Serial.println("PENNY");
      else if (coinValues[pulseCount-1]==.05) Serial.println("NICKEL");
      else if (coinValues[pulseCount-1]==.10) Serial.println("DIME");
      else if (coinValues[pulseCount-1]==.25) Serial.println("QUARTER");
      
      pulseCount = 0;
    }
  }
  
  else if (pollFingerprint) {
    if (getFingerprintIDez()!=-1) {
      Serial.println("THE EAGLE HAS LANDED");
    }
  }
}
 
void acceptorPulse()
{
  lastAction = millis();
  lastPulse = millis();
  pulseCount++;
}
 
void acceptorCount()
{
  digitalWrite(13, digitalRead(13));
}

uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println("No finger detected");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  // OK success!

  p = finger.image2Tz();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }
  
  // OK converted!
  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    Serial.println("Found a print match!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("Did not find a match");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }   
  
  // found a match!
  Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  Serial.print(" with confidence of "); Serial.println(finger.confidence); 
}

// returns -1 if failed, otherwise returns ID #
int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK)  return -1;
  
  // found a match!
  Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID; 
}

/*void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '&') {
      stringComplete = true;
    } 
  }
}*/
