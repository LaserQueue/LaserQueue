import os, sys
import subprocess, time
import http.server
import json
from http.server import SimpleHTTPRequestHandler

from backend.parseargv import args

selfpath = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
	os.chdir(selfpath)

	if os.name != "nt" and os.geteuid():
		temppath = os.path.join(os.path.sep, "tmp")
		if not os.path.exists(os.path.join(temppath, "topage.json")):
			open(os.path.join(temppath, "topage.json"), "w").close()
		if not os.path.exists(os.path.join(temppath, "toscript.json")):
			open(os.path.join(temppath, "toscript.json"), "w").close()
		if not os.path.exists(os.path.join(selfpath, "backend", "cache.json")):
			json.dump([], open(os.path.join(selfpath, "backend", "cache.json"), "w"))
		if not os.path.exists(os.path.join(selfpath, "backend", "scache.json")):
			json.dump({}, open(os.path.join(selfpath, "backend", "scache.json"), "w"))
		if not os.path.exists(os.path.join(selfpath, "www", "config.json")):
			json.dump({}, open(os.path.join(selfpath, "www", "config.json"), "w"))

	os.chdir(os.path.join(os.getcwd(), "backend"))
	os.system("python3 initialize.py "+" ".join(sys.argv[1:]))

	argvs = [i for i in sys.argv[1:] if i != "-q"]
	FNULL = open(os.devnull, 'w')

	output = FNULL if args.shh else subprocess.STDOUT

	backend_server = subprocess.Popen(["python3", "server.py"]+argvs, stdout=output, stderr=output)
	backend_main = subprocess.Popen(["python3", "main.py"]+argvs, stdout=output, stderr=output)

	time.sleep(0.5)

	os.chdir(os.path.join(os.getcwd(), "..", "www"))
	if os.name != "nt" and os.geteuid() and args.port < 1024:
		prompt = """Root required to host on ports up to 1023, enter your password to elevate permissions.
(Use --port PORT to change ports.)
Password: """
		frontend = subprocess.Popen(["sudo", "-p", prompt, "python3", "-m", "http.server", str(args.port)], stdout=output, stderr=output)
	else:
		frontend = subprocess.Popen(["python3", "-m", "http.server", str(args.port)], stdout=output, stderr=output)
	
	while not backend_server.returncode and not backend_main.returncode and not frontend.returncode: time.sleep(0.001)
	backend_server.kill()
	backend_main.kill()
	frontend.kill()
	

