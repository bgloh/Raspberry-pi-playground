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
accConfUUID = 0xAA12 # accelerometer configuration uuid

# connect sensorTag
p = Peripheral(sensorTagMACaddress)
# instantiation of accelerometer object
accel = sensorBase(p,accSvcUUID,accConfUUID,accDataUUID)
# enable acceleromter
accel.enable()
# wait until sensor is ready
time.sleep(2.0)
# read data
rawData=struct.unpack('bbb',accel.read())
print(rawData)
#disconnect
accel.disconnect()
