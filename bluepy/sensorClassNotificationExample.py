from bluepy.btle import UUID, Peripheral, DefaultDelegate
import time
import struct

# sensor notification handle of TI cc2540 sensorTag
sensors = {'accel':{'name': 'accelerometer','handle' : 48}, \
            'temp' :{'name': 'IR temperature','handle' : 37}, \
            'key' :{'name': 'simple key','handle' : 107}
           }

# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

# notification callback
class mDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        # ... initialise here
    def handleNotification(self, cHandle, data):
    	# check cHandle and process 'data'
        if cHandle == sensors['temp']['handle']:
            # read 2 unsigned 16 bits data
            (objT, ambT) = struct.unpack('HH', data)
            ambienTempInDegree = ambT/128.0
            print sensors['temp']['name'] + ':' + '{0:2.1f}'.format(ambienTempInDegree)
        elif cHandle == sensors['accel']['handle']:
            accRawData = struct.unpack('bbb',data)
            print sensors['accel']['name'] + ':' + '{0:s}'.format(accRawData)
        elif cHandle == sensors['key']['handle']:
                keyData = struct.unpack('B',data)
                print sensors['key']['name'] + ':' + '{0:d}'.format(keyData[0])
        else:
            print (cHandle)

class sensorBase:
    #sensor and notification on-off
    #sensorOn  = struct.pack("B", 0x01)
    sensorOff = struct.pack("B", 0x00)
    notificationOn = struct.pack('<bb', 0x01, 0x00)
    notificationOff = struct.pack('<bb', 0x00, 0x00)

    # intialize
    def __init__(self,periph,svcUUID,dataUUID,confUUID,sensorOn):
        self.periph = periph
        self.svcUUID = _TI_UUID(svcUUID)
        self.confUUID = _TI_UUID(confUUID)
        self.dataUUID = _TI_UUID(dataUUID)
        self.sensorOn = sensorOn
        if (svcUUID == 0xFFE0):
            self.service = self.periph.getServiceByUUID(svcUUID)
        else:
            self.service = self.periph.getServiceByUUID(self.svcUUID)
        self.confChar = None
        self.dataChar = None
        self.notifyDescriptor = None

    def enableSensor(self):
        self.confChar = self.service.getCharacteristics(self.confUUID)[0]
        self.confChar.write(self.sensorOn)

    def enableNotification(self):
        self.notifyDescriptor = self.service.getDescriptors(forUUID=0x2902)[0]
        self.notifyDescriptor.write(self.notificationOn)

    def readData(self):
        self.dataChar = self.service.getCharacteristics(self.dataUUID)[0]
        return self.dataChar.read()

    def readConfiguration(self):
        return self.confChar.read()

    def writeData(self,data):
        self.dataChar = self.service.getCharacteristics(self.dataUUID)[0]
        self.dataChar.write(data)

    def writeConfiguration(self,data):
        self.confChar = self.service.getCharacteristics(self.confUUID)[0]
        self.confChar.write(data)

    def disconnect(self):
        self.periph.disconnect()

#sensorTag MAC address
sensorTagMACaddress = "BC:6A:29:AC:48:40"

#Ir temperature sensor
irTempSvcUUID  = 0xAA00 # ir temp sensor service uuid
irTempDataUUID = 0xAA01 # ir temp sensor data uuid
irTempConfUUID = 0xAA02 # ir temp sensor configuration uuid
irTempSensorOn = struct.pack("B", 0x01)

#Accelerometer sensor ble info osensorOn  = struct.pack("B", 0x01)f cc2540
accSvcUUID  = 0xAA10 # accelerometor service uuid
accDataUUID = 0xAA11 # accelerometor data uuid
accConfUUID = 0xAA12 # accelerometer configuration uuid
accSensorOn = struct.pack("B", 0x01)

# simple key service for cc2540 sensortag: notification only
keySvcUUID = 0xFFE0
keyDataUUID = 0xFFE1
keyConfUUID = 0x0000
keySensorOn = 0 # 0 means none

# test service : LED cc2540 sensorTag
testSvcUUID  = 0xAA60 # accelerometor service uuid
testDataUUID = 0xAA61 # accelerometor data uuid
testConfUUID = 0xAA62 # accelerometer configuration uuid
testSensorOn = 0 # 0 means none

# connect sensorTag
p = Peripheral(sensorTagMACaddress)

# set notification callback
p.setDelegate( mDelegate() )

# instantiation of sensor object
irTemp = sensorBase(p,irTempSvcUUID,irTempDataUUID,irTempConfUUID,irTempSensorOn)
accel = sensorBase(p,accSvcUUID,accDataUUID,accConfUUID,accSensorOn)
key = sensorBase(p,keySvcUUID,keyDataUUID,keyConfUUID,keySensorOn)
test = sensorBase(p,testSvcUUID,testDataUUID,testConfUUID,testSensorOn)

# enable sensor
irTemp.enableSensor()
accel.enableSensor()

# wait until sensor is ready
time.sleep(2)

# read sensor data couple of times for test
for i in range(1,3):
  rawAccel=struct.unpack('bbb',accel.readData())
  print 'rawAcceleration:{0:s}'.format(rawAccel)

# test LEDs
LED1blink = struct.pack('B',0x81)
LED2blink = struct.pack('B',0x82)
LEDoff = struct.pack('B',0x00)

test.writeConfiguration(LED1blink)
time.sleep(2)
test.writeConfiguration(LED2blink)
time.sleep(2)
test.writeConfiguration(LEDoff)

# enable notation for sensor
irTemp.enableNotification()
accel.enableNotification()
key.enableNotification()

# Main loop --------
while True:
    if p.waitForNotifications(1):
        # handleNotification() was called
       continue

    print "Waiting..."
    # Perhaps do something else here
