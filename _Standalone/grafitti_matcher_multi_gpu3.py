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
import silx.opencl.sift
from silx.opencl import ocl####################

import multiprocessing

import sys
import pyopencl


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
import matplotlib.pyplot as plt
import numpy


from os import mkdir
from os import listdir
from os.path import isfile, join

import time
import os

######################################

def keypoints_minion(si, im):
    # returns silx sift keypoints of an image
    # si = silx.opencl.sift.SiftPlan()
    # im = cv2.imread(path,0)
    try:
        return si.keypoints(im)
    except Exception as e:
        return False
        with open("threadfailkm.txt", "w") as f:
            f.write("failed keypoints minion: "+str(e))




def matching_minion(ks1, ks2, mp):
    # returns matching keypoints (silx sift)
    # ks1 = silx.opencl.sift.SiftPlan().keypoints(image)
    # ks2 = "
    # mp = silx.opencl.sift.MatchPlan()

    try:
        return mp(ks1, ks2).shape[0]
    except Exception as e:
        return -1
        with open("threadfail.txt", "w") as f:
            f.write("failed matching minion: "+str(e))


def show_matching_minion(ks1, ks2, mp, im, img, imagetarget):
    try:
        
        mkp = mp(ks1, ks2)
        if mkp.shape[0] > 0:
            fig, ax = plt.subplots(frameon=False)
            ax.imshow(im, aspect="auto")
            ax.axis('off')
            ax.plot(mkp[:].x, mkp[:].y,'om')
            try:
                folder=imagetarget+"_mkp"
                if not os.path.exists(folder):
                    mkdir(folder)
                f = folder+"/"+img[img.rfind("/")+1:]+"_smk_.png"
                if os.path.isfile(f):
                    os.remove(f)   # Opt.: os.system("rm "+strFile)
                plt.savefig(f, dpi=100)#dpi=100=640x480
                #Image.open(f).convert('L').save(f)
            except Exception as e:
                with open("threadfail.txt", "w") as f:
                    f.write("failed show matching keypoints minion writing file: "+str(e))
                
        return mkp.shape[0]

    
    except Exception as e:
        return -1
        with open("threadfail.txt", "w") as f:
            f.write("failed show matching keypoints minion: "+str(e))
            
def minion(returnvar, i, a, show=True, imagetarget=None):#, a):
    # i = deviceID and minionID
    # a = dictionary of all args
    # returnvar = manager.dict
    try:
        ks1 = a["ks1"]
        portion = a["portion"]
        imagebase = a["imagebase"]
        processor = a["processor"]
        bestplat = a["bestplat"]
        maxres = a["maxres"]
        try:
            maxres = int(maxres) - 50
        except Exception as e:
            with open("threadfail.txt", "w") as f:
                f.write("failed minion resize maxres: "+"==="+str(e))
        mp = silx.opencl.sift.MatchPlan(device=i, platformid=bestplat, devicetype=processor)
        #############################
        localD = {}


      
        for img in portion:
            img=imagebase+"/"+img
            im = cv2.imread(img,0)



        
            ##########################
            #im=PIL.Image.open(img)
            #im.thumbnail((baseresolution,baseresolution))
            ############################
            
            if im is None:
                localD[str(img)] = int(-1)### IMG NOT READABLE RETURN -1
   
            else:

                height, width = im.shape

                
       
            
                if height > maxres or width > maxres:   
                    scalefactor = maxres / width
                    if height > width:
                        scalefactor = maxres / height
                    im = cv2.resize(im,None,fx=scalefactor,fy=scalefactor)
            
                
                si = silx.opencl.sift.SiftPlan(template=im, platformid=bestplat,devicetype=processor, deviceid=i)#####MULTIGPU template=im, 

                if show:
                    localD[str(img)] = show_matching_minion(ks1, keypoints_minion(si, im), mp, im, img, imagetarget)
                    continue
                localD[str(img)] = matching_minion(ks1, keypoints_minion(si, im), mp)
            
            #localD = {"status":"si ok"}
        #
        

      

        returnvar[i]=localD
    except Exception as e:
        returnvar[i]={"status":str(e)}
        with open("threadfail.txt", "a") as f:
            f.write("failed minion: "+str(e))
def handle_minions(ndevices, ks1, portion, imagebase, bestplat, processor, show, imagetarget, maxres):
    '''
    ndevices: ndevices (number of GPUs)
    ks1: ks1 (keypoints of imagetarget)
    portion: L (list of all imagepaths)
    '''
    manager = multiprocessing.Manager()
    returnvar = manager.dict()
    forks = []
    print("ndevices:", str(ndevices))
    for i in range(ndevices):
        p = multiprocessing.Process(target=minion, args=(returnvar, i, {"processor":processor, "maxres":maxres, "bestplat":bestplat, "ks1":ks1, "imagebase":imagebase, "portion":portion[i*len(portion)//ndevices:(i+1)*len(portion)//ndevices]}, show, imagetarget))
        print("started GPU #", str(i))
        forks.append(p)
        p.start()
    i=0
    for proc in forks:
        proc.join()
        print("stopped GPU #", str(i))
        i+=1
    print("_________________")
    print("GPUs STOPPED")
    print("_________________")
    tmp = returnvar.copy()

    s=0
    for i in tmp:
        for j in tmp[i]:
            s+=sys.getsizeof(j)
    print("SIZE: ",s)
    #returnvar=None
    #print(tmp)
    D={}
    for m in tmp:
        D={**D, **tmp[m]}
    return D
    #Return Dict
    #sys.exit()########


#######################################







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


def silx_sift(path, maxres):
    #Returns keypoints
    #im = scipy.misc.imread(path)
    #im = numpy.array(Image.open(path))
    try:
        path = path.replace("\\", "/")
        #s=time.time()
        im = cv2.imread(path,0)

            
        #im = cv2.resize(img, (tarres_w, tarres_h))

        #tarresolution = 400
        #im=PIL.Image.open(path)
        #im.thumbnail((tarresolution,tarresolution))

        
        #print("READ:", time.time()-s)
        ###
        if im is None:
            return None
        #s=time.time()
        height, width = im.shape

        
        
        if height > maxres or width > maxres:   
            scalefactor = maxres / width
            if height > width:
                scalefactor = maxres / height

    
            im = cv2.resize(im,None,fx=scalefactor,fy=scalefactor)
        
        si = silx.opencl.sift.SiftPlan(template=im, platformid=bestplat,devicetype=processor, deviceid=0)#####MULTIGPU
        #si.keypoints(im)
        #print("KEYPOINTS:", time.time()-s)
        return si.keypoints(im)
    except Exception as e:
        print("silx_sift", e)


'''
def match_sift():
    pass
def match_silx_sift(path):
    try:
        ks2 = silx_sift(path)
        if ks2 is None:
            return -1
        #s=time.time()
        mp = silx.opencl.sift.MatchPlan(device=0, platformid=bestplat, devicetype=processor,)#####MULTIGPU
        match = mp(ks1, ks2)#####MULTIGPU
        #print("MATCHING:", time.time()-s)
        return match.shape[0]
    except Exception as e:
        print("match_silx_sift:", e)
def score2dict(p, t):
    try:
        return match_silx_sift(p)
    except Exception as e:
        print(e)
        if t<3:
            return score2dict(p, t+1)
        return -1
'''

   

def do_work():
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

  
    ks1 = silx_sift(imagetarget, maxres)
    print("ks1: ", type(ks1))

    D={}
    c=0
    s=time.time()

##############################
    D = handle_minions(ndevices=ndevices, ks1=ks1, portion=L, imagebase=imagebase, bestplat=bestplat, processor=processor, show=show, imagetarget=imagetarget, maxres=maxres)
##############################

##    for img in L:
##        a=time.time()
##        c+=1
##        path=imagebase+"/"+img
##        print(path)
##
##        D[path]=score2dict(path, 1)
##        print("silx:"+ str(D[path]))
##        
##       
##
##            
##        if c==limit:
##            break
##        #print(c, "--", (time.time()-s)/60, "min passed", (time.time()-s)/60/c*(limit-c),"remaining")
##        startbutton_txt.set(str((time.time()-s)/60/c*(limit-c))[:3]+" min left")
##        pb["value"] = c+1
##        print("---", c, limit)
##        pb.update_idletasks()
##        print("TIME FOR THIS IMG: ", time.time()-a)
##    #print(D)

    #print(D)
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
    
    


    sorted_D = do_work()
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

    devices=[]
    platforms=[]
    ###GET LAST PLATFORM, PROBABLY NOT INTEGRATED GPU
    i = pyopencl.get_platforms()
    bestplat=len(i)-1
    i = i[len(i)-1]
    for j in i.get_devices(device_type=pyopencl.device_type.GPU):
        print(j)
        try:
            print(j.get_info(pyopencl.device_info.MAX_CLOCK_FREQUENCY))
            print(j.get_info(pyopencl.device_info.PARENT_DEVICE))
            print(j.get_info(pyopencl.device_info.PLATFORM))
            print(type(j.get_info(pyopencl.device_info.PLATFORM)))
            print(j.get_info(pyopencl.device_info.VENDOR))
            print(j.get_info(pyopencl.device_info.VENDOR_ID))
            print(j.get_info(pyopencl.device_info.MAX_CLOCK_FREQUENCY))
            print("DEVID: ", j.int_ptr)
            devices.append((j.get_info(pyopencl.device_info.VENDOR_ID), j.int_ptr))
            platforms.append(j.get_info(pyopencl.device_info.PLATFORM))
        except Exception as e:
            print(e)
    print("-----")
    print(len(devices))
    ndevices=len(devices)
    #ndevices=4
    #ndevices = 1
    print("______")
    for i in devices:
        print(i, type(i[0]), type(i[1]))

    try:
        config=configparser.ConfigParser()
        config.read("graffiti_config.ini")
        ###############
        limit=int(config["general"]["limit"])
        prevsize=int(config["general"]["prevsize"])
        processor=config["general"]["processor"]
        columns=int(config["general"]["columns"])
        showlimit=int(config["general"]["showlimit"])
        show=config["general"]["show"]
        maxres = int(config["general"]["maxres"])
        showscore = int(config["general"]["showscore"])
        if show == "True":
            show = True
        else:
            show = False
        wo=int(config["general"]["wo"])#width offset scrollbar
        if int(config["general"]["ndevices"]) > 0:
            ndevices = int(config["general"]["ndevices"])
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
        print("grafitti_config.ini file missing or corrupt")
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
