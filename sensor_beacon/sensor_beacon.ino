/*
  Button LED
  This example creates a BLE peripheral with service that contains a
  characteristic to control an LED and another characteristic that
  represents the state of the button.
  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.
  - Button connected to pin 4
  You can use a generic BLE central app, like LightBlue (iOS and Android) or
  nRF Connect (Android), to interact with the services and characteristics
  created in this sketch.
  This example code is in the public domain.
*/

#include <ArduinoBLE.h>
#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_APDS9960.h>
#include <PDM.h>

#define BITMASK 0x00ff

typedef struct colorStruct{
  int r;
  int g;
  int b;
  int c;
}COLOUR;

BLEService sensorService("19B10010-E8F2-537E-4F6C-D104768A1214"); // create service

//Characteristics for sensor values
BLEIntCharacteristic tempCharacteristic("19B10012-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //temperature
BLEIntCharacteristic humCharacteristic("19B10013-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //humidity
BLEIntCharacteristic pressCharacteristic("19B10014-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //pressure
BLEIntCharacteristic col_rgCharacteristic("19B10015-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //colour (Red Green)
BLEIntCharacteristic col_bcCharacteristic("19B10016-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //colour (Blue Clear)
BLEIntCharacteristic dbaCharacteristic("19B10017-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify); //sound (DB(A))

//declarations for sensor variables
short sampleBuffer[256];
float db = 0.0;
volatile int samplesRead; //number of sound samples read
int temperature;
int humidity;
int pressure;
COLOUR colours;

void setup() {
  Serial.begin(9600);

  // configure the data receive callback
  PDM.onReceive(onPDMdata);
  
  if (!HTS.begin()) {
    Serial.println("Failed to initialize humidity temperature sensor!");
    while (1);
   }
      if (!BARO.begin()) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1);
   }
      if (!APDS.begin()) {
    Serial.println("Error initializing APDS9960 sensor.");
  }
  // initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate
  if (!PDM.begin(1, 16000)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }
  
  Serial.println(BLE.address());
  // set the local name peripheral advertises
  BLE.setLocalName("Sensorboard");
  // set the UUID for the service this peripheral advertises:
  BLE.setAdvertisedService(sensorService);

  // add the characteristics to the service
  sensorService.addCharacteristic(tempCharacteristic);
  sensorService.addCharacteristic(humCharacteristic);
  sensorService.addCharacteristic(pressCharacteristic);
  sensorService.addCharacteristic(col_rgCharacteristic);
  sensorService.addCharacteristic(col_bcCharacteristic);
  sensorService.addCharacteristic(dbaCharacteristic);

  // add the service
  BLE.addService(sensorService);

  // start advertising
  BLE.advertise();

  Serial.println("Bluetooth device active, waiting for connections...");
}

void loop() {
  BLE.poll();

  int val = millis();
  int maxVal = 0;
  while(millis() - val < 700){  
    if (samplesRead) {
      //Serial.println(samplesRead);
      // print samples to the serial monitor or plotter
      for (int i = 0; i < samplesRead; i++) {
        if(sampleBuffer[i] > maxVal){
//           Serial.println(sampleBuffer[i]);
           maxVal = sampleBuffer[i];
        }
      }
      samplesRead = 0;
  }}
  db = map(maxVal*2,0,1500,0,90); 
  
  temperature = (int)(HTS.readTemperature()*100);
  humidity = (int)(HTS.readHumidity()*100);
  pressure = (int)(BARO.readPressure()*100);
  
  if(APDS.colorAvailable())
    APDS.readColor(colours.r, colours.g, colours.b, colours.c);

  tempCharacteristic.writeValue(temperature);
  BLE.poll();
  delay(50);
  humCharacteristic.writeValue(humidity);
  BLE.poll();
  delay(50);
  pressCharacteristic.writeValue(pressure);
  BLE.poll();
  delay(50);
  col_rgCharacteristic.writeValue((int)(colours.r << 16) | (colours.g & BITMASK));
  BLE.poll();
  delay(50);
  col_bcCharacteristic.writeValue((int)(colours.b << 16) | (colours.c & BITMASK));
  BLE.poll();
  delay(50);
  dbaCharacteristic.writeValue(db);
  BLE.poll();
  delay(50);
}

void onPDMdata() {  
  int bytesAvailable = PDM.available();// query the number of bytes available  
  PDM.read(sampleBuffer, bytesAvailable);// read into the sample buffer
  samplesRead = bytesAvailable / 2;// 16-bit, 2 bytes per sample
}