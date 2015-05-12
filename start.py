import os, sys
import http.server
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

if args.shh:
	newargs = " ".join([i for i in sys.argv[1:] if i != "-q"])
	os.system("cd "+selfpath+"; ./start.sh {0} >/dev/null".format(newargs))
	quit()

if os.name != "nt" and os.geteuid() and args.port == 80:
	print("Root required on port 80, enter your password to elevate permissions.")
	print("(Use --port PORT to change ports.)")
	os.system("cd "+selfpath+"; sudo -k ./start.sh "+" ".join(sys.argv[1:]))
	quit()

if __name__ == "__main__":
	os.system("cd "+selfpath+"; cd backend; python3 initialize.py "+" ".join(sys.argv[1:]))
	os.system("cd "+selfpath+"; ./startbackend.sh " + " ".join(sys.argv[1:]) + " &")
	os.chdir(os.path.join(os.getcwd(), "www"))
	http.server.test(HandlerClass=SimpleHTTPRequestHandler, port=args.port)
