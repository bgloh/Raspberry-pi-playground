# notification example for accelerometer of cc2540 sensortag
from bluepy.btle import DefaultDelegate, UUID, Peripheral
import struct
import time

class mDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
    	# ... perhaps check cHandle
        # ... process 'data'
        if cHandle==48:
        	print 'accelerometer data'
    	# read sensor value
    	data = dataChar.read()
		# convert C-type into python value : 'bbb' => singed char
        accRawData = struct.unpack('bbb',data)
        print(accRawData)
        

# Initialisation  -------
# encoding TI uuid
def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

# cc2540 sensorTag MAC address
sensorTagMACaddress = "BC:6A:29:AC:48:40"

#sensor on-off
# sturct.pack convert python value into C type
sensorOn  = struct.pack("B", 0x01)
sensorOff = struct.pack("B", 0x00)
notificationOn = struct.pack('<bb', 0x01, 0x00)
notificationOff = struct.pack('<bb', 0x00, 0x00)


#Accelerometer sensor ble info of cc2540
svcUUID  = _TI_UUID(0xAA10) # accelerometor service uuid
dataUUID = _TI_UUID(0xAA11) # accelerometor data uuid
confUUID = _TI_UUID(0xAA12) # accelerometer configuration uuid 


p = Peripheral( sensorTagMACaddress )
p.setDelegate( mDelegate() )

# Setup to turn notifications on, e.g.
# service
svc = p.getServiceByUUID( svcUUID )
confChar = svc.getCharacteristics( confUUID )[0]
dataChar = svc.getCharacteristics( dataUUID )[0]
notifyDescriptor = svc.getDescriptors(forUUID=0x2902)[0]

# turn sensor on
confChar.write(sensorOn)

# start notification
notifyDescriptor.write(notificationOn)

# Main loop --------

while True:
    if p.waitForNotifications(1):
        # handleNotification() was called
        continue

    print "Waiting..."
    # Perhaps do something else here