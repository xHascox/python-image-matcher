#https://www.analyticsvidhya.com/blog/2019/10/detailed-guide-powerful-sift-technique-image-matching-python/

#SCRIPT USES ABOUT 150MB RAM PER GPU plus -> 8 -> 2 GB
# Network: 150 Mbit/s if pictures on network location
# CPU 100% on i7-7700
# GPU 10% per device, probably a lot mote, cant run multiple instances on one GPU

# pip install opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10

#silx https://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe?fixForIE=.exe.
# pip install silx

#replace match.py in silx directory (Appdata Programs Python Silx)#################################################
#SILX:
import socket
import dict_socket as ds

#import silx.opencl.sift
#from silx.opencl import ocl####################

import multiprocessing

import sys
#import pyopencl


#(4318, 2291888308736)
#sys.exit()


# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopencl
# pip install path_downlaoded_file (cpython35)

#/SILX


# pip install matplotlib
#python -m pip install Pillow

import PIL.Image
import PIL.ImageTk

import cv2

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import math
import configparser

import numpy


from os import mkdir
from os import listdir
from os.path import isfile, join

import time
import os

def handler(imagetarget, L, imagebase, show, maxres, server, server_port):
    '''
    todo must be a list of strings (img path)
    NO COMMAS IN IMG PATH - NETWORK WILL FAIL (CSV)
    '''
    
    ######################################SOCKET
    #send paths to server and get back dict with scores (without resizing images)

    #gethostname
    client = socket.gethostbyname(socket.gethostname())
    client_port = 53333

    payload={}
    payload["imagebase"]=imagebase
    payload["imagetarget"]=imagetarget
    payload["IP"]=client
    payload["port"]=client_port
    print("send", payload)
    ds.send_dict(server, server_port, payload)
    print("waiting...")
    tmp = ds.receive_dict(client, client_port)
    
    print("GOT STH")
    ### 
    

    D={}
    #for m in tmp:
    #    D={**D, **tmp[m]}
    
    # D is unsorted
    return tmp
    
    ###################################### /SOCKET
   

def OpenTarFile():
    name = askopenfilename(initialdir="C:/Users/Batman/Documents/Programming/tkinter/",
                           filetypes =(("All Files","*.*"),),
                           title = "Choose a file."
                           )
    try:
        global imagetarget
        imagetarget = name
        return name
    except:
        return False
    
def OpenDir():
    name = askdirectory(initialdir="C:/Users/Batman/Documents/Programming/tkinter/",
                           title = "Choose a folder."
                           )
    try:
        global imagebase
        imagebase = name
        return name
    except:
        return False


def do_work(server, server_port):
    global limit
    global showlimit
    global imagebase
    global imagetarget
    global mp
    global keypoints_1
    global descriptors_1
    global ks1
    global D
    global c
    
    global L

    global pb
####MULTIGPU
    global bestplat
    global processor
    
    '''
    MULTIPROCESSING:
    things -> L
    tar -> ks1
    split -> ndevices
    gpu -> 
    '''

    # Reduce resolution of target image to get better results:

  
    

    D={}
    c=0
    s=time.time()

##############################
    D = handler(imagetarget, L, imagebase, show, maxres, server, server_port)
##############################

    try:
        sorted_D = sorted(((value, key) for (key,value) in D.items()), reverse=True)
    except Exception as e:
        print("sorting D: ", e)
        sorted_D={}
    return sorted_D

#for i in sorted_D:
#    print(i)
#    img = cv2.imread(i[1])
#    plt.figure()
#    plt.imshow(img)
#plt.show()


#




def do_all():
    global sorted_D
    global server_ip
    global server_port
    
    
    sorted_D = do_work(server_ip, server_port)
    Window(root)


def callback(event):
    global root
    t = event.widget.cget("text")
    if config["general"]["cc"]=="NAME":
        t=t[t.rfind("/")+1:]
    print(t[:t.find("#")], t[t.find("#")+1:])
    root.clipboard_clear()
    root.clipboard_append(t[:t.find("#")])
    root.update() # now it stays on the clipboard after the window is closed

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")



