import socket
import sys
from os import listdir
import os
import time

def send_files_fast(folder, ip, port):
    try:
        p = listdir(folder)

        mb = 1000000
        print("connecting to:", ip, port)
        s = socket.socket()
        s.connect((ip, port))
        print("connected")
        
        
        for file in p:
            #print(folder+"/"+file)
            if os.path.isdir(folder+"/"+file):
                #print("skipped")
                continue
            #send lenfilename (1) byte
            #print("1")
            s.send(bytes([len(bytes(file,"utf-8"))]))
            #send filename 
            s.send(bytes(file, "utf-8"))
            #send lenfile (8) bytes endianness!
            #print("2")
            s.send(int.to_bytes(os.path.getsize(folder+"/"+file), 8, "big"))
            #send file
            #print("3")
            with open(folder+"/"+file, "rb") as f:
                while True:
                    data = f.read(mb)
                    if not data:
                        break
                    #print("send data")
                    s.send(data)
            #print("3")
        #send 255 to terminate
        s.send(bytes([255]))
        s.close()
        return True
    except Exception as e:
        print(e)


def send_files(folder, ip, port):
    try:
        '''
        folder = string path
        ip = string ip
        port = int port
        ---------------------
        --> len of filename as 8 bit
        --> Filename
        --> Imagebytes
        --> Imagebytes
        --> close connection
        -->...........
        --> 8 bit "11111111"
        '''
        
        
        #print("connected sending")
        p = listdir(folder)

        mb=1000000

        for file in p:
            print("trying to connect")
            s=socket.socket()
            s.connect((ip, port))
            print("send len of name:", str(len(bytes(file, "utf-8"))))
            s.send(bytes([len(bytes(file, "utf-8"))]))#Send 1 Byte = len in bytes of filename
            print("send filename:", file)
            s.send(bytes(file, "utf-8"))#Send Filename as utf 8 string
            
            with open(folder+"/"+file, "rb") as f:   
                while True:
                    data = f.read(mb)
                    if not data:
                        break
                    print("send data")
                    s.send(data)
                    
            
            s.close()
        print("4")
        s = socket.socket()
        s.connect((ip, port))
        s.send(bytes([255]))
        
        
        print("sent stop")
    except Exception as e:
        print(e)
    finally:
        
        s.close()
        return True
if __name__ == "__main__":
    print(send_files_fast("test", "10.0.1.3", 22157))
