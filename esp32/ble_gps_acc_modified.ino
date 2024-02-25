#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>


#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define GPS_CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define ACCEL_CHARACTERISTIC_UUID  "825af059-3530-4698-bd27-3f881eea9a6f"

//#define SERVICE_UUID_RECEIVE    "624148b3-c9c9-4968-8543-4fe150e1ed9a"
#define STATUS_CHARACTERISTIC_UUID "d29ed658-35c8-4d80-bf33-78e22b1a596e"

BLEServer* pServer = NULL;
BLECharacteristic *gpsCharacteristic = NULL;
BLECharacteristic *accelCharacteristic = NULL;

//BLEServer* pServerReceive =NULL;
BLECharacteristic* statusCharacteristic = NULL;

BLEDescriptor *pDescr;
BLE2902 *pBLE2902;

//global variables
bool deviceConnected = false;
bool oldDeviceConnected = false;
unsigned long lastUpdateTime = 0;
unsigned long startAlarm;
bool allarmeAcceso=false;

// GPS variables
#define RXD2 16
#define TXD2 17
HardwareSerial SerialGPS(2);
TinyGPSPlus gps;

// MPU6050 variables
Adafruit_MPU6050 mpu;



void checkToReconnect() 
{
  // disconnected so advertise
  if (!deviceConnected && oldDeviceConnected) {
    delay(500); // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising(); // restart advertising
    //pServerReceive->startAdvertising(); // restart advertising
    Serial.println("Disconnected: start advertising");
    oldDeviceConnected = deviceConnected;
  }
  // connected so reset boolean control
  if (deviceConnected && !oldDeviceConnected) {
    // do stuff here on connecting
    Serial.println("Reconnected");
    oldDeviceConnected = deviceConnected;
  }
}



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


void setup() {
  Serial.begin(115200);
  SerialGPS.begin(9600, SERIAL_8N1, RXD2, TXD2);

  pinMode(4,OUTPUT);  
  pinMode(2,OUTPUT);  //ROSSO
  pinMode(13,OUTPUT);  
  digitalWrite(4,LOW);
  digitalWrite(2,LOW);
  digitalWrite(13,LOW);

  Wire.begin();
  mpu.begin();

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }
  
  BLEDevice::init("ESP32");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  //pServerReceive = BLEDevice::createServer();
  //pServerReceive->setCallbacks(new MyServerCallbacks());
  
  //Create services
  BLEService *pService = pServer->createService(SERVICE_UUID);
  //BLEService *pServiceReceive = pServerReceive->createService(SERVICE_UUID_RECEIVE);

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

  // Start services
  pService->start();
  //pServiceReceive->start();

  // Start advertising
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
  //BLEAdvertising *pAdvertisingReceive = pServerReceive->getAdvertising();
  //pAdvertisingReceive->start();

}

void loop() {

  // Controlla la connessione BLE e gestisci le riconnessioni
  //checkToReconnect();

  // Invia dati GPS e di localizzazione ogni secondo
  if(deviceConnected){

    digitalWrite(13,HIGH);

    if (millis() - lastUpdateTime >= 1000) {
      lastUpdateTime = millis();
      // Leggi e invia dati GPS e di localizzazione
      sendData();
    }

    // Gestisci la ricezione dei dati BLE
    receiveData();
  }
  
  else{
    digitalWrite(13,LOW);
  }
}

void sendData(){
    // Read GPS data
    while (SerialGPS.available() > 0) {
      gps.encode(SerialGPS.read());
    }

    if (gps.location.isValid()) {
      float latitude = gps.location.lat();
      float longitude = gps.location.lng();

      // Send GPS data
      String gpsData = String(latitude, 6) + "/" + String(longitude, 6);
      gpsCharacteristic->setValue(gpsData.c_str());
      gpsCharacteristic->notify();
    }

    // Read accelerometer data
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    int caduta=0;
    float accelX=a.acceleration.x;
    float accelY=a.acceleration.y;
    float accelZ=a.acceleration.z;
    float accTOT= sqrt(accelX*accelX+accelY*accelY+accelZ*accelZ);
    Serial.println(accTOT);
      
    //send accelerometer data
    String accelData = String(accTOT);
    accelCharacteristic->setValue(accelData.c_str());
    accelCharacteristic-> notify();
}

void receiveData(){
    // Check for incoming data
    std::string value = statusCharacteristic->getValue();
    if (!value.empty()) {
      // Convert string to integers
      int isolatedStatus = value[0] - '0'; // Convert char to integer
      int alarmStatus = value[2] - '0'; // Convert char to integer

      // Process received values
      if (isolatedStatus == 0) {
        // Bracelet is not isolated
        Serial.println("Bracelet is not isolated");
        digitalWrite(2,LOW);
      } else if (isolatedStatus == 1) {
        // Bracelet is isolated
        Serial.println("Bracelet is isolated");
        digitalWrite(2,HIGH);
      } else {
        // Invalid isolated status received
        //Serial.println("Invalid isolated status received");
        digitalWrite(2,LOW);
      }

      if (alarmStatus == 0) {
        // No alarm set
        //Serial.println("No alarm set");
        allarmeAcceso=false;
        digitalWrite(4,LOW);
      } 

      else if (alarmStatus == 1) {    //ACCENDO IL CICALINO
        if(!allarmeAcceso){
          allarmeAcceso=true;
          digitalWrite(4,HIGH);
          startAlarm=millis();
          //Serial.println("Alarm set");
        }
        // Alarm set
        else if(millis()-startAlarm>2000){  //
          digitalWrite(4,LOW);
          //Serial.println("Alarm stopped");
        }
      } 

      else {
        // Invalid alarm status received
        digitalWrite(4,LOW);
        Serial.println("Invalid alarm status received");
        
      }
    }
}