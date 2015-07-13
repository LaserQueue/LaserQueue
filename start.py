import os, sys
import subprocess, time
import json
import atexit

from scripts.parseargv import args
from scripts.config import *

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath)

def initFile(path, data=""):
	if not os.path.exists(path):
		newfile = open(path, "w")
		newfile.write(data)
		newfile.close()

def gPopen(cmd, stdin=None, stdout=None, stderr=None):
	if os.name == "nt":
		return subprocess.Popen(["py", "-3"] + cmd, stdin, stdout, stderr)
	else:
		return subprocess.Popen(["python3"] + cmd, stdin, stdout, stderr)

def gSystem(cmd):
	if os.name == "nt":
		return os.system("py -3 "+cmd)
	else:
		return os.system("python3 "+cmd)

def cleanup(): 
	try: backend.kill()
	except: pass
	try: frontend.kill()
	except: pass

class dummyProcess:
	def __init__(self):
		self.returncode = None
	def kill(self):
		pass

atexit.register(cleanup) 

if __name__ == "__main__":
	initFile(os.path.join(selfpath, "scripts", "cache.json"), "[]")
	initFile(os.path.join(selfpath, "scripts", "scache.json"), "{}")
	initFile(os.path.join(selfpath, "www", "config.json"), "{}")
	initFile(os.path.join(selfpath, "www", "infotext.md"), "To view our code or report an issue, go to [our GitHub repository](https://github.com/yrsegal/LaserQueue).")

	cprintconf.color = bcolors.CYAN
	cprintconf.name = "Setup"
	os.chdir("scripts")
	if not args.no_init:
		initcode = gSystem("initialize.py "+" ".join(sys.argv[1:]))
		if initcode:
			if initcode == 2560:
				os.chdir("..")
				cprint("Update successful! Restarting server...\n\n\n")
				quit(gSystem("start.py "+" ".join(sys.argv[1:]))/256)
			else:
				quit(initcode/256)

	argvs = [i for i in sys.argv[1:] if i != "-q"]
	FNULL = open(os.devnull, 'w')

	output = FNULL if args.shh else None

	backend_port = int(Config(os.path.join("..","www","config.json"))["port"])

	load_frontend = (args.load_frontend or (not args.load_frontend and not args.load_backend)) and not args.load_none
	load_backend = (args.load_backend or (not args.load_frontend and not args.load_backend)) and not args.load_none


	if load_backend:
		if os.name != "nt" and os.geteuid() and backend_port < 1024:
			cprintconf.color = bcolors.BLUE
			cprintconf.name = "Backend"
			cprint("""Root required on ports up to 1023, attempting to elevate permissions.
			          (Edit config.json to change ports.)""", strip=True)
			backend = subprocess.Popen(["sudo", "-p", " "*(26+len(cprintconf.name)) +"Password: ", "python3", "main.py"]+argvs, stdout=output, stderr=output)
		else:
			backend = gPopen(["main.py"]+argvs, stdout=output, stderr=output)
	else:
		backend = dummyProcess()

	time.sleep(0.5)

	os.chdir(os.path.join("..", "www"))
	if load_frontend:
		if os.name != "nt" and os.geteuid() and args.port < 1024:
			cprintconf.color = bcolors.PURPLE
			cprintconf.name = "HTTP"
			cprint("""Root required on ports up to 1023, attempting to elevate permissions.
			          (Use --port PORT to change ports.)""", strip=True)
			frontend = subprocess.Popen(["sudo", "-p", " "*(26+len(cprintconf.name)) +"Password: ", "python3", "../scripts/http/server.py", str(args.port)], stdout=output, stderr=output)
		else:
			frontend = gPopen(["../scripts/http/server.py", str(args.port)], stdout=output, stderr=output)
	else:
		frontend = dummyProcess()
	
	try:
		while not backend.returncode and not frontend.returncode and not args.load_none: time.sleep(0.001)
	except KeyboardInterrupt:
		print()
		cprintconf.color = bcolors.RED
		cprintconf.name = "Cleanup"
		cprint("Keyboard interrupt recieved, exiting.")
	finally:
		quit(0)
	

