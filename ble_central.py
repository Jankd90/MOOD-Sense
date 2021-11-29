import time
from bluepy import btle
import struct, os
from concurrent import futures
import sys
from influxdb import InfluxDBClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#SECRET_KEY = os.environ.get("SECRET_KEY")#

global addr_var
global delegate_global
global perif_global
#https://simonhearne.com/2020/pi-influx-grafana/
addr_var = ['a2:07:f1:8f:60:43', 'ee:85:31:d8:af:ea']
CHARACTERISTIC_UUID = "19b10012-e8f2-537e-4f6c-d104768a1214"
char_uuid = "19b10012-e8f2-537e-4f6c-d104768a1214"
char_uuid2 = "19b10013-e8f2-537e-4f6c-d104768a1214" 
char_uuid3 = "19b10014-e8f2-537e-4f6c-d104768a1214" 
char_uuid4 = "19b10015-e8f2-537e-4f6c-d104768a1214" 
char_uuid5 = "19b10016-e8f2-537e-4f6c-d104768a1214"
char_uuid6 = "19b10017-e8f2-537e-4f6c-d104768a1214"  

delegate_global = []
perif_global = []
[delegate_global.append(0) for ii in range(len(addr_var))]
[perif_global.append(0) for ii in range(len(addr_var))]

client = InfluxDBClient('localhost', 8086, 'root', 'root', 'db1')

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
        global addr_var
        global client
        global delegate_global
        #print(int.from_bytes(data, byteorder=sys.byteorder),cHandle)
        for ii in range(len(addr_var)):
            if delegate_global[ii]==self:
                
                if cHandle == 21 or cHandle == 24:
                    adr = "{0}:{1}".format(addr_var[ii],cHandle-1) 
                    value = int.from_bytes(data[:2], byteorder=sys.byteorder)
                    self.write_to_db(adr, value)
                    adr = "{0}:{1}".format(addr_var[ii],cHandle+1) 
                    value = int.from_bytes(data[2:], byteorder=sys.byteorder)
                    self.write_to_db(adr, value)
                else:
                    adr = "{0}:{1}".format(addr_var[ii],cHandle) 
                    value = int.from_bytes(data, byteorder=sys.byteorder)
                    self.write_to_db(adr, value)
                
                
                
                
              #  try:
                    #data_decoded = struct.unpack("b",data)
                    #perif_global[ii].writeCharacteristic(cHandle,struct.pack("b",55))
                #print("Address: "+addr_var[ii])
                    #print(data_decoded)
              #      return
              #  except:                    
              #      pass
              #  try:
                    #data_decoded = data.decode('utf-8')
                    #perif_global[ii].writeCharacteristic(cHandle,struct.pack("b",55))
             #       print("Address: "+addr_var[ii])
                    #print(data_decoded)
              #      return
               # except:
                #    return

    
def perif_loop(perif,indx):
    while True:
        try:
            if perif.waitForNotifications(1):
                #print("waiting for notifications...")
                continue
        except:
            try:
                perif.disconnect()
            except:
                pass
            print("disconnecting perif: "+perif.addr+", index: "+str(indx))
            reestablish_connection(perif,perif.addr,indx)
            


def reestablish_connection(perif,addr,indx):
    while True:
        try:
            print("trying to reconnect with "+addr)
            perif.connect(addr)
            setup_notifications(perif)
            print("re-connected to "+addr+", index = "+str(indx))
            return
        except:
            continue

                    
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


def establish_connection(addr):
    global delegate_global
    global perif_global
    global addr_var

    while True:
        try:
            for jj in range(len(addr_var)):
                if addr_var[jj]==addr:
                    print("Attempting to connect with "+addr+" at index: "+str(jj))
                    p = btle.Peripheral(addr)
                    perif_global[jj] = p
                    p_delegate = MyDelegate(addr)
                    delegate_global[jj] = p_delegate
                    p.withDelegate(p_delegate)
                    print("Connected to "+addr+" at index: "+str(jj))
                    setup_notifications(p)
                    perif_loop(p,jj)
        except:
            print("failed to connect to "+addr)
            continue


ex = futures.ProcessPoolExecutor(max_workers = os.cpu_count())
results = ex.map(establish_connection,addr_var)