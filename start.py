#!/usr/bin/env python3
import os, sys
import time, json
import multiprocessing, atexit

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

def init_file(path, data=""):
	"""
	Make a file if it doesn't exist.
	"""
	if not os.path.exists(path):
		write_file(path, data, printer)

def global_sync_system(cmd):
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
	def terminate(*args, **kwargs): pass

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


global backend_thread, frontend_thread
backend_thread, frontend_thread = DummyProcess(), DummyProcess()
def cleanup():
	global backend_thread, frontend_thread
	backend_thread.terminate()
	frontend_thread.terminate()

if __name__ == "__main__":
	atexit.register(cleanup)
	version = Config(os.path.join("www","defaultconf.json"))["version"]
	if not args.no_version_print: 
		printer.color_print("Running {version}.", version=parse_version(version))

	if args.regen != [] or "port" not in args.regen:
		try:
			backend_port = int(Config(os.path.join(selfpath,"www","config.json"))["port"]) # Get the port to host the backend from
		except:
			backend_port = int(Config(os.path.join("www","defaultconf.json"))["port"])
	else:
		backend_port = int(Config(os.path.join("www","defaultconf.json"))["port"])

	# Based on the args, load frontend, backend, or neither.
	load_frontend = (args.load_frontend or (not args.load_frontend and not args.load_backend)) and not args.load_none
	load_backend = (args.load_backend or (not args.load_frontend and not args.load_backend)) and not args.load_none

	can_serve_to_restricted = os.name == "nt" or not os.geteuid()

	useSudo = ((load_backend and not can_serve_to_restricted and backend_port < 1024) or
						(load_frontend and not can_serve_to_restricted and args.port < 1024))

	if useSudo:
		passprompt = "Password: "
		if not args.shh:
			passprompt = printer.colorconfig.whitespace()+passprompt
		printer.color_print("""Root required on ports up to 1023, attempting to elevate permissions.
			                     (Edit config.json to change backend ports, 
			                     	use --port PORT to change frontend ports.)""", strip=True)
		os.chdir(selfpath)
		quit(int(os.system("sudo -p \""+passprompt+"\" python3 start.py -V "+" ".join(sys.argv[1:]))/256)) # Restart this script with top permissions

	printer = Printer(ansi_colors.CYAN, "Setup")
	# Initialize all needed files
	init_file(os.path.join(selfpath, "scripts", "cache.json"), "[]")
	init_file(os.path.join(selfpath, "www", "config.json"), "{}")
	init_file(os.path.join(selfpath, "www", "infotext.md"), "To view our code or report an issue, go to [our GitHub repository](https://github.com/LaserQueue/LaserQueue).")
	init_file(os.path.join(selfpath, "www", "dist", "js", "plugins.js"))
	init_file(os.path.join(selfpath, "www", "dist", "css", "plugins.css"))

	# Do setup
	import initialize
	if not args.no_init:
		initcode = initialize.main()
		if initcode == 1: # If the update exit code was called
			os.chdir(selfpath)
			printer.color_print("Update successful! Restarting...\n\n\n")
			quit(int(global_synchronous_system("start.py "+" ".join(sys.argv[1:]))/256)) # Restart this script
	else:
		printer.color_print("Skipping initialization.", color=ansi_colors.YELLOW)

	try:
		os.chdir(os.path.join(selfpath, "www"))
		import scripts.backend, scripts.http.server
		if load_backend: backend_thread =   multiprocessing.Process(target=scripts.backend.main)
		if load_frontend: frontend_thread = multiprocessing.Process(target=scripts.http.server.main, args=(args.port,))
		backend_thread.start()
		frontend_thread.start()
		backend_thread.join()
		frontend_thread.join()
	except KeyboardInterrupt:
		# Print a cleanup message if exited manually
		print()
		printer = Printer(ansi_colors.RED, "Cleanup")
		printer.color_print("Keyboard interrupt received, exiting.")
