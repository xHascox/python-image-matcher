import socket
import sys
import time
from os import mkdir
import os
import shutil

##s = socket.socket()
##s.bind(("localhost", 22153))
##s.listen(10)
##
##src, address = s.accept()
##
##print(address)
##i=0
##mb=1000000
##
##buf=1*mb
##
##t = time.time()
##
##with open("recv.data", "wb") as f:
##    try:
##        while True:
##            f.write(src.recv(buf))
##            i+=1
##            #print(data)
##            if t<=time.time()-1:
##                print("recv", i, "MB", "per sec")
##                i=0
##                t=time.time()
##    finally:
##        src.close()

def recv_files_fast(folder, ip, port, buf=1000000):
    '''
    --> connectiom
    --> lenfilename(1)
    --> filename (lenfilename)
    --> lenfile (8)
    --> file
    --> file
    --> ...
    --> lenfilename 255=11111111 (1)
    --> close

    '''
    try:
        s = socket.socket()
        s.bind((ip, port))
        s.listen(10)

        if not os.path.exists(folder):
            mkdir(folder)
        else:
            shutil.rmtree(folder)
            mkdir(folder)
                    
        m = 0
        start = time.time()

        print("waiting for connection")

        ##################################
        #TIMEOUT SECONDS
        s.settimeout(10)
        src, address = s.accept()
        #################################

        print("connected from", address)
        print("wtf")
        while True:
            #################
            src.settimeout(10)
            #################
            lenfilename = ord(src.recv(1))
            if lenfilename == 255:
                break
            #################
            src.settimeout(10)
            #################
            filename = src.recv(lenfilename).decode("utf-8")
            lenfile = int.from_bytes(src.recv(8), "big")
            #print("LENGTH OF FILE big ENDIAN:", lenfile)

            chunksize = buf
            with open(folder+"/"+filename, "wb") as f:
                while lenfile > 0:
                    if lenfile < chunksize:
                        chunksize=lenfile
                    #################
                    src.settimeout(10)
                    #################
                    data = src.recv(chunksize)
                    f.write(data)
                    lenfile -= len(data)
        src.close()
        s.close()
        return True
    except Exception as e:
        print(e)
        src.close()
        s.close()
        return False

def recv_files(folder, ip, port, buf=1000000):
    try:
        '''
        folder = string path
        ip = string ip
        port = int port
        ---------------------
        --> len of filename as 8 bit
        --> Filename
        --> Imagebytes
        --> close connection
        --> .....
        --> 8 bit "11111111" instead of len
        '''
        s = socket.socket()
        s.bind((ip, port))
        s.listen(10)

        if not os.path.exists(folder):
            mkdir(folder)
        else:
            shutil.rmtree(folder)
            mkdir(folder)
                    
        m = 0
        start = time.time()
        while True:
            
            try:
                print("waitinf for connection")
                src, address = s.accept()
                print("connected from:", address)
                length = ord(src.recv(1))# get 8bit = len of filename
                if length==255:
                    break
                print("length of filename:", length)
                name = src.recv(length).decode("utf-8")# get filename
                
                
                with open(folder+"/"+name, "wb") as f:
                    while True:
                        #print("3")
                        data = src.recv(buf)
                        m+=1
                        if not data:
                            print("breaking")
                            break
                        f.write(data)
                        if start < time.time()-1:
                            print(m, "MB/s")
                            m=0
                            start=time.time()
    
            except Exception as e:
                print(e)
        print("leaving")
    finally:
        src.close
        s.close()

if __name__ == "__main__":
    recv_files_fast("recv", "10.0.1.3", 22157)
