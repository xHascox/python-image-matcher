import socket
import multiprocessing
import sys
#import time #create timeout in receive_list/dict ? maybe useless because needed in receive()?

'''
Client -> Server:50003
Server -> Client:50004


server = "10.0.1.3"
server_port = 50003

client = "10.0.1.3"
client_port = 50004
'''



def send_dict(client, client_port, payload):
    '''
    --> dict  -->
    --> key,   -->
    --> value, -->
    --> ...   -->
    --> stop  -->
    receive: starts with utf-8 dict
    client = string of ip "10.0.1.3"
    client_port = int of port 50003
    payload = dictionary {"key":"value"}
    receive: terminated by utf-8 stop
    '''
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((client, client_port))
    except:
        
        print("CONNECTION NOT POSSIBLE")
        return False
    server.send(bytes("dict", "utf-8"))

    for key in payload:
        server.send(bytes(key+",", "utf-8"))
        server.send(bytes(str(payload[key])+",", "utf-8"))

    server.send(bytes("stop", "utf-8"))
    server.close()
    return True
    

def receive_dict_str(server, server_port, buf=256):
    '''
    <-- dict  <--
    <-- key,   <--
    <-- value, <--
    <-- ...   <--
    <-- stop  <--
    '''
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.bind((server, server_port))
        client.listen(8)
        print("waiting for connection--")

        while True:
            try:
                client.settimeout(2)
                client_socket, address = client.accept()
                print("break out")
                break
            except KeyboardInterrupt:
                client.close()
                try:
                    client_socket.close()
                except:
                    pass
                sys.exit()
            except Exception as e:
                #print(e)
                pass
        
        print("connected")
        payload = ""

        while True:
            print("looping")
            try:
                
                if client_socket.recv(4).decode("utf-8") == "dict":
                    print("keyword dict")
                    while True:
                        try:
                            print("get elem")
                            elem = client_socket.recv(buf).decode("utf-8")
                            print("elem")
                            if elem[elem.rfind(",")+1:] == "stop":
                                print(payload, elem)
                                print("stopping")
                                try:
                                    client_socket.close()
                                    client.close()
                                except Exception as e:
                                    print("shit")
                                    #print(e)
                                
                                if elem.rfind(",")>=0:
                                    payload += elem[:elem.rfind(",")]
                                else:
                                    payload=payload[:-1]

                                #print("returning:", payload)
                                payload = payload.split(",")
                                D = {}
                                for el in range(int(len(payload)/2)):
                                    D[payload.pop()]=str(payload.pop())
                                #print(D)
                                return D
                            payload += elem
                            print("I")
                        except Exception as e:
                            print(e)
                        
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
def receive_dict(server, server_port, buf=256):
    '''
    <-- dict  <--
    <-- key,   <--
    <-- value, <--
    <-- ...   <--
    <-- stop  <--
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((server, server_port))
    client.listen(8)

    client_socket, address = client.accept()
    payload = ""

    while True:
        try:
            if client_socket.recv(4).decode("utf-8") == "dict":
                while True:
                    try:
                        elem = client_socket.recv(buf).decode("utf-8")
                        #print(elem)
                        if elem[elem.rfind(",")+1:] == "stop":
                            #print("stopping")
                            try:
                                client_socket.close()
                                client.close()
                            except Exception as e:
                                #print("shit")
                                return bytes(str(e), "utf-8")
                            
                            if elem.rfind(",")>=0:
                                payload += elem[:elem.rfind(",")]
                            else:
                                payload=payload[:-1]

                            #print("returning:", payload)
                            payload = payload.split(",")
                            D = {}
                            for el in range(int(len(payload)/2)):
                                D[payload.pop()]=int(payload.pop())
                            #print(D)
                            return D
                        payload += elem
                        
                    except:
                        pass
                    
        except:
            pass
            
       
def send_list(client, client_port, payload):
    #payload = str()able
    '''
    --> list  -->
    --> elem,  -->
    --> elem,  -->
    --> ...   -->
    --> stop  -->
    receive: starts with utf-8 dict
    client = string of ip "10.0.1.3"
    client_port = int of port 50003
    payload = dictionary {"key":"value"}
    receive: terminated by utf-8 stop
    '''
    payload = (bytes(str(j), "utf-8") for j in payload)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((client, client_port))
    

    
    server.send(bytes("list", "utf-8"))
    #print("sent keyword list")
    for element in payload:
        #print("sending:", element)
        server.send(element+bytes(",", "utf-8"))
    server.send(bytes("stop", "utf-8"))
    #print("sent stop")
    server.close()
    return True
    
def receive_list(server, server_port, buf=256):
    #receives and returns strings
    '''
    <-- list  <--
    <-- elem, <--
    <-- elem, <--
    <-- ...   <--
    <-- stop  <--
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((server, server_port))
    client.listen(8)

    client_socket, address = client.accept()
    
    
    payload = ""
    while True:
        #print("loop1")
        try:
            if client_socket.recv(4).decode("utf-8") == "list":
                while True:
                    #print("loop2")
                    try:
                        elem = client_socket.recv(buf).decode("utf-8")
                        #print(elem)
                        if elem[elem.rfind(",")+1:] == "stop":
                            #print("stopping")
                            try:
                                client_socket.close()
                                client.close()
                            except Exception as e:
                                #print("shit")
                                return bytes(str(e), "utf-8")
                            #print(elem)
                            if elem.rfind(",")>=0:
                                payload += elem[:elem.rfind(",")]
                            else:
                                payload=payload[:-1]
                            #print("returning:", payload)
                            return payload.split(",")
                        payload += elem
                        
                    except:
                        pass
                    
        except:
            pass
            
