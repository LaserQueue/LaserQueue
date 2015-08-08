#!/usr/bin/env python3
import os, sys
import subprocess, time
import json
import atexit

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath) # Make sure we're in the right directory

if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 4):
	from cprints import cprint, cprintconf, bcolors

	cprintconf.color = bcolors.DARKRED
	cprintconf.name = "Error"
	version = sys.version.split(" ")[0]

	cprint("""The version of Python is outdated.
		Found: {}
		Required: 3.4+
		Please update to the correct version.""".format(version), 
		color=bcolors.DARKRED, strip=True)
	quit()

# Allow importing from scripts
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
from parseargv import args
from config import *

def initFile(path, data=""):
	"""
	Make a file if it doesn't exist.
	"""
	if not os.path.exists(path):
		newfile = open(path, "w")
		newfile.write(data)
		newfile.close()
		if os.name != "nt" and not os.geteuid():
			try:
				uid = os.environ.get('SUDO_UID')
				gid = os.environ.get('SUDO_GID')
				if uid:
					os.chown(path, int(uid), int(gid))
			except: 
				cprint("WARNING: {} created as root.".format(os.path.basename(path)), color=bcolors.YELLOW)

def gPopen(cmd, stdin=None, stdout=None, stderr=None):
	"""
	Run a non-blocking command with python, independent of windows vs *nix.
	"""
	if os.name == "nt":
		return subprocess.Popen(["py", "-3"] + cmd, stdin, stdout, stderr)
	else:
		return subprocess.Popen(["python3"] + cmd, stdin, stdout, stderr)

def gSystem(cmd):
	"""
	Run a blocking command with python, independent of windows vs *nix.
	"""
	if os.name == "nt":
		return os.system("py -3 "+cmd)
	else:
		return os.system("python3 "+cmd)

def cleanup():
	"""
	Clean up threads left behind.
	"""
	try: backend.kill()
	except: pass
	try: frontend.kill()
	except: pass

class dummyProcess:
	"""
	An object that can be called instead of a Popen.
	"""
	def __init__(self):
		self.returncode = None
	def kill(self):
		pass

atexit.register(cleanup) # Make sure cleanup gets called on exit

if __name__ == "__main__":
	cprintconf.name = "Startup"
	cprintconf.color = bcolors.GREEN
	# Initialize all needed files
	initFile(os.path.join(selfpath, "scripts", "cache.json"), "[]")
	initFile(os.path.join(selfpath, "scripts", "scache.json"), "{}")
	initFile(os.path.join(selfpath, "www", "config.json"), "{}")
	initFile(os.path.join(selfpath, "www", "infotext.md"), "To view our code or report an issue, go to [our GitHub repository](https://github.com/LaserQueue/LaserQueue).")
	initFile(os.path.join(selfpath, "www", "dist", "js", "plugins.js"))

	# Do setup
	cprintconf.color = bcolors.CYAN
	cprintconf.name = "Setup"
	os.chdir("scripts") # Move to the right directory
	if not args.no_init:
		initcode = gSystem("initialize.py "+" ".join(sys.argv[1:])) # Run initialize with all arguments
		if initcode:
			if initcode == 2560: # If the update exit code was called
				os.chdir("..")
				cprint("Update successful! Restarting server...\n\n\n")
				quit(gSystem("start.py "+" ".join(sys.argv[1:]))/256) # Restart this script
			else:
				quit(initcode/256) # Quit if something went wrong
	else:
		cprint("Skipping initialization.", color=bcolors.YELLOW)

	argvs = [i for i in sys.argv[1:] if i != "-q"]
	FNULL = open(os.devnull, 'w') # If the silent arg is called, this is where data will go.

	output = FNULL if args.shh else None

	backend_port = int(Config(os.path.join("..","www","config.json"))["port"]) # Get the port to host the backend from

	# Based on the args, load frontend, backend, or neither.
	load_frontend = (args.load_frontend or (not args.load_frontend and not args.load_backend)) and not args.load_none
	load_backend = (args.load_backend or (not args.load_frontend and not args.load_backend)) and not args.load_none


	passprompt = "{}Password: ".format(cprintconf.whitespace()[1:])

	if load_backend: # Make sure that we're at the correct permission level
		if os.name != "nt" and os.geteuid() and backend_port < 1024:
			cprintconf.color = bcolors.BLUE
			cprintconf.name = "Backend"
			cprint("""Root required on ports up to 1023, attempting to elevate permissions.
			          (Edit config.json to change ports.)""", strip=True)
			# Run the backend with sudo
			backend = subprocess.Popen(["sudo", "-p", passprompt, "python3", "main.py"]+argvs, stdout=output, stderr=output)
		else: # Run the backend normally
			backend = gPopen(["main.py"]+argvs, stdout=output, stderr=output)
	else: # If we aren't loading the backend, use a dummyProcess so the program doesn't get confused
		backend = dummyProcess()

	time.sleep(0.5)

	os.chdir(os.path.join("..", "www"))
	if load_frontend: # Make sure we're at the correct permission level
		if os.name != "nt" and os.geteuid() and args.port < 1024:
			cprintconf.color = bcolors.PURPLE
			cprintconf.name = "HTTP"
			cprint("""Root required on ports up to 1023, attempting to elevate permissions.
			          (Use --port PORT to change ports.)""", strip=True)
			# Run the frontend with sudo
			frontend = subprocess.Popen(["sudo", "-p", passprompt, "python3", "../scripts/http/server.py", str(args.port)], stdout=output, stderr=output)
		else: # Run the frontend normally
			frontend = gPopen(["../scripts/http/server.py", str(args.port)], stdout=output, stderr=output)
	else: # If we aren't loading the frontend, use a dummyProcess so the program doesn't get confused
		frontend = dummyProcess()

	try:
		# Wait for something to quit
		while not backend.returncode and not frontend.returncode and not args.load_none: time.sleep(0.001)
	except KeyboardInterrupt:
		# Print a cleanup message if exited manually
		print()
		cprintconf.color = bcolors.RED
		cprintconf.name = "Cleanup"
		cprint("Keyboard interrupt received, exiting.")
	finally: # And then, quit
		quit(0)
