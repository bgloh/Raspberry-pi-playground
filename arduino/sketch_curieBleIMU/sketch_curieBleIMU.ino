#include <CurieIMU.h>
#include <CurieBLE.h>
#include <MadgwickAHRS.h>
#include "CurieTimerOne.h"

#define   LED                                           13
#define   BYTES_TO_SEND                                  6 // NUMBER OF BYTES TO SEND
#define   ISR_CALLBACK_FREQUENCY_1HZ                    1000000
#define   ISR_CALLBACK_FREQUENCY_10HZ                   (1000000/10)
#define   ISR_CALLBACK_FREQUENCY_25HZ                   (1000000/25)
#define   MADGWICK_FILTER_FREQUENCY_25HZ                 25
#define   ACCEL_FREQUENCY_200HZ                         200
#define   ACCEL_FREQUENCY_100HZ                         100
#define   ACCEL_FREQUENCY_50HZ                           50
#define   GYRO_FREQUENCY_200HZ                          200
#define   GYRO_FREQUENCY_100HZ                          100
#define   GYRO_FREQUENCY_50HZ                            50
#define   ACCEL_RANGE_2G                                  2
#define   ACCEL_RANGE_4G                                  4
#define   GYRO_RANGE_250DEG_PER_SEC                     250
#define   GYRO_RANGE_125DEG_PER_SEC                     125

// configurations
#define   ISR_CALLBACK_FREQUENCY                        ISR_CALLBACK_FREQUENCY_25HZ
#define   ACCEL_FREQUENCY                               ACCEL_FREQUENCY_50HZ
#define   GYRO_FREQUENCY                                GYRO_FREQUENCY_200HZ
#define   ACCEL_RANGE                                   ACCEL_RANGE_2G 
#define   GYRO_RANGE                                    GYRO_RANGE_250DEG_PER_SEC
#define   MADGWICK_FILTER_FREQUENCY                     MADGWICK_FILTER_FREQUENCY_25HZ

/*****  curieIMU.h
supported values for gyro frequency: 25, 50, 100, 200, 400, 800, 1600, 3200 (Hz)
supported values for accelerometer: 12.5, 25, 50, 100, 200, 400, 800, 1600 (Hz)
supported values gyro rate: 125, 250, 500, 1000, 2000 (degrees/second)
supported values for acceleration: 2, 4, 8, 16 (G) ******************/


// GLOBAL VARIABLES
Madgwick filter;
BLEService EulerService("19B1180F-E8F2-537E-4F6C-D104768A1214"); // BLE Euler Service


// BLE Battery Level Characteristic"
BLECharacteristic EulerAngleChar("19B12A19-E8F2-537E-4F6C-D104768A1214",  // standard 16-bit characteristic UUID
                                                     BLERead | BLENotify | BLEWrite, BYTES_TO_SEND);     // remote clients will be able to read,write, and notify
uint8_t mData[BYTES_TO_SEND] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
                                                     
float g_roll, g_pitch, g_heading;    // Euler angles
bool connected = false; // connected flag

void setup() {
  Serial.begin(9600);
  pinMode(LED,OUTPUT);  

  // start the IMU and filter
  CurieIMU.begin();
  CurieIMU.setGyroRate(GYRO_FREQUENCY); 
  CurieIMU.setAccelerometerRate(ACCEL_FREQUENCY); 
 
  // Set the accelerometer range to 2G
  CurieIMU.setAccelerometerRange(ACCEL_RANGE);
  
  // Set the gyroscope range to 250 degrees/second
  CurieIMU.setGyroRange(GYRO_RANGE);

 // Start Magwick filter
  filter.begin(MADGWICK_FILTER_FREQUENCY);

  
  // Initialize
  // Begin BLE
  BLE.begin();
  
  BLE.setLocalName("EulerMonitor");
  
  BLE.setAdvertisedService(EulerService);  // add the service UUID

  // add characteristics
  EulerService.addCharacteristic(EulerAngleChar);

  // add service
  BLE.addService(EulerService);   

  // assign event handler for connected peripherals
  BLE.setEventHandler(BLEConnected, OnConnectionHandler);

  // assign event handler for disconnected peripherals
  BLE.setEventHandler(BLEDisconnected, DisconnectedHandler);

  // assign event handler for characteristic
  EulerAngleChar.setEventHandler(BLEWritten, CharacteristWrittenHandler);
  
  //EulerAngleChar.setEventHandler(BLESubscribed, SubscriptionHandler);

  // data update notification handler
  EulerAngleChar.setEventHandler(BLEValueUpdated, NotificationHandler);
   
  // set initial value for the characteristic
  EulerAngleChar.setValue(mData,BYTES_TO_SEND);   // initial 2 bytes value for this characteristic
 
  
  // start advertising
  BLE.advertise(); 
  
  // End of BLE setup 
  Serial.println("Bluetooth device active, waiting for connections...");
   
  // Start interrupt
   CurieTimerOne.start(ISR_CALLBACK_FREQUENCY, &RRYupdateIsr);  // set timer and callback
}