if __name__ == '__main__':

    print(__name__)
    global server_ip
    global server_port
    

    try:
        config=configparser.ConfigParser()
        config.read("graffiti_config_client.ini")
        ###############
        limit=int(config["general"]["limit"])
        prevsize=int(config["general"]["prevsize"])
        processor=config["general"]["processor"]
        columns=int(config["general"]["columns"])
        showlimit=int(config["general"]["showlimit"])
        show=config["general"]["show"]
        maxres = int(config["general"]["maxres"])
        showscore = int(config["general"]["showscore"])
        server_ip = config["general"]["server_ip"]
        server_port = int(config["general"]["server_port"])
        if show == "True":
            show = True
        else:
            show = False
        wo=int(config["general"]["wo"])#width offset scrollbar
        
            
        #imagebase = config["files"]["search_in"]
        #imagetarget = config["files"]["search_for"]
        #if config["files"]["ask_at_run"]=="True":
        
        imagetarget = OpenTarFile()
        imagebase = OpenDir()

        #root=Tk()
        root=Toplevel()

        
        img=PIL.Image.open(imagetarget)
        
        img.thumbnail((prevsize*1.5,prevsize*1.5))
        render=PIL.ImageTk.PhotoImage(img)
        img=Label(root, image=render, text=imagetarget[imagetarget.rfind("/")+1:], font=("Helvetica", 12), anchor=S, justify=LEFT, compound=TOP)
        img.image=render
        img.pack(side=LEFT)
        img.bind("<Button-1>", lambda e: callback(e))

        
        print(listdir(imagebase))
        L = listdir(imagebase)
        if limit>len(L):
            limit=len(L)
        if limit==-1:
            limit=len(L)
        if showlimit==-1:
            showlimit=limit
        if showlimit>len(L):
            showlimit=len(L)
        if showlimit>limit:
            showlimit=limit
    except KeyError:
        print("graffiti_config_client.ini file missing or corrupt")
        print("it should look like this:")
        print(
            '''\n
    [files]
    ask_at_run = True
    search_in = .
    search_for = 0000.jpg
    [general]
    limit = -1
    prevsize = 200
    columns = 3
    showlimit = -1
    wo = 30
    ''')


        sys.exit()
        
    class Window(Frame):
        def __init__(self, master=None):
            global sorted_D
            global prevsize
            
            
            Frame.__init__(self, master)
            self.master = master
            self.pack(fill=BOTH, expand=1)
            j=0
            k=0
            l=0
            labeldict = {}
            print("pictures processed: ", len(sorted_D))
            print(sorted_D)
            
            for i in sorted_D:
                if i[0]<0:
                    print("-1", i[1])
                    continue
                    #break
                    #continue -> nothing better will come, but you see how many/which ones failed
                if i[0]<showscore:
                    break
                img=PIL.Image.open(i[1])
                
                img.thumbnail((prevsize,prevsize))
                render=PIL.ImageTk.PhotoImage(img)
                
                labeldict[i[1]]=Label(canvas, image=render, text=i[1]+"#"+str(i[0]))
                
                labeldict[i[1]].image=render
                labeldict[i[1]].bind("<Button-1>", lambda e: callback(e))
                if j==columns:
                    k+=1
                    j=0
                canvas.create_window(j*prevsize, k*prevsize, window=labeldict[i[1]], anchor=NW)
                j+=1
                l+=1
                canvas.config(height=l*prevsize)
                canvas.update()
                if l==showlimit:
                    break
    info = Label(root, text="Config Datei: graffiti_config.ini\nLinksklick auf ein Bild \num den Dateinamen/Pfad zu kopieren.\n! Crashes at some PNG files", font=("Helvetica", 12), anchor=NW, justify=LEFT, compound=TOP)
    info.place(x=0, y=0, height=prevsize, width=prevsize*1.5)

    pb = ttk.Progressbar(info, orient="horizontal", length=prevsize, mode="determinate")
    pb.pack(side=BOTTOM)
    pb["maximum"] = limit
    pb["value"] = 0
    pb.update_idletasks()

    startbutton_txt = StringVar()

    startbutton = Button(info, textvariable=startbutton_txt, command=do_all)
    startbutton.pack(side=BOTTOM)
    startbutton_txt.set("Run")

    canvas = Canvas(root, bg="Black", width=columns*prevsize+wo, height=math.ceil(showlimit/columns)*prevsize)
    canvas.pack()
    canvas.bind_all("<MouseWheel>", on_mousewheel)


    scrollbar = Scrollbar(canvas, orient=VERTICAL, command=canvas.yview)
    scrollbar.place(relx=1, rely=0, relheight=1, anchor=NE)
    canvas.config(yscrollcommand=scrollbar.set, scrollregion=(0,0,0,math.ceil(showlimit/columns)*prevsize))
    #app=Window(root)
    root.wm_title("Grafitti Matcher GPU")
    root.geometry(str(int(columns*prevsize+wo+prevsize*1.5))+"x"+str(int(4*prevsize)))
    root.mainloop()
