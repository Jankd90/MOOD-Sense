from bluepy import btle
import struct
from influxdb import InfluxDBClient
import time
import sys

addr = '08:1d:54:03:89:70'
CHARACTERISTIC_UUID = "19b10012-e8f2-537e-4f6c-d104768a1214"
char_uuid = "19b10012-e8f2-537e-4f6c-d104768a1214"
char_uuid2 = "19b10013-e8f2-537e-4f6c-d104768a1214" 
char_uuid3 = "19b10014-e8f2-537e-4f6c-d104768a1214" 
char_uuid4 = "19b10015-e8f2-537e-4f6c-d104768a1214" 
char_uuid5 = "19b10016-e8f2-537e-4f6c-d104768a1214"
char_uuid6 = "19b10017-e8f2-537e-4f6c-d104768a1214"  


client = InfluxDBClient('localhost', 8086, 'root', 'root', 'db1')  

def setup_notifications(p):
    characteristics = p.getCharacteristics()
    for char in characteristics:
        if(char.uuid == char_uuid ):  
            c = char
        if(char.uuid == char_uuid2 ):
            c2 = char
        if(char.uuid == char_uuid3 ):
            c3 = char
        if(char.uuid == char_uuid4 ):
            c4 = char
        if(char.uuid == char_uuid5 ):
            c5 = char
        if(char.uuid == char_uuid6 ):
            c6 = char
                      
    setup_data = b"\x01\x00"
    p.writeCharacteristic(c.valHandle + 1, setup_data)
    p.writeCharacteristic(c2.valHandle + 1, setup_data)
    p.writeCharacteristic(c3.valHandle + 1, setup_data)
    p.writeCharacteristic(c4.valHandle + 1, setup_data)  
    p.writeCharacteristic(c5.valHandle + 1, setup_data)  
    p.writeCharacteristic(c6.valHandle + 1, setup_data)  



class MyDelegate(btle.DefaultDelegate):
    def __init__(self,params):
        btle.DefaultDelegate.__init__(self)
    def write_to_db(self, adr, value):
        timestamp = int(time.time()*1000000000)
        #print("Address: "+adr)
        json_body = [
            {
            "measurement": adr,
            "tags": {
            "host": "server01",
            "region": "assen"
            },
            "time": timestamp,
            "fields": {
            "value": value
            }
            }
            ]
        client.write_points(json_body)
    def handleNotification(self,cHandle,data):
        if cHandle == 21 or cHandle == 24:
            adr = "{0}:{1}".format(addr,cHandle-1) 
            value = int.from_bytes(data[:2], byteorder=sys.byteorder)
            self.write_to_db(adr, value)
            adr = "{0}:{1}".format(addr,cHandle+1) 
            value = int.from_bytes(data[2:], byteorder=sys.byteorder)
            self.write_to_db(adr, value)
        else:
            adr = "{0}:{1}".format(addr,cHandle) 
            value = int.from_bytes(data, byteorder=sys.byteorder)
            self.write_to_db(adr, value)
        #print("handling notification...")
##        print(self)
##        print(cHandle)
        #print(value)


p = btle.Peripheral(addr)
p_delegate = MyDelegate(addr)
p.withDelegate(p_delegate)
setup_notifications(p)

def reestablish_connection():
    p.connect(addr)
    setup_notifications(p)

while True:
    try:
        if p.waitForNotifications(1.0):
            continue
    except:
        try:
            p.disconnect()
        except:
            pass
        print("disconnecting perif")
        reestablish_connection()