void loop() {

  // Poll BLE event
  BLE.poll();

  // Uncomment this to show rpy data on serial port
  // Send RPY to serial monitor
 /* Serial.println("roll(deg),pitch(deg), yaw(deg)"); 
  Serial.print(g_roll);Serial.print("\t");Serial.print(g_pitch);Serial.print("\t");Serial.println(g_heading);
  delay(1000);*/
 }

/********************************************************************************************************/
// Timer1 interrupt service routine
// isr reads CurieIMU motion sensor data and convert them into roll, pitch, and yaw angles
/********************************************************************************************************/

void RRYupdateIsr() {
  int aix, aiy, aiz,gix, giy, giz;  // acceleration and gyroscope data in int16 
  float ax, ay, az,gx, gy, gz;      // acceleration and gyroscope data in float
  uint8_t RollPitchYaw[6];          // RollHighByte RollLowByte PitchHighByte PitchLowByte ...
  static unsigned int loop_cnt =0;  // isr loop counter

  // increase loop counter
  loop_cnt++;
    
   // read raw data from CurieIMU
    CurieIMU.readMotionSensor(aix, aiy, aiz, gix, giy, giz);

    // convert from raw data to gravity and degrees/second units
    ax = convertRawAcceleration(aix);
    ay = convertRawAcceleration(aiy);
    az = convertRawAcceleration(aiz);
    gx = convertRawGyro(gix);
    gy = convertRawGyro(giy);
    gz = convertRawGyro(giz);

    /***** MADGWICK ALGORITHM **************************************/
    // update the MADGWICK filter, which computes orientation
    filter.updateIMU(gx, gy, gz, ax, ay, az);

    // update the heading, pitch and roll using MADGWICK Algorithm
    g_roll = filter.getRoll();
    g_pitch = filter.getPitch();
    g_heading = filter.getYaw();
    /****************************************************************/

    // Update characteristics every two incidents of Interrupt
    if(loop_cnt == 2) {
      
      // convert roll,pitch,yaw from Madgwick algroth into bytes array to send over Bluetooth LE data stream
      RollPitchYawByteStream(g_roll,g_pitch,g_heading, RollPitchYaw);
      
      // update Ble characteristics
      EulerAngleChar.setValue( RollPitchYaw, BYTES_TO_SEND);
      
      // reset loop counter
      loop_cnt = 0;

      // blink LED to indicate isr is working
      if (connected == false)
      timedBlink();
    }
 }

float convertRawAcceleration(int aRaw) {
  // since we are using 2G range
  // -2g maps to a raw value of -32768
  // +2g maps to a raw value of 32767
  
  float a = (aRaw * 2.0) / 32768.0;
  return a;
}

// convert raw gyro value into degree/second
// assuming the range is +-250 degrees/second
float convertRawGyro(int gRaw) {
  // since we are using 250 degrees/seconds range
  // -250 maps to a raw value of -32768
  // +250 maps to a raw value of 32767
  
  float g = (gRaw * 250.0) / 32768.0;
  return g;
}

// timed LED blink
void timedBlink()  
{
  static char toggle = 1;
  digitalWrite(LED, toggle);
  toggle = !toggle;  // use NOT operator to invert toggle value
}

