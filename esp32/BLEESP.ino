#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <Wire.h>
//#include <MPU6050.h>

BLEServer* pServer = NULL;

BLECharacteristic *gpsCharacteristic = NULL;
BLECharacteristic *accelCharacteristic = NULL;
BLECharacteristic* statusCharacteristic = NULL;

BLEDescriptor *pDescr;
BLE2902 *pBLE2902;
bool deviceConnected = false;

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define GPS_CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define ACCEL_CHARACTERISTIC_UUID  "825af059-3530-4698-bd27-3f881eea9a6f"
#define STATUS_CHARACTERISTIC_UUID "d29ed658-35c8-4d80-bf33-78e22b1a596e"

// GPS variables
#define RXD2 16
#define TXD2 17
HardwareSerial SerialGPS(2);
TinyGPSPlus gps;

// MPU6050 variables
//MPU6050 mpu;

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};

class CharacteristicCallBack: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pChar) override { 
    std::string pChar2_value_stdstr = pChar->getValue();
    String pChar2_value_string = String(pChar2_value_stdstr.c_str());
    int pChar2_value_int = pChar2_value_string.toInt();
    Serial.println("pChar2: " + String(pChar2_value_int)); 
  }
};

  unsigned long startAlarm;
  bool allarmeAcceso=false;

void setup() {
  Serial.begin(115200);
  SerialGPS.begin(9600, SERIAL_8N1, RXD2, TXD2);

  pinMode(4,OUTPUT);  //rosso
  pinMode(2,OUTPUT);  //giallo
  digitalWrite(4,LOW);
  digitalWrite(2,LOW);

  Wire.begin();
  //mpu.begin();
  //mpu.calcGyroOffsets(true);
  
  BLEDevice::init("ESP32");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create GPS characteristic
  gpsCharacteristic = pService->createCharacteristic(
                                       GPS_CHARACTERISTIC_UUID,
                                       BLECharacteristic::PROPERTY_READ |
                                       BLECharacteristic::PROPERTY_NOTIFY
                                     );
  gpsCharacteristic->addDescriptor(new BLE2902());

  // Create accelerometer characteristic
  accelCharacteristic = pService->createCharacteristic(
                                       ACCEL_CHARACTERISTIC_UUID,
                                       BLECharacteristic::PROPERTY_READ |
                                       BLECharacteristic::PROPERTY_NOTIFY
                                     );
  accelCharacteristic->addDescriptor(new BLE2902());

  // Create status characteristic
  statusCharacteristic = pService->createCharacteristic(
                                       STATUS_CHARACTERISTIC_UUID,
                                       BLECharacteristic::PROPERTY_READ |
                                       BLECharacteristic::PROPERTY_WRITE |
                                       BLECharacteristic::PROPERTY_NOTIFY
                                     );
  statusCharacteristic->addDescriptor(new BLE2902());


  pService->start();
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
}

void loop() {
  if (deviceConnected) {
    // Read GPS data
    while (SerialGPS.available() > 0) {
      gps.encode(SerialGPS.read());
    }

    if (gps.location.isValid()) {
      float latitude = gps.location.lat();
      float longitude = gps.location.lng();

      // Read accelerometer data
      //mpu.update();

      //float accelX = mpu.getAccX();
      //float accelY = mpu.getAccY();
      //float accelZ = mpu.getAccZ();
      float accelX = 1;
      float accelY = 1;
      float accelZ = 1;

      //float accTOT=accelX*accelX+accelY*accelY+accelZ*accelZ;
      float accTOT=3;

      // Send GPS and accelerometer data
      String gpsData = String(latitude, 6) + "/" + String(longitude, 6);
      gpsCharacteristic->setValue(gpsData.c_str());
      String accelData = String(accTOT);
      accelCharacteristic->setValue(accelData.c_str());

      accelCharacteristic-> notify();
      gpsCharacteristic->notify();
    }

    // Check for incoming data
    std::string value = statusCharacteristic->getValue();
    if (!value.empty()) {
      // Convert string to integers
      int isolatedStatus = value[0] - '0'; // Convert char to integer
      int alarmStatus = value[2] - '0'; // Convert char to integer

      // Process received values
      if (isolatedStatus == 0) {
        // Bracelet is not isolated
        //Serial.println("Bracelet is not isolated");
        digitalWrite(2,LOW);
      } else if (isolatedStatus == 1) {
        // Bracelet is isolated
        //Serial.println("Bracelet is isolated");
        digitalWrite(2,HIGH);
      } else {
        // Invalid isolated status received
        //Serial.println("Invalid isolated status received");
        digitalWrite(2,LOW);
      }

      if (alarmStatus == 0) {
        // No alarm set
        Serial.println("No alarm set");
        allarmeAcceso=false;
        digitalWrite(4,LOW);
      } 

      else if (alarmStatus == 1) {    //ACCENDO IL CICALINO
        if(!allarmeAcceso){
          allarmeAcceso=true;
          digitalWrite(4,HIGH);
          startAlarm=millis();
          Serial.println("Alarm set");
        }
        // Alarm set
        else if(millis()-startAlarm>2000){  //
          digitalWrite(4,LOW);
          Serial.println("Alarm stopped");
        }
      } 


      else {
        // Invalid alarm status received
        digitalWrite(4,LOW);
        Serial.println("Invalid alarm status received");
        
      }
    }
  }
}