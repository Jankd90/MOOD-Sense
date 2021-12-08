from bluepy import btle
from influxdb import InfluxDBClient
import time
import sys
import os

addr = '76:3f:d6:62:63:d8'
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

def write_to_db(adr, value):
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


p = btle.Peripheral(addr)
p_delegate = MyDelegate(addr)
p.withDelegate(p_delegate)
#setup_notifications(p)
chars = p.getCharacteristics()
for c in chars:
    print(c)
    if(c.uuid == char_uuid):
        print(c.read())
print("connected")

def read_values():
    for c in chars:
        #print("cool")
        if(c.uuid == char_uuid ):  
            data = c.read()
            #print("reading...", data)
            adr = "{0}:{1}".format(addr,10) 
            value = int.from_bytes(data, byteorder=sys.byteorder)
            #print("reading...", value)
            write_to_db(adr, value)
        if(c.uuid == char_uuid2 ):
            data = c.read()
            adr = "{0}:{1}".format(addr,11) 
            value = int.from_bytes(data, byteorder=sys.byteorder)
            write_to_db(adr, value)
        if(c.uuid == char_uuid3 ):
            data = c.read()
            adr = "{0}:{1}".format(addr,12) 
            value = int.from_bytes(data, byteorder=sys.byteorder)
            write_to_db(adr, value)
        if(c.uuid == char_uuid4 ):
            data = c.read()
            #print(data[0])
            adr = "{0}:{1}".format(addr,13) 
            value = int.from_bytes(data[:2], byteorder=sys.byteorder)
            write_to_db(adr, value)
            adr = "{0}:{1}".format(addr,14) 
            value = int.from_bytes(data[2:], byteorder=sys.byteorder)
            write_to_db(adr, value)
        if(c.uuid == char_uuid5 ):
            data = c.read()
            #print(data[0])
            adr = "{0}:{1}".format(addr,15) 
            value = int.from_bytes(data[:2], byteorder=sys.byteorder)
            write_to_db(adr, value)
            adr = "{0}:{1}".format(addr,16) 
            value = int.from_bytes(data[2:], byteorder=sys.byteorder)
            write_to_db(adr, value)
        if(c.uuid == char_uuid6 ):
            data = c.read()
            adr = "{0}:{1}".format(addr,17) 
            value = int.from_bytes(data, byteorder=sys.byteorder)
            write_to_db(adr, value)
            
    

def reestablish_connection():
    i = 0
    while True:
        try:
            p.connect(addr)
            print("reconnected")
            return
        except:
            print("couldn't reconnect")
            time.sleep(3)
            i = i + 1
            if(i > 10):
                print("restarting")
                p.disconnect()
                os.execl(sys.executable, sys.executable, *sys.argv)
            continue
   
  

while True:
    try:
        #print("try")
        read_values()
        #time.sleep(1.0)
    except:
        try:
            p.disconnect()
        except:
            pass
        print("disconnecting perif")
        reestablish_connection()

