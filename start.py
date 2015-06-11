import os, sys
import subprocess, time
import http.server
import json
import tempfile
from http.server import SimpleHTTPRequestHandler

from backend.parseargv import args

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


if __name__ == "__main__":
	temppath = tempfile.gettempdir()
	initFile(os.path.join(temppath, "topage.json"))
	initFile(os.path.join(temppath, "toscript.json"))
	initFile(os.path.join(selfpath, "backend", "cache.json"), "[]")
	initFile(os.path.join(selfpath, "backend", "scache.json"), "{}")
	initFile(os.path.join(selfpath, "www", "config.json"), "{}")

	os.chdir("backend")
	if gSystem("initialize.py "+" ".join(sys.argv[1:])) == 10:
		os.chdir("..")
		print("Update complete. Restarting program.")
		gSystem("start.py ".join(sys.argv[1:]))
		quit()

	argvs = [i for i in sys.argv[1:] if i != "-q"]
	FNULL = open(os.devnull, 'w')

	output = FNULL if args.shh else None

	backend_server = gPopen(["server.py"]+argvs, stdout=output, stderr=output)
	backend_main = gPopen(["main.py"]+argvs, stdout=output, stderr=output)

	time.sleep(0.5)

	os.chdir(os.path.join("..", "www"))
	if os.name != "nt" and os.geteuid() and args.port < 1024:
		prompt = """Root required to host on ports up to 1023, enter your password to elevate permissions.
(Use --port PORT to change ports.)
Password: """
		frontend = subprocess.Popen(["sudo", "-p", prompt, "python3", "-m", "http.server", str(args.port)], stdout=output, stderr=output)
	else:
		frontend = gPopen(["-m", "http.server", str(args.port)], stdout=output, stderr=output)
	
	while not backend_server.returncode and not backend_main.returncode and not frontend.returncode: time.sleep(0.001)
	backend_server.kill()
	backend_main.kill()
	frontend.kill()
	

