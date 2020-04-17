#https://www.analyticsvidhya.com/blog/2019/10/detailed-guide-powerful-sift-technique-image-matching-python/
'''
How it works:
Prompts the user for a target or multiple targets
Prompts for a folder of images
It will search for images in the Imagebase-Folder that are similar to the target(s)

It can do all of the work by it self (Standalone Verison)
Or use a Client-Server infrastucture. You simply need to install the dependencies
and run the server.py script on a server (with a lot of GPUs)
Then run the script on the client side.

the client can send the images via a network, or you can just put them on a shared folder.
'''
#SCRIPT USES ABOUT 150MB RAM PER GPU plus -> 8 -> 2 GB
# Network: 150 Mbit/s if pictures on network location
# CPU 100% on i7-7700
# GPU 10% per device, probably a lot mote, cant run multiple instances on one GPU

# pip install opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10

#silx https://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe?fixForIE=.exe.
# pip install silx
#replace match.py in silx directory (Appdata Programs Python Silx)#################################################
#import silx.opencl.sift
#from silx.opencl import ocl####################
#import pyopencl
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopencl
# pip install path_downlaoded_file (cpython35)

# pip install matplotlib
#python -m pip install Pillow


from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askdirectory
import math
import configparser
import socket

import dict_socket as ds
import send_file_bodge as sfb

import sys

import PIL.Image
import PIL.ImageTk

import cv2

from os import mkdir
from os import listdir
from os.path import isfile, join

import time
import os
import shutil
import multiprocessing

#import matplotlib.pyplot as plt
import numpy

def read_img_cv(p, n=1):
    '''
    p = path to image
    n = cv2 color (1=color, 0=grey, -1=alpha)
    Reads an Image (from unicode path) and returns it as cv2 image
    '''
    import cv2
    import numpy
    try:
        r = cv2.imread(p, n)

        if r is not None:
            return r
        stream = open(p, "rb")
        filebytes = bytearray(stream.read())
        numpyarray = numpy.asarray(filebytes, dtype=numpy.uint8)
        r = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        return r
    except Exception as e:
        print("READ IMG:", e)
        return None

def write_img_cv(p, img):
    '''
    p = path to write to
    img = cv2 image
    Writes an image to a unicode path
    '''
    import cv2
    import numpy
    try:
        img_str = cv2.imencode(".jpg", img)[1].tostring()
        numpyarray = numpy.fromstring(img_str, dtype=numpy.uint8)
        filebytes = numpyarray.tobytes()
        with open(p, "wb") as f:
            f.write(filebytes)
    except Exception as e:
        print(e)

def copy_img(p1, p2):
    '''
    Copies an image from path p1 to path p2
    Works with unicode
    '''
    write_img_cv(p2, read_img_cv(p1, 1))

def resize_minion(L, imagebase, maxres):
    '''
    L = List of filenames (listdir) of images
    imagebase = path to directory where L is
    maxres = int, resolution to resize to
    Resizes a list of images in imagebase to
    imagebase/RESIZED/image.png.jpg <<<
    '''
    import cv2
    for i in L:
        j = imagebase+"/"+i
        img = read_img_cv(j, 0)
        if img is None:
            print("MINION NONE", j)
            continue
        
        h = img.shape[0]
        w = img.shape[1]
        if h > maxres or w > maxres:
            scalefactor = maxres / w
            if h > w:
                scalefactor = maxres / h
            img = cv2.resize(img, None, fx=scalefactor, fy=scalefactor)
        write_img_cv(imagebase+"/RESIZED/"+i+".jpg", img)


