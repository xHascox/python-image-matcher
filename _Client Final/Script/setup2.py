import sys
from cx_Freeze import setup, Executable

##setup(
##    name="Graffiti Matcher Client",
##    version="1.0",
##    description="Client to connect to Graffiti Matcher Server",
##    executables = [Executable("client_multi.py", base = "Win32GUI")])
##

setup(
    name="Graffiti Matcher Client",
    version="1.0",
    description="Client to connect to Graffiti Matcher Server",
    executables = [Executable("client_multi.py")])

