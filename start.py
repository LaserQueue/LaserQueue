import os, sys
import subprocess, time
import http.server
import multiprocessing
import json
from http.server import SimpleHTTPRequestHandler

import argparse
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-n", "--regen-host", help="Regenerate host in config", dest="host",
	action="store_const",const=True,default=False)
parser.add_argument("-h", "--help", help="Show this help message and exit", dest="help",
	action="store_const",const=True,default=False)
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-q", "--quiet", help="Makes the script not give output", dest="shh",
	action="store_const",const=True,default=False)
parser.add_argument("-b", "--queue-backup", help="Backup queue and load from backup on start", dest="backup",
	action="store_const",const=True,default=False)
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen",
	action="store_const",const=True,default=False)
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
args = parser.parse_args()

if args.help:
	parser.print_help()
	quit()

selfpath = os.path.dirname(os.path.realpath(__file__))

def startfrontend():
	http.server.test(HandlerClass=SimpleHTTPRequestHandler, port=args.port)

if __name__ == "__main__":
	os.chdir(selfpath)
	if args.shh:
		newargs = " ".join([i for i in sys.argv[1:] if i != "-q"])
		os.system("cd "+selfpath+"; ./start.sh {0} >/dev/null".format(newargs))
		quit()

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

	backend_server = subprocess.Popen(["python3", "server.py"]+sys.argv[1:])
	backend_main = subprocess.Popen(["python3", "main.py"]+sys.argv[1:])

	time.sleep(0.1)

	os.chdir(os.path.join(os.getcwd(), "..", "www"))
	if os.name != "nt" and os.geteuid() and args.port < 1024:
			prompt = """Root required to host on ports up to 1023, enter your password to elevate permissions.
(Use --port PORT to change ports.)
Password: """
			frontend = subprocess.Popen(["sudo", "-p", prompt, "python3", "-m", "http.server", str(args.port)])
	else:
		frontend = multiprocessing.Process(target = startfrontend)
		frontend.start()
	
	while not backend_server.returncode and not backend_main.returncode: time.sleep(0.001)
	backend_server.kill()
	backend_main.kill()
	if os.name != "nt" and os.geteuid() and args.port < 1024:
		frontend.kill()
	else:
		frontend.terminate()
	

