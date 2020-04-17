HOW TO INSTALL:

install Python 3.5.4 (choose add to PATH)
(if PATH does not work -> cd to C:\Users\User\AppData\Local\Programs\Python\Python35 and install and run things from there)

python -m pip install opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10
install vcpp build tools (https://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe?fixForIE=.exe.)
python -m pip install silx
Replace match.py in the silx directory (C:\Users\Admin\AppData\Local\Programs\Python\Python35\Lib\site-packages\silx\opencl\sift)
python -m pip install "pyopencl cp35.whl" (https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopencl)
python -m pip install matplotlib
python -m pip install Pillow

GENERAL INFORMATION:

RAM: 200 MB per used GPU, plus some for processing in general = 2 GB for 8 GPUs
CPU: 100% on one core per used GPU (i7-7700)
GPU: 10% (CPU Bottleneck)
Network/Disk: 150 Mbit/s (more when transfering files)

Show information about available OpenCL Devices (CPU & GPU):
cmd: clinfo.exe > clinfo.txt
If nothing is visible, install OpenCL Drivers on CPU and GPU

Config File: grafitti_config_server.ini
Format: 

[general]
; how many GPUs should be used:
ndevice = 8


sys.path:
C:\Users\Admin\Desktop\local Grafitti Matcher GPU
C:\Users\Admin\AppData\Local\Programs\Python\Python35\python35.zip
C:\Users\Admin\AppData\Local\Programs\Python\Python35\DLLs
C:\Users\Admin\AppData\Local\Programs\Python\Python35\lib
C:\Users\Admin\AppData\Local\Programs\Python\Python35
C:\Users\Admin\AppData\Local\Programs\Python\Python35\lib\site-packages

TO STOP THE SERVER:
Ctrl + C 
in the console Window, and wait some seconds it will stop
