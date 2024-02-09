#include <TinyGPSPlus.h>


// The TinyGPSPlus object
// ESP 32

TinyGPSPlus gps;


void setup() {

  Serial.begin(9600);
  Serial2.begin(9600);
  pinMode(4,OUTPUT);
  delay(3000);
}


void loop() {
  //updateSerial();

  while (Serial2.available() > 0)
   if (gps.encode(Serial2.read()))
       displayInfo();


  if (millis() % 5000==0 && gps.charsProcessed() < 10){
    Serial.println(F("No GPS detected: check wiring."));
    delay(5000);
      // ogni 5 sec riprova
  }

}


void displayInfo(){


  Serial.print(F("Location: "));


  if (gps.location.isValid()){
    digitalWrite(4,HIGH);
    Serial.print("Lat: ");
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print("Lng: ");
    Serial.print(gps.location.lng(), 6);
    Serial.println();
  }  
  else Serial.print(F("INVALID"));
}


void updateSerial()


{


  delay(500);


  while (Serial.available())


  {


    Serial2.write(Serial.read());//Forward what Serial received to Software Serial Port


  }


  while (Serial2.available())


  {


    Serial.write(Serial2.read());//Forward what Software Serial received to Serial Port


  }


}

