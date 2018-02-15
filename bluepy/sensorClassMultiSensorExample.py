from bluepy.btle import UUID, Peripheral
import time
import struct
# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

class sensorBase:
    #sensor on-off
    sensorOn  = struct.pack("B", 0x01)
    sensorOff = struct.pack("B", 0x00)

    # intialize
    def __init__(self,periph,svcUUID,confUUID,dataUUID):
        self.periph = periph
        self.svcUUID = _TI_UUID(svcUUID)
        self.confUUID = _TI_UUID(confUUID)
        self.dataUUID = _TI_UUID(dataUUID)
        self.service = None
        self.confChar = None
        self.dataChar = None

    def enable(self):
        self.service = self.periph.getServiceByUUID(self.svcUUID)
        self.confChar = self.service.getCharacteristics(self.confUUID)[0]
        self.dataChar = self.service.getCharacteristics(self.dataUUID)[0]
        self.enabled = self.confChar.write(self.sensorOn)
    def read(self):
        return self.dataChar.read()
    def readSetting(self):
        return self.confChar.read()
    def disconnect(self):
        self.periph.disconnect()

sensorTagMACaddress = "BC:6A:29:AC:48:40"

#Accelerometer sensor ble info of cc2540
accSvcUUID  = 0xAA10 # accelerometor service uuid
accDataUUID = 0xAA11 # accelerometor data uuid
accConfUUID = 0xAA12 # accelerometer configuration uuid#Accelerometer sensor ble info of cc2540

#Ir temperature sensor
irTempSvcUUID  = 0xAA00 # ir temp sensor service uuid
irTempDataUUID = 0xAA01 # ir temp sensor data uuid
irTempConfUUID = 0xAA02 # ir temp sensor configuration uuid

# connect sensorTag
p = Peripheral(sensorTagMACaddress)

# instantiation of accelerometer object
accel = sensorBase(p,accSvcUUID,accConfUUID,accDataUUID)
# instantiation of ir temp sensor object
irTemp = sensorBase(p,irTempSvcUUID,irTempConfUUID,irTempDataUUID)
# enable acceleromter
accel.enable()
# enable ir temperature sensor
irTemp.enable()
# wait until sensor is ready
time.sleep(2.0)
# read 3 signed bytes data
rawAccel=struct.unpack('bbb',accel.read())

# read 2 unsigned 16 bits data
(objT, ambT) = struct.unpack('HH', irTemp.read())
ambienTempInDegree = ambT/128.0;
print 'raw-accel:{0:s}'.format(rawAccel)
print 'temperature[deg]:{0:2.1f}'.format(ambienTempInDegree)
#disconnect
accel.disconnect()
irTemp.disconnect()
