# Raspberry-pi-playground

ROS Raspberry Pi 3 image file (Ubuntu Mate Xenial 16.04 and ROS Kinetic) is downloaded from [German Robotics](http://www.german-robot.com/2016/05/26/raspberry-pi-sd-card-image/).

* SSH of Ubuntu Mate is disabled with a default setting.
To turn it on, put `ssh` file on boot directory.
* Tools you need to use raspberry pi
   * Nodejs tools
     * [node-red](https://nodered.org/docs/hardware/raspberrypi)
   * Python tools
     * pip - A tool for installing Python packages; you need `get-pip.py`.
        * useful pip commands : install, uninstall, list, show, freeze
     * virtualenv - a tool to isolate application specific dependencies from a shared Python installation.

## Communication
  ### [__blupy__](https://github.com/IanHarvey/bluepy)- Python interface to Bluetooth LE on Linux
[documentation-bluepy](http://ianharvey.github.io/bluepy-doc/)<br>
Installation from the source and buil locally

```bash  
    $ git clone https://github.com/IanHarvey/bluepy.git
    $ cd bluepy
    $ python setup.py build
    $ sudo python setup.py install
 ```
Command-line tools from _BlueZ_ is good for debugging.<br>
There are instructions for building _BlueZ_ on the Raspberry Pi at [RPi Bluetooth LE](http://www.elinux.org/RPi_Bluetooth_LE).<br>

### bluez how-to
To scan ble devices, **first make sure bluetooth is turned on** <br>
`sudo hciconfig hci0 up`<br>
`sudo hcitool lescan` <br>
Connect with _gatt_ <br>
`gatttool -I -b MAC-address` <br>
Mac-address is something like `BC:6A:29:AC:48:40` <br>
Type `exit` to get out of bluez command line mode <br>

### bluepy mini-tutorial
* #### scan example
To scan ble devices <br>
`$ sudo blescan` <br>
python code : [scanExample.py](https://github.com/bgloh/Raspberry-pi-playground/blob/master/bluepy/scanExample.py) <br>

```python
from bluepy.btle import Scanner, DefaultDelegate

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print "Discovered device: ", dev.addr
        elif isNewData:
            print "Received new data from", dev.addr

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)
```
Run it using python interactive mode <br>
`$ python -i scanExample.py ` <br>
Objects `devices` contains all info. about scanned ble devices.<br><br>
To find the name of a first device from scanned device objects

```python
name = devices[1].getValueText(9); print("name: ",name)
```

To find the name of a second device from scanned device objects  <br>

```python
 name = devices[2].getValueText(9); print("name: ",name)
```
To find the MAC address of a second device from scanned device objects  <br>

```python
 addr = devices[2].addr; print("MAC address: ",addr)
```

* #### connect example
python code : [connectExample.py](https://github.com/bgloh/Raspberry-pi-playground/blob/master/bluepy/connectExample.py) <br>

To run `sudo python connectExample.py`

```python
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

```
**code explanation**

Python struct package allows data type conversion between python data type and C data type. For detailed info, refer to [python struct library docs](https://docs.python.org/2/library/struct.html).
```Python
sensorOn  = struct.pack("B", 0x01)
```
Encode 4 byte UUID into TI UUID

```python
svcUUID  = _TI_UUID(0xAA10)
```


* #### notification example
python code : [notificationExample.py](https://github.com/bgloh/Raspberry-pi-playground/blob/master/bluepy/notificationExample.py) <br>

To run `sudo python notificationExample.py`

```python
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
```

**code explanation** <br>
To **enable notification** from ble peripherals, notification must be enabled by writing to a special characteristic configuration. The SensorTag can be configured to send notifications for every sensor by writing **“01 00”** to the characteristic configuration **< GATT_CLIENT_CHAR_CFG_UUID>** whose UUID is **0x2902** for the corresponding sensor data, the data is then sent as soon as the data has been updated(source: [TI cc2540 sensortag wiki](http://processors.wiki.ti.com/index.php/SensorTag_User_Guide)).<br>
*`<bb` means little-endian binary encoding*.
```python
notificationOn = struct.pack('<bb', 0x01, 0x00)
notificationOff = struct.pack('<bb', 0x00, 0x00)
notifyDescriptor = svc.getDescriptors(forUUID=0x2902)[0]
notifyDescriptor.write(notificationOn)
```
If notafication is sucessful and subscribed data is updated, the new data is available in callback class named **"mDelegate()"**. `data` variable holds new update data and `cHandle` has integer identification number for updated data field. Integer id. no. for `accelerometer data` is `48`.  

```Python
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
```