// LED blinking routing
void blinkLED(  const unsigned char DESIRED_COUNT)
{
  static unsigned char counter =0;
  static char toggle = 0;
  counter++;
  if (counter == DESIRED_COUNT)
  {
    toggle ^= 1;
    digitalWrite(LED,toggle);
    counter = 0;
  }
 }

// connect event handler 
void OnConnectionHandler(BLEDevice central) {
  // central connected event handler
  connected = true;
  digitalWrite(LED,1);
  Serial.print("Connected event, central: ");
  Serial.println(central.address());
 }

// disconnect event handler 
void DisconnectedHandler(BLEDevice central) {
  // central disconnected event handler
  connected = false;
  digitalWrite(LED,0);
  Serial.print("Disconnected event, central: ");
  Serial.println(central.address());
}

// characteristics written handler
void CharacteristWrittenHandler(BLEDevice central, BLECharacteristic characteristic) {
  // central wrote new value to characteristic, update LED
  const unsigned char *data = characteristic.value();
  Serial.print("Characteristic event, written: ");
  Serial.println(*data);
}

// subscription handler
// TO DO: still need to figure out what subscription is ??
void SubscriptionHandler(BLEDevice central, BLECharacteristic characteristic){
  Serial.println("subscribed");
   EulerAngleChar.setValue(mData,BYTES_TO_SEND);   
}

// data update notification handler
void NotificationHandler(BLEDevice central, BLECharacteristic characteristic){
  Serial.println("notification hadler");
  EulerAngleChar.setValue(mData,BYTES_TO_SEND);
}

// convert int16 into int8 version 1; DEPRECATED DUE TO ARDUINO COMPILIER WARNING
/* convert int16 into usigned int8
  uint8_t * convertInt16toUchar8(int16_t input) {
  uint8_t output[2] ; 
  output[0]= (uint8_t) ((input & 0xFF00)>>8); // High Byte
  output[1]= (uint8_t) (input & 0x00FF);      // Low  Byte
  return output;
} */


// convert int16 into unsigned int8 array
void convertInt16toUchar8_v2(int16_t input, uint8_t* output) {
  
  output[0]= (uint8_t) ((input & 0xFF00)>>8); // High Byte
  output[1]= (uint8_t) (input & 0x00FF);      // Low  Byte
  
} 

// convert int16 into signed int8
void convertInt16toChar8(int16_t input, int8_t* output) {
  
  output[0]= (int8_t) ((input & 0xFF00)>>8); // High Byte
  output[1]= (int8_t) (input & 0x00FF);      // Low  Byte
  
} 

/**********************************************************************************************************/
// Covert float data byte data array  
// data order ; RollHighByte, RollLowByte, PitchHighByte, PithchLowByte, YawHighByte, YawLowByte
/**********************************************************************************************************/

void RollPitchYawByteStream(float roll, float pitch, float heading, uint8_t* RollPitchYawAngle){

   int16_t roll_int16, pitch_int16, yaw_int16; // roll, pitch, yaw int16 data types
   uint8_t RollM[2], PitchM[2], YawM[2]; // roll, pitch, and yaw angle arrays
  
    // roll, pitch, and yaw angles(degrees) multiplied by a factor of 10 and
    // converted into int16 data type
    roll_int16  =   (int16_t) ( roll * 10);
    pitch_int16 =   (int16_t) ( pitch * 10);
    yaw_int16   =   (int16_t) ( heading * 10);

    // convert int16 into unsigned int8
    convertInt16toUchar8_v2(roll_int16, RollM);
    convertInt16toUchar8_v2(pitch_int16, PitchM);
    convertInt16toUchar8_v2(yaw_int16, YawM);

   // put roll,pitch yaw byte into RollPitchYawAngleArray   
    RollPitchYawAngle[0] =  RollM[0];       // Roll High Byte
    RollPitchYawAngle[1] =  RollM[1];       // Roll Low Byte
    RollPitchYawAngle[2] =  PitchM[0];      // Pitch High Byte
    RollPitchYawAngle[3] =  PitchM[1];      // Pitch Low Byte
    RollPitchYawAngle[4] =  YawM[0];        // Yaw High Byte
    RollPitchYawAngle[5] =  YawM[1];        // Yaw Low Byte
}
/*********************************************************************************************************/