def handler(its, imagetarget, L, imagebase, show, maxres, server, server_port, multicore, resize):
    '''
    its = str, how the target should be named for the server
    imagetarget = path to the imagetarget
    L = listdir(imagebase), list of filenames
    imagebase = path of directory of L
    show = bool, show matching keypoints?
    maxres = int, resolution to resize to
    server = str, server IP
    server_port = int, server port
    multicore = bool, should it use multicore for resizing
    resize = bool, should it resize images

    This function spawns the multiprocessses
    Returns a Dictionary with the scores matching to ONE imagetarget

    NO COMMAS IN IMG PATH - NETWORK WILL FAIL (CSV)
    '''
    #get own IP
    client = socket.gethostbyname(socket.gethostname())
    client_port = 53333

    #configparser
    
    #Want to Resize?
    #tarres indicates if the target got resized and saved to imagetarget_TARGET_RESIZED.jpg
    tarres = (False,)

    #Resize all images if resize is True
    if resize:
        # pip install opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10
        import cv2
        
        #delete folder /RESIZED if it already exists and create a new one
        if not os.path.exists(imagebase+"/RESIZED"):
            mkdir(imagebase+"/RESIZED")
        else:
            import shutil
            shutil.rmtree(imagebase+"/RESIZED")
            mkdir(imagebase+"/RESIZED")

        #Multiprocessing Resizing:
        if multicore:
            import multiprocessing

            #determine how many cores the cpu has to know how many subprocesses to spawn
            cores=multiprocessing.cpu_count()#//2 #use half of the cpu cores
            forks = []

            #Spawn the resize_minion() subprocesses:
            #Gives each of them a slice of the whole L
            for i in range(cores):
                p = multiprocessing.Process(target=resize_minion, args=(L[i*len(L)//cores:(i+1)*len(L)//cores], imagebase, maxres))
                forks.append(p)
                p.start()
            for proc in forks:
                proc.join()
            print("finished resizing")
            
        #Singlecore Resizing:
        else:

            #Loop over each image and add the path and filename together
            for i in L:
                j = imagebase + "/" + i
                #print(j)

                #Try to read the image, None if it doesnt work
                img = read_img_cv(j, 0)
                if img is None:
                    print("NONE")
                    try:
                        stream = open(j, "rb")
                        filebytes = bytearray(stream.read())
                        numpyarray = numpy.asarray(filebytes, dtype=numpy.uint8)
                        img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
                        if img is None:
                            print("still NONE", j)
                            continue
                    except Exception as e:
                        print(e)
                        continue
                print("NOT NONE")

                #Print Dimensions of the image:
                #img.shape = [h,w, (byte-depth)]
                print(img.shape)
                w = img.shape[1]
                h = img.shape[0]

                #Calculate scalefactor if the image is bigger than maxres
                #And resize the image
                if h > maxres or w > maxres:
                    scalefactor = maxres / w
                    if h > w:
                        scalefactor = maxres / h
                    img = cv2.resize(img, None, fx=scalefactor, fy=scalefactor)
            
            #Store the (resized) image in subfolder /RESIZED/filename.png.jpg
                print("WRITING")
                write_img_cv(imagebase+"/RESIZED/"+i+".jpg", img)
                print("resized to", imagebase+"/RESIZED/"+i+".jpg")

        #Change LOCAL imagebase to the RESIZED folder
        #Because the resized images will be sent to the server
        #send subfolder ""
        #print("MAGIC DONE DEBUGGINF")
        imagebase = imagebase+"/RESIZED"

    #Read the target image and maybe resize it
    #Save it anyways to imagetarget_TARGET_RESIZED.jpg
    #set tarres to true
    img=read_img_cv(imagetarget, 0)
    if img is None:
        print("COULD NOT RESIZE IMAGETARGET")
    else:
        w = img.shape[1]
        h = img.shape[0]
        if (h > maxres or w > maxres) and resize:
            scalefactor = maxres / w
            if h > w:
                scalefactor = maxres / h
            img = cv2.resize(img, None, fx=scalefactor, fy=scalefactor)
        write_img_cv(imagetarget+"_TARGET_RESIZED.jpg", img)    
        imagetarget=imagetarget+"_TARGET_RESIZED.jpg"
        tarres = (True, imagetarget)
        print("TARGET IS RESIZED/SAVED", imagetarget)
        #get results ""

        #delete subfolder

    #GLOBAL send
    send = True # not shared folder
    #Always send the images, why not?
    ###############################

    ##### SEND IMAGES #####
    # Sending the images as raw data
    if send:
        
        #Copy imagetarget to imagebase
        #So only one folder needs to be sent
        #payload["imagetarget"] is set to just the targets filename.png_TARGET_RESIZED.jpg
        
        import time
        payload={}
        payload["imagetarget"]=imagetarget[imagetarget.rfind("/")+1:]
        copied = False

        #payload["imagetarget"] is changed to its (TARGET_TIMESTAMP) if it needs to be copied
        if not imagetarget[:imagetarget.rfind("/")] == imagebase:
            newtar = its #"TARGET_"+str(int(time.time()))+imagetarget[imagetarget.rfind("."):]
            #print(type(imagetarget), type(imagebase), type(newtar), imagetarget, imagebase, newtar)

            copy_img(imagetarget, (imagebase+"/"+newtar))

            payload["imagetarget"]=newtar# ONLY NAME NOT PATH
            copied = True
        
        # SEND FILE NAME IMAGETARGET
        #already done, payload["imagetarget"]

        #Tell the server the images will be sent raw:
        payload["way"] = "sendraw"

        #Tell the server the clients IP
        payload["IP"]=client

        #Tell the server the port the client is listening for results
        payload["port"]=client_port

        #Send these metainformations as a dictionary to the server
        print("send", payload)
        ds.send_dict(server, server_port, payload)

        #Send the folder imagebase resp. all its content as raw bytes to the server
        import send_file_bodge as sfb
        sfb.send_files_fast(imagebase, server, server_port+1)
        print("sent ALL FILES")

        # Delete copied imagetarget in RESIZED and imagetarget.png_TARGET_RESIZED.jpg
        if tarres[0]:
            os.remove(tarres[1])
        if copied:
            os.remove(imagebase+"/"+newtar)
        ####################################################
        if resize:
            import shutil
            shutil.rmtree(imagebase)

     # Sending Dict with Path to Images on shared Folder
    else:
       
        #Send Metainformation as a dictionary to the server
        payload={}
        payload["way"] = "path"
        payload["imagebase"]=imagebase
        payload["imagetarget"]=imagetarget
        payload["IP"]=client
        payload["port"]=client_port
        print("send", payload)
        ds.send_dict(server, server_port, payload)

    #Wait for the server to calculate and send back the results as a dictionary
    print("waiting...")
    tmp = ds.receive_dict(client, client_port)
    print("GOT STH")

    
    

    D={}
    #for m in tmp:
    #    D={**D, **tmp[m]}
    # D is unsorted

    #Return an unsorted dictionary: tmp={"RECEIVE/image001.jpg": score}
    return tmp
    
    ###################################### /SOCKET

def OpenTarFiles():
    '''
    tkinter GUI: Prompts the User to choose one/some Files
    Returns a list of all file-paths
    '''
    names = list(askopenfilenames(initialdir=".",
                            filetypes =(("All Files","*.*"),),
                            title = "Choose some files."
                            ))
    try:
        global imagetargets
        imagetargets = names
        return names
    except:
        return False

def OpenTarFile():
    '''
    tkinter GUI: Prompts the User to choose one Files
    Returns a string of the file-path
    '''
    name = askopenfilename(initialdir=".",
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
    '''
    tkinter GUI: Prompts the User to choose a Directory (imagebase)
    Returns a string of the Dir-path
    '''
    name = askdirectory(initialdir=".",
                           title = "Choose a folder."
                           )
    try:
        global imagebase
        imagebase = name
        return name
    except:
        return False


def do_work(server, server_port):
    '''
    Manages all the computing:
    Calls the handler() for each imagetarget
    Merges the Dictionaries that it got from the server to one
    Sets the maximum valid score (tarscore)
    Returns the sorted Dictionary
    '''
    global limit
    global showlimit
    global imagebase
    global imagetarget
    global imagetargets
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

    #resize:
    global maxres
    global multicore
    global resize
    global gotresized
    '''
    MULTIPROCESSING:
    things -> L
    tar -> ks1
    split -> ndevices
    gpu -> 
    '''

   

    D={}
    c=0
    s=time.time()

    #Declare its; the current targets name (timestamp)
    global its
    its = "TARGET_"+str(int(time.time()))+imagetarget[imagetarget.rfind("."):]

    

    #List to store all result dictionaries
    listofD = []

    if resize:
        gotresized = True
    else:
        gotresized = False

    #Loop over all imagetargets and call the handler() for each
    #Loop first over all target images, then again if they got resized
    #last Loop is when not resized
    while True:
        print("resize:", resize)
        for t in imagetargets:
            listofD.append({})
            listofD[len(listofD)-1]=handler(its, t, L, imagebase, show, maxres, server, server_port, multicore, resize)
        if not resize:
            break
        resize = False

    # Add the scores together:
    #try:
    global tarscore
    tarscore=0
    
    if True:
        for k in listofD[0].copy():
            #print(k, gotresized)
            if k.find("TARGET_") >= 0:
                print("is target:", bytes(k, "utf-8"))
                for j in listofD[1:]:
                    if k in j:
                        v = j[k]
                    else:
                        print("sadly weird", len(listofD))
                        v=0
                    listofD[0][k]+=v
                continue
            if gotresized:######################### MULTIPLE TARGET PER TARGET
                val = listofD[0].pop(k, 0)
                listofD[0][k[:-4]]=val
                #print(k, "to", k[:-4])
            for j in listofD[1:]:
                #j[k] two k possible
                if k in j:
                    v = j[k]
                else:
                    try:
                        v = j[k[:-4]]
                    except:
                        v=0#WTF?
                
                listofD[0][k[:-4]]+=v
    #except Exception as e:
    #    print("Adding scores:", e)
        #print("k:", k, "j", j, "listD0:", listofD[0])
    ############
    #for i in listofD[0]:
        #print(i, listofD[0][i])
    D=listofD[0]
    


    for d in listofD:
        print("LEN:", len(d))
    #for k in listofD[0]:
    #    print(k)

    print(bytes(imagetarget, "utf-8"))
    print(bytes(its, "utf-8"))
    print("___________")
    tarscore += listofD[0]["RECEIVE/"+its]

    #if ("RECEIVE/"+its) not in listofD[0]:
    #    print("sadly target (score) not in D")
    #    for k in listofD[0]:
    #        if k.find("TARGET")>=0:
    #            print(k)
    #            print(imagetarget)
    #            tarscore+=listofD[0]["RECEIVE/"+its]
    #    print("printed all targets in D")
    

    
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
    '''
    This Function is executed when the Button "Run" is pressed
    It starts the calculation
    '''
    global sorted_D
    global server_ip
    global server_port
    
    
    sorted_D = do_work(server_ip, server_port)
    Window(root)


def callback(event):
    '''
    This Function is executed when the User clicks on a Label (image) in the GUI
    it prints (filename/path, SCORE) of the clicked image and copies that name/path to clipboard 
    '''
    global root

    #Get attribute "text" of the clicked event / label
    t = event.widget.cget("text")
    if config["general"]["cc"]=="NAME":
        t=t[t.rfind("/")+1:]
    
    #Separate score from name
    print(str(bytes(t[:t.find("#")], "utf-8"))[2:-1], t[t.find("#")+1:])

    #Add to clipboard
    root.clipboard_clear()
    root.clipboard_append(t[:t.find("#")])############################################## APPEND WEIRD BYTES THAT CANT BE PRINTED? DOES IT WORK?
    root.update() # now it stays on the clipboard after the window is closed

def on_mousewheel(event):
    '''
    scroll the Scrollbar
    '''
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")



if __name__ == '__main__':
    '''
    Main Function
    This only runs if the script is not started as a subprocess
    '''

    multiprocessing.freeze_support()


    #Import all dependencies


    #Start Timing
    starttime=time.time()

    global server_ip
    global server_port

    #Read the config file
    #And prompt the user for File and Directory
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
        resize=config["general"]["resize"]
        multicore=config["general"]["multicore"]
        
        if resize == "True":
            resize=True
        else:
            resize=False

        if multicore == "True":
            multicore=True
        else:
            multicore=False
        
        if show == "True":
            show = True
        else:
            show = False
        wo=int(config["general"]["wo"])#width offset scrollbar
        
            
        #imagebase = config["files"]["search_in"]
        #imagetarget = config["files"]["search_for"]
        #if config["files"]["ask_at_run"]=="True":
        
        
        imagetarget = OpenTarFiles()
        imagetargets = imagetarget
        print(imagetarget)
        imagetarget=imagetarget[0]
        
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

        
        #print(listdir(imagebase))
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
        '''
        THE GUI
        '''
        def __init__(self, master=None):
            global sorted_D
            global prevsize
            global imagebase
            global resize
            
            Frame.__init__(self, master)
            self.master = master
            self.pack(fill=BOTH, expand=1)
            j=0
            k=0
            l=0
            labeldict = {}

            #When finished processing, print general info:
            print("_________________")
            print("pictures processed: ", len(sorted_D))
            #print(sorted_D)
            print("took seconds:", time.time()-starttime)
            print("imgtarget score:", tarscore)
            print("__________________")

            ######################################################
            #Loop over the sorted results and dispay the good ones
            ######################################################

            for i in sorted_D:
                #print the filename
                print(bytes(i[1], "utf-8"))

                #Dont Show the Target Image itself:
                if i[1].find("TARGET_")>=0:
                    continue

                #Handle the failed images:
                if i[0]<0:
                    print("-1", i[1])
                    break
                    continue
                    #break
                    #continue -> nothing better will come, but you see how many/which ones failed

                #Handle the too good to be true images:
                if i[0]>tarscore:
                    continue

                #Handle images that are below the showscore threshhold
                if i[0]<showscore:
                    break
                    continue
                    
                # m = path of shown image
                # needed to display it
                m=i[1]
                if i[1].rfind("/")>0:
                    m=imagebase+"/"+i[1][i[1].rfind("/")+1:]
                
                #print(m)

                #Open the image with PIL
                img=PIL.Image.open(m)
                
                #Make the image tkinter compatible and resize it
                img.thumbnail((prevsize,prevsize))
                render=PIL.ImageTk.PhotoImage(img)
                
                #Create a Label on the black canvas and add it to the labeldict (the visible image)
                labeldict[m]=Label(canvas, image=render, text=m+"#"+str(i[0]))
                
                #Render it and add the onclick action
                labeldict[m].image=render
                labeldict[m].bind("<Button-1>", lambda e: callback(e))

                #jump to nexst line
                if j==columns:
                    k+=1
                    j=0
                
                #Show the Label on the canvas
                canvas.create_window(j*prevsize, k*prevsize, window=labeldict[m], anchor=NW)
                j+=1
                l+=1
                canvas.config(height=l*prevsize)
                canvas.update()

                #Stop if trying to show too many images
                if l==showlimit:
                    break

            
    
    #The text shown in the upper left corner of the GUI
    info = Label(root, text="Speed: 10 pictures/sec\nConfig Datei: graffiti_config.ini\nLinksklick auf ein Bild \num den Dateinamen/Pfad zu kopieren.\n! Crashes at some PNG files", font=("Helvetica", 12), anchor=NW, justify=LEFT, compound=TOP)
    info.place(x=0, y=0, height=prevsize, width=prevsize*1.5)

    #Progressbar: only used in standalone verison
    pb = ttk.Progressbar(info, orient="horizontal", length=prevsize, mode="determinate")
    pb.pack(side=BOTTOM)
    pb["maximum"] = limit
    pb["value"] = 0
    pb.update_idletasks()

    #The Start Button "Run"
    startbutton_txt = StringVar()

    startbutton = Button(info, textvariable=startbutton_txt, command=do_all)
    startbutton.pack(side=BOTTOM)
    startbutton_txt.set("Run")

    #Black Canvas:
    canvas = Canvas(root, bg="Black", width=columns*prevsize+wo, height=math.ceil(showlimit/columns)*prevsize)
    canvas.pack()
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    #Scrollbar:
    scrollbar = Scrollbar(canvas, orient=VERTICAL, command=canvas.yview)
    scrollbar.place(relx=1, rely=0, relheight=1, anchor=NE)
    canvas.config(yscrollcommand=scrollbar.set, scrollregion=(0,0,0,math.ceil(showlimit/columns)*prevsize))
    #app=Window(root)

    #GUI Window Title and Size:
    root.wm_title("Graffiti Matcher Client")
    root.geometry(str(int(columns*prevsize+wo+prevsize*1.5))+"x"+str(int(4*prevsize)))

    #tkinter GUI mainloop, after that (after user clicks Run button) the whole program runs
    root.mainloop()
