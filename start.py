import os, sys
import http.server
from http.server import SimpleHTTPRequestHandler

import argparse
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-l", "--local", help="Run from localhost", dest="local",
	action="store_const",const=True,default=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-b", "--queue-backup", help="Backup queue and load from backup on start", dest="backup",
	action="store_const",const=True,default=False)
parser.add_argument("-h", "--help", help="Show help", dest="help",
	action="store_const",const=True,default=False)
parser.add_argument("-r", "--regen-config", help="Regenerate config.json", dest="regen",
	action="store_const",const=True,default=False)
parser.add_argument("-s", "--skip-install", help="Skip package installation", dest="skip",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
args = parser.parse_args()

selfpath = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
	os.system("cd "+selfpath+"; cd backend; python3 initialize.py "+" ".join(sys.argv[1:]))
	os.system("cd "+selfpath+"; ./startbackend.sh " + " ".join(sys.argv[1:]) + " &")
	os.chdir(os.path.join(os.getcwd(), "www"))
	http.server.test(HandlerClass=SimpleHTTPRequestHandler, port=args.port)
	os.system("pkill Python; pkill python3")
