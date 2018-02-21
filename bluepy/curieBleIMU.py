from bluepy.btle import UUID, Peripheral
import time
import struct
import numpy as np

# Curie BLE sketch_curieBle.ino central program
# file location : Arduino Web Editor

# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

# CurieNano MAC address
MACaddress = "84:68:3E:04:5E:B5"

#led  on-off
# sturct.pack convert python value into C type
# B : unsigned char
ledOn  = struct.pack("B", 0x01)
ledOff = struct.pack("B", 0x00)
svcUUID  = '19B1180F-E8F2-537E-4F6C-D104768A1214' # Euler  service uuid
confUUID = '19B12A19-E8F2-537E-4F6C-D104768A1214' # Euler configuration char  uuid
 
# connect
device = Peripheral(MACaddress)
print('waiting for ble peripheral to connect ...')

# get services
service = device.getServiceByUUID(svcUUID);


# get control characteristics handle
confChar = service.getCharacteristics(confUUID)[0]

# blink
#noOfBlink = 10
waitPeriod = 2
print 'connected'

# wait
time.sleep(waitPeriod)

# read roll, pitch, yaw in degrees
for i in range(50):
	rpy=struct.unpack('>hhh',confChar.read())
	[roll,pitch,yaw]=np.array(rpy)/10
	time.sleep(0.2)
	print 'roll:{0:d} pitch:{1:d} yaw:{2:d}'.format(roll,pitch,yaw)

# disconnect
#device.disconnect()
#print('disconnected')

