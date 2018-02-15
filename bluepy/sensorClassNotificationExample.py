from bluepy.btle import UUID, Peripheral, DefaultDelegate
import time
import struct
from enum import Enum

# sensor enumeration
sensors = {'accel' : 48,'temp' : 37}


# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

#
class mDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        # ... initialise here
    def handleNotification(self, cHandle, data):
    	# ... perhaps check cHandle
        # ... process 'data'
        if cHandle == sensors['temp']:
            print 'IR temperature data'
            # read 2 unsigned 16 bits data
            (objT, ambT) = struct.unpack('HH', data)
            ambienTempInDegree = ambT/128.0
            print 'temperature[deg]:{0:2.1f}'.format(ambienTempInDegree)
        elif cHandle == sensors['accel']:
            accRawData = struct.unpack('bbb',data)
            print 'acceleromter:{0:s}'.format(accRawData)
        else:
            pass

class sensorBase:
    #sensor on-off
    sensorOn  = struct.pack("B", 0x01)
    sensorOff = struct.pack("B", 0x00)
    notificationOn = struct.pack('<bb', 0x01, 0x00)
    notificationOff = struct.pack('<bb', 0x00, 0x00)

    # intialize
    def __init__(self,periph,svcUUID,confUUID,dataUUID):
        self.periph = periph
        self.svcUUID = _TI_UUID(svcUUID)
        self.confUUID = _TI_UUID(confUUID)
        self.dataUUID = _TI_UUID(dataUUID)
        self.service = None
        self.confChar = None
        self.dataChar = None
        self.notifyDescriptor = None

    def enable(self):
        self.service = self.periph.getServiceByUUID(self.svcUUID)
        self.confChar = self.service.getCharacteristics(self.confUUID)[0]
        self.dataChar = self.service.getCharacteristics(self.dataUUID)[0]
        self.notifyDescriptor = self.service.getDescriptors(forUUID=0x2902)[0]
        self.confChar.write(self.sensorOn)

    def enableNotification(self):
        self.notifyDescriptor.write(self.notificationOn)

    def read(self):
        return self.dataChar.read()

    def readSetting(self):
        return self.confChar.read()

    def disconnect(self):
        self.periph.disconnect()

#sensorTag MAC address
sensorTagMACaddress = "BC:6A:29:AC:48:40"

#Ir temperature sensor
irTempSvcUUID  = 0xAA00 # ir temp sensor service uuid
irTempDataUUID = 0xAA01 # ir temp sensor data uuid
irTempConfUUID = 0xAA02 # ir temp sensor configuration uuid

#Accelerometer sensor ble info of cc2540
accSvcUUID  = 0xAA10 # accelerometor service uuid
accDataUUID = 0xAA11 # accelerometor data uuid
accConfUUID = 0xAA12 # accelerometer configuration uuid

# connect sensorTag
p = Peripheral(sensorTagMACaddress)

# set notification callback
p.setDelegate( mDelegate() )

# instantiation of ir sensor object
irTemp = sensorBase(p,irTempSvcUUID,irTempConfUUID,irTempDataUUID)
# enable ir sensor
irTemp.enable()
# enable notation for ir sensor
irTemp.enableNotification()

# instantiation of acceleromter sensor object
accel = sensorBase(p,accSvcUUID,accConfUUID,accDataUUID)
# enable ir sensor
accel.enable()
# enable notation for ir sensor
accel.enableNotification()

# Main loop --------
while True:
    if p.waitForNotifications(1):
        # handleNotification() was called
        continue

    print "Waiting..."
    # Perhaps do something else here
