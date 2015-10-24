#!/usr/bin/env python3
import os, sys
import subprocess, time
import json, multiprocessing

selfpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(selfpath) # Make sure we're in the right directory
# Allow importing from scripts
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 4):
	from wireutils import *

	printer.color_printing_config.color = ansi_colors.DARKRED
	printer.color_printing_config.name = "Error"
	version = sys.version.split(" ")[0]

	printer.color_print("""The version of Python is outdated.
		Found: {version}
		Required: 3.4+
		Please update to the correct version.""",
		version=version, 
		color=ansi_colors.DARKRED, strip=True)
	quit()

from parseargv import args
from util import *
printer = Printer(ansi_colors.GREEN, "LaserQueue")

def initFile(path, data=""):
	"""
	Make a file if it doesn't exist.
	"""
	if not os.path.exists(path):
		writeFile(path, data, printer)

def globalSyncCommand(cmd):
	"""
	Run a blocking command with python, independent of windows vs *nix.
	"""
	if os.name == "nt":
		return os.system("py -3 "+cmd)
	else:
		return os.system("python3 "+cmd)

class DummyProcess:
	def start(*args, **kwargs): pass
	def join(*args, **kwargs): pass

version_regex = re.compile(r"^(dev-)?\d+\.\d+\.\d+$")
dev_tag_regex = re.compile(r"^dev-")
def parse_version(version):
	return_words = []
	if version_regex.match(version):
		is_dev = dev_tag_regex.match(version)
		if is_dev: 
			version = dev_tag_regex.sub("", version)
			return_words.append("development")
		return_words.append("version{bold}")
		return_words.append(str(version))
	else:
		return_words.append("{bold}{red}an unknown version")

	return format("{words}{endc}", words=" ".join(return_words))


if __name__ == "__main__":
	version = Config(os.path.join("www","defaultconf.json"))["version"]
	printer.color_print("Running {version}.", version=parse_version(version))


	printer = Printer(ansi_colors.CYAN, "Setup")
	# Initialize all needed files
	initFile(os.path.join(selfpath, "scripts", "cache.json"), "[]")
	initFile(os.path.join(selfpath, "www", "config.json"), "{}")
	initFile(os.path.join(selfpath, "www", "infotext.md"), "To view our code or report an issue, go to [our GitHub repository](https://github.com/LaserQueue/LaserQueue).")
	initFile(os.path.join(selfpath, "www", "dist", "js", "plugins.js"))
	initFile(os.path.join(selfpath, "www", "dist", "css", "plugins.css"))

	# Do setup
	import scripts.initialize
	if not args.no_init:
		initcode = scripts.initialize.main()
		if initcode == 1: # If the update exit code was called
			os.chdir(selfpath)
			printer.color_print("Update successful! Restarting...\n\n\n")
			quit(int(globalSyncCommand("start.py "+" ".join(sys.argv[1:]))/256)) # Restart this script # Quit if something went wrong
	else:
		printer.color_print("Skipping initialization.", color=ansi_colors.YELLOW)

	backend_port = int(Config(os.path.join(os.path.pardir,"www","config.json"))["port"]) # Get the port to host the backend from

	# Based on the args, load frontend, backend, or neither.
	load_frontend = (args.load_frontend or (not args.load_frontend and not args.load_backend)) and not args.load_none
	load_backend = (args.load_backend or (not args.load_frontend and not args.load_backend)) and not args.load_none

	canServeToRestricted = os.name == "nt" or not os.geteuid()

	useSudo = ((load_backend and not canServeToRestricted and backend_port < 1024) or
						(load_frontend and not canServeToRestricted and args.port < 1024))

	if useSudo:
		passprompt = format("{whitespace}Password: ", whitespace=printer.colorconfig.whitespace())
		printer.color_print("""Root required on ports up to 1023, attempting to elevate permissions.
			                     (Edit config.json to change backend ports, 
			                     	use --port PORT to change frontend ports.)""", strip=True)
		os.chdir(selfpath)
		quit(int(os.system("sudo -p \""+passprompt+"\" python3 start.py "+" ".join(sys.argv[1:]))/256))


	try:
		os.chdir(os.path.join(selfpath, "www"))
		import scripts.main, scripts.http.server
		if load_backend:
			backThread = multiprocessing.Process(target=scripts.main.main)
		else:
			backThread = DummyProcess()
		if load_frontend:
			frontThread = multiprocessing.Process(target=scripts.http.server.main, args=(args.port,))	
		else:
			backThread = DummyProcess()
		backThread.start()
		frontThread.start()
		backThread.join()
		frontThread.join()
	except KeyboardInterrupt:
		# Print a cleanup message if exited manually
		print()
		printer = Printer(ansi_colors.RED, "Cleanup")
		printer.color_print("Keyboard interrupt received, exiting.")
