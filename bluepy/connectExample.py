from bluepy.btle import UUID, Peripheral
import time
import struct


# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

# cc2540 sensorTag MAC address
sensorTagMACaddress = "BC:6A:29:AC:48:40"

#sensor on-off
# sturct.pack convert python value into C type
# B : unsigned char
sensorOn  = struct.pack("B", 0x01)
sensorOff = struct.pack("B", 0x00)

#Accelerometer sensor ble info of cc2540
svcUUID  = _TI_UUID(0xAA10) # accelerometor service uuid
dataUUID = _TI_UUID(0xAA11) # accelerometor data uuid
confUUID = _TI_UUID(0xAA12) # accelerometer configuration uuid 


# connect
device = Peripheral(sensorTagMACaddress)
print('waiting for ble peripheral to connect ...')
# get services
service = device.getServiceByUUID(svcUUID);

# get control characteristics handle
confChar = service.getCharacteristics(confUUID) [0]
# get data characteristics handle
dataChar = service.getCharacteristics(dataUUID) [0]

# turn sensor on
confChar.write(sensorOn)

# wait until sensor is ready
time.sleep(2)

# read sensor value
data = dataChar.read()

# convert C-type into python value : 'bbb' => singed char
rawData = struct.unpack('bbb',data)
print(rawData)

# turn sensor off
confChar.write(sensorOff)

# disconnect
device.disconnect()

