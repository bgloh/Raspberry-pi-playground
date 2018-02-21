from bluepy.btle import UUID, Peripheral
import time
import struct

# Curie BLE example CallbackLED.ino central program

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
svcUUID  = '19B10000-E8F2-537E-4F6C-D104768A1214' # LED  service uuid
confUUID = '19B10001-E8F2-537E-4F6C-D104768A1214' # LEd configuration char  uuid
 
# connect
device = Peripheral(MACaddress)
print('waiting for ble peripheral to connect ...')

# get services
service = device.getServiceByUUID(svcUUID);


# get control characteristics handle
confChar = service.getCharacteristics(confUUID)[0]
# blink
noOfBlink = 10
blinkPeriod = 0.1
print 'connected. start blinking {0:d} times...'.format(noOfBlink)

for i in range(noOfBlink):
  confChar.write(ledOn)
  time.sleep(blinkPeriod)
  confChar.write(ledOff)
  time.sleep(blinkPeriod)

# disconnect
device.disconnect()
print('disconnected')

