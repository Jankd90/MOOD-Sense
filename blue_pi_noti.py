"""
ref:
bluepy Documentation: Working with notifications
http://ianharvey.github.io/bluepy-doc/notifications.html
"""
# Python3 example on Raspberry Pi to handle notification from
# ESP32 BLE_notify example.
#
# To install bluepy for Python3:
# $ sudo pip3 install bluepy

from bluepy import btle
import sys

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        #print(type(data))
        #print(dir(data))
        #print(data, cHandle)
        print(int.from_bytes(data, byteorder=sys.byteorder),cHandle)
        #print(data[1])


# Initialisation  -------
address = 'a2:07:f1:8f:60:43'
service_uuid = "19B10010-E8F2-537E-4F6C-D104768A1214"
char_uuid = "19b10012-e8f2-537e-4f6c-d104768a1214"
char_uuid2 = "19b10013-e8f2-537e-4f6c-d104768a1214" 
p = btle.Peripheral(address)
p.withDelegate(MyDelegate())
#p2 = btle.Peripheral(address)
# Setup to turn notifications on, e.g.
print(p.getCharacteristics())
svc = p.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics()[0]
ch2 = svc.getCharacteristics(char_uuid2)[0]

print(ch)
"""
print(type(ch))
print(ch)
print(dir(ch))

peripheral = ch.peripheral
print(type(peripheral))
print(peripheral)

propNames = ch.propNames
print(type(propNames))
print(propNames)

properties = ch.properties
print(type(properties))
print(properties)
"""

"""
Remark for setup_data for bluepy noification-
Actually I don't understand how come setup_data = b"\x01\x00",
and ch.valHandle + 1.
Just follow suggestion by searching in internet:
https://stackoverflow.com/questions/32807781/
ble-subscribe-to-notification-using-gatttool-or-bluepy
"""
setup_data = b"\x01\x00"
#p.writeCharacteristic(ch.valHandle + 1, setup_data)
#p.writeCharacteristic(ch2.valHandle + 1, setup_data)
#svc = p.getServiceByUUID( service_uuid )
#ch = svc.getCharacteristics( char_uuid )[0]
#ch.write( b"\x01\x00" )
#ch2 = svc.getCharacteristics( char_uuid2 )[0]
#ch2.write( setup_data )
#print(int.from_bytes(ch.read(), byteorder=sys.byteorder))
#print(int.from_bytes(ch2.read(), byteorder=sys.byteorder))


#ch_data = p.readCharacteristic(ch.valHandle + 1)
#ch2_data = p.readCharacteristic(ch2.valHandle + 1)

#print(type(ch_data))
#print(ch_data)
#print(type(ch_data))
#print(ch2_data)

print("=== Main Loop ===")

while True:
    print(p.readCharacteristic(ch2.valHandle))
    print(p.readCharacteristic(ch.valHandle))
    if p.waitForNotifications(1):
        # handleNotification() was called
        continue

    print("Waiting...")
    # Perhaps do something else here