import dict_socket as ds
import multiprocessing
import sys
import socket
import cv2
import silx.opencl.sift
from silx.opencl import ocl
import pyopencl
from os import listdir
from os import mkdir
from os.path import isfile, join
import configparser
import shutil
import numpy
'''
Client -> Server:5000x
Server -> Client:5100x


<-- Dict (imagebase, imagetarget, IP, port)

--> Dict {path: score}



'''

def read_img_cv(p, n=1):
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
        print("RI", e)
        return None

def write_img_cv(p, img):
    try:
        img_str = cv2.imencode(".jpg", img)[1].tostring()
        numpyarray = numpy.fromstring(img_str, dtype=numpy.uint8)
        filebytes = numpyarray.tobytes()
        with open(p, "wb") as f:
            f.write(filebytes)
    except Exception as e:
        print(e)

def copy_img(p1, p2):
    write_img_cv(p2, read_img_cv(p1, 1))



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
        m = mp(ks1, ks2).shape[0]
        #print(m)
        return m
        #return mp(ks1, ks2).shape[0]
    except Exception as e:
        return -1
        with open("threadfail.txt", "w") as f:
            f.write("failed matching minion: "+str(e))



def handler(debug, returndict, ID, ks1, bestplat, todo, imagetarget):
    with open(str(ID)+"s.txt", "w") as f:
        f.write("start")
    #try:
        
       

    #imagebase="//psitf/itf/_ITF/Infrastruktur/Passware Multi-GPU Cluster/_Grafitti Matcher GPU/Bilder"

    mp = silx.opencl.sift.MatchPlan(device=ID, platformid=bestplat, devicetype="GPU")
    D={}
    for i in todo:
        #DOSIFT

        im = read_img_cv(i, 0)
        if debug:
            print(bytes(i, "utf-8"))
        #with open(str(ID)+"_1.txt", "w") as f:
            #f.write(str(imagetarget))
        #with open(str(ID)+"_2.txt", "w") as f:
            #f.write(str(i))
        
        # MATCHING IT WITH ITSELF TO KNOW MAXIMAL MATCHING SCORE TO ELIMINATE FALSE POSITIVES
        #if i == imagetarget:
        #    D[i]=-1
        #    continue
        if im is None:
            if debug:
                print("1.4")
            D[i]=-1
        else:
            if debug:
                print("1.5")
            si = silx.opencl.sift.SiftPlan(template=im, platformid=bestplat,devicetype="GPU", deviceid=ID)
            if debug:
                print("2")
            D[i]=matching_minion(ks1, keypoints_minion(si, im), mp)
            if debug:
                print("3")
    if debug:
        print("fin")
    try:
        returndict[ID]=D
    except Exception as e:
        print("exactly here fails dunno why manager", e)
    if debug:
        print("4")
   
                
    #except Exception as e:
        #print("------\n\n\n\n------HANDLER FAILED", e)
        #with open(str(ID)+"s.txt", "w") as f:
         #   f.write(str(e))


def setup_ocl():
    '''
    Returns a tuple of the best platform ID, number of OpenCL Devices on that platform
    '''
    devices=[]
    platforms=[]
    ###GET LAST PLATFORM, PROBABLY NOT INTEGRATED GPU
    i = pyopencl.get_platforms()
    bestplat=len(i)-1
    i = i[len(i)-1]
    for j in i.get_devices(device_type=pyopencl.device_type.GPU):
        #print(j)
        try:
            #print(j.get_info(pyopencl.device_info.MAX_CLOCK_FREQUENCY))
            #print(j.get_info(pyopencl.device_info.PARENT_DEVICE))
            #print(j.get_info(pyopencl.device_info.PLATFORM))
            #print(type(j.get_info(pyopencl.device_info.PLATFORM)))
            print(j.get_info(pyopencl.device_info.NAME))
            #print(j.get_info(pyopencl.device_info.VENDOR))
            #print(j.get_info(pyopencl.device_info.VENDOR_ID))
            #print(j.get_info(pyopencl.device_info.MAX_CLOCK_FREQUENCY))
            #print("DEVID: ", j.int_ptr)
            devices.append((j.get_info(pyopencl.device_info.VENDOR_ID), j.int_ptr))
            platforms.append(j.get_info(pyopencl.device_info.PLATFORM))
        except Exception as e:
            pass
            #print(e)
    #print("-----")
    #print(len(devices))
    ndevices=len(devices)
    #ndevices=4
    #ndevices = 1
    #print("______")
    
    return bestplat, ndevices


if __name__ == "__main__":
    
    '''
    description
    '''

    config=configparser.ConfigParser()
    config.read("graffiti_config_server.ini")
    ###############
    cndevices=int(config["general"]["ndevices"])
    show=config["general"]["show"]
    server_port=int(config["general"]["server_port"])
    folder = config["general"]["folder"]
    debug = int(config["general"]["debug"])
    ###############
    
    #Server Network Configuration (PORT)
    server = socket.gethostbyname(socket.gethostname())
    #server_port = 63341##

    #Info from Client
    #print("waiting")

    while True:

        request = ds.receive_dict_str(server, server_port)
        ##### RECEIVE IMAGES RAW #####
        if request["way"] == "sendraw":
            #get raw
            import recv_file_bodge as rfb

            rvtimeout = rfb.recv_files_fast(folder, server, server_port+1)
            if not rvtimeout:
                #TIMEOUT
                #CLIENT PROB CRASHED
                #LETS RESTART
                continue

            imagebase = folder
            imagetarget = folder+"/"+request["imagetarget"]
        else:
            imagebase = request["imagebase"]
            imagetarget = request["imagetarget"]

        print("____TARGET:", imagetarget)
        client = request["IP"]
        client_port = int(request["port"])

        
        #OpenCL Platform and number of Devices
        bestplat, ndevices = setup_ocl()

        #Do not use all Devices because of Config File
        if cndevices > 0:
            ndevices=cndevices
            
        #print(bestplat, ndevices)
        #L = List of all absolute paths to images
        L = [imagebase+"/"+each for each in listdir(imagebase)]

        #Calculate Keypoints of Imagetarget
        #print(imagetarget)
        im = read_img_cv(imagetarget,0)
        si = silx.opencl.sift.SiftPlan(template=im, platformid=bestplat,devicetype="GPU", deviceid=0)
        ks1=keypoints_minion(si, im)

        #print("start mp")
        #Start multiprocessing to use more than one GPU Device
        forks = []
        manager = multiprocessing.Manager()
        returndict = manager.dict()
        for i in range(ndevices):
            p=multiprocessing.Process(target=handler, args=(
                debug,
                returndict,
                i,
                ks1,
                bestplat,
                L[i*len(L)//ndevices:(i+1)*len(L)//ndevices],
                imagetarget))
            forks.append(p)
            p.start()
       
    
        for i in forks:
            i.join()
        #print("stopped ps")

        #Fill the results of the child-processes back into one dictionary
        tmp=returndict.copy()


        #for i in tmp:
        #    print(i)


        
        D={}
        for m in tmp:
            D={**D, **tmp[m]}

        #send the results back to the client as a dictionary
        ds.send_dict(client, client_port, D)
        #print(D)
        #print("ok end")

        # DELETE RECEIVED IMAGES
        if request["way"]=="sendraw":
            shutil.rmtree(folder)
        print(len(D))
        for i in D:
            print("ex:", i)
            break
        print("ended successfully")
