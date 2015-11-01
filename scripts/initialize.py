import pip
import gzip, tarfile
import getpass, hashlib

import plugins
from parseargv import args

# Set up pretty printing
from util import *
printer = Printer(ansi_colors.CYAN, "Setup")

file_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(file_path) # Make sure we're in the correct directory

# All the config paths
plugin_js_path = os.path.join(os.path.pardir, "www", "dist", "js", "plugins.js")
plugin_css_path = os.path.join(os.path.pardir, "www", "dist", "css", "plugins.css")
config_path = os.path.join(os.path.pardir, "www", "config.json")
user_config_path = os.path.join(os.path.pardir, "www", "userconf.json")
default_config_path = os.path.join(os.path.pardir, "www", "defaultconf.json")

# Utility function to test for internet connection.
connected_to_internet = lambda: bool(get_IPs(test=True))
# Open/save to the config file
open_config = lambda: json.load(open(config_path))
save_config = lambda data: write_file(config_path, json.dumps(data, indent=2, sort_keys=True))


version_regex = re.compile(r"^(dev-)?\d+\.\d+\.\d+$")
dev_tag_regex = re.compile(r"^dev-")
def check_version_numbers(current, master):
	if version_regex.match(current):
		version_number = convert_version_number(current)
		if version_number < 0: return False
	else:
		printer.color_print("The current version lacks a valid version tag.", color=ansi_colors.RED)
		return False

	if version_regex.match(master):
		master_version_number = convert_version_number(master)
		if version_number < 0: return False
	else:
		printer.color_print("The master version lacks a valid version tag.", color=ansi_colors.RED)
		return False

	return version_number > master_version_number

def convert_version_number(version):
	version_number = 0.0
	is_dev = dev_tag_regex.match(version)
	if is_dev:
		version_number = -1.0
	else:
		float_index = 0
		for i in version:
			if i.isdigit():
				float_index += 1
				version_number += int(i) * 10 ** -float_index
	return version_number


def update_config():
	"""
	Make sure the config has the required data in it.
	If args.regen, it will pretend as though the original config was empty.
	"""
	if os.path.exists(config_path) and args.regen != []:
		current_data = open_config()

		if args.regen: # Regenerate everything after -r
			for key in args.regen:
				if key in current_data:
					del current_data[key]

		if "host" not in current_data or not current_data["host"]:
			current_data["host"] = get_IPs()[0]
		if "version" in current_data: # Version should always be latest
			del current_data["version"]
	else:
		current_data = {"host": get_IPs()[0]}
	data = json.load(open(default_config_path))
	if os.path.exists(user_config_path):
		user_data = json.load(open(user_config_path))
	else:
		user_data = {}
	data = dict(dict(data, **user_data), **current_data)
	save_config(data)


def get_IPs(test=False):
	"""
	Get the IPs this device controls.
	"""
	from netifaces import interfaces, ifaddresses, AF_INET
	ips = []
	for interface in interfaces():
		addresses = [address['addr'] for address in ifaddresses(interface).get(AF_INET, [{"addr":"not found"}])]
		if "not found" not in addresses and "127.0.0.1" not in addresses:
			ips += addresses
	if not ips and not test:
		ips.append("localhost")
		printer.color_print("WARNING: No internet connection. Using -l behavior.", color=ansi_colors.YELLOW)
	return ips

def concat_plugins():
	js = plugins.get_plugin_filetype(".min.js")
	plugin_js = "\n".join(js)
	write_file(plugin_js_path, plugin_js, printer)

	css = plugins.get_plugin_filetype(".min.css")
	plugin_css = "\n".join(css)
	write_file(plugin_css_path, plugin_css, printer)


PACKAGES = [
	"websockets",
	"netifaces",
	"GitPython"
]
def fetch_dependencies():
	"""
	Go through PACKAGES and install everything missing.
	"""
	if args.skip:
		printer.color_print("Skipping package install.", color=ansi_colors.YELLOW)
		return

	# Gets a list of installed packages
	installed_packages = [str(i).split(" ")[0] for i in pip.get_installed_distributions()]

	# Check if anything's been installed
	installed = False

	for package in PACKAGES:
		if package in installed_packages:
			continue # Don't do anything if the package is installed
		if "netifaces" in installed_packages and not connected_to_internet():
			printer.color_print("No internet connection. Skipping package install.", color=ansi_colors.YELLOW)
			return
		installed = True

		# Ask if they want to install this dependency
		confirm = ("y" if args.all else "")
		while confirm not in ["y", "n"]:
			confirm = printer.color_input("Install dependency {dep}? (y/n) ", dep=package).lower().strip()

		if confirm == "n": # If the person chose not to install the dependency
			printer.color_print("WARNING: Program may not run without this library.", color=ansi_colors.YELLOW)
			continue # Don't do anything
		if pip.main(["install", package]) and os.name != "nt": # If the install fails and this is a *nix system:
			# Ask again, with minor error colors
			confirm = ("y" if args.all else "")
			while confirm not in ["y", "n"]:
				confirm = printer.color_input("Install failed, try again with elevated permissions? (y/n) ", color=ansi_colors.RED).lower().strip()

			if confirm == "n": # If the person chose not to install the dependency
				printer.color_print("WARNING: Program may not run without this library.", color=ansi_colors.YELLOW)
				continue # Don't do anything
			if not os.system("sudo pip3 install "+package): # Try again with root permissions
				installed_packages.append(package) # If it succeeds, add it to the installed packages
		else:
			installed_packages.append(package) # If it succeeds at first, add it to the installed packages
	if installed:
		for package in PACKAGES:
			if package not in installed_packages:
				printer.color_print("Failed to install dependency {dep}.", color=ansi_colors.DARKRED, dep=package)
				installed = False # If not everything's been installed, don't say it was successful

	if installed:
		printer.color_print("Sucessfully installed all dependencies!")

def make_tarfile(output_filename, source_dir):
	"""
	Make a tarball of the chosen directory to the chosen filename.
	"""
	with tarfile.open(output_filename, "w:gz") as tar:
			tar.add(source_dir, arcname=os.path.basename(source_dir))

def update():
	"""
	Try to update LaserQueue to the latest version.
	"""
	if args.skip_update:
		printer.color_print("Skipping updating.", color=ansi_colors.YELLOW)
		return

	if not connected_to_internet():
		printer.color_print("No internet connection. Skipping update.", color=ansi_colors.YELLOW)
		return

	import git
	config = json.load(open(default_config_path))

	try:
		config_page = urllib.request.urlopen(config["updateTarget"]).read().decode('utf8')
		master_config = json.loads(config_page) # Get the current up-to-date config

		if "version" in master_config and check_version_numbers(config["version"], master_config["version"]): # If the remote version is greater than the one here

			printer.color_print("New update found: Version {ver}.", ver=master_config["version"])

			prefix = format("{path}-", path=os.path.basename(os.path.abspath(os.path.pardir))) # Prefix for new or old versions
			update_directory = os.path.join(os.path.pardir,os.path.pardir,prefix+master_config["version"]) # Directory if fetch updating
			backup_file = os.path.join(os.path.pardir, os.path.pardir, prefix+config["version"]+".tar.gz") # Backup file if overwrite updating

			prompt = format("""Do you want to get version {current} to {latest}?
				                 The fetch option will update into {update_directory}.
				                 The overwrite option will backup to {backup_file}, and fetch master.
				                 (fetch / overwrite / cancel) """,
				                 current=config["version"],
				                 lastest=master_config["version"],
				                 update_directory=os.path.abspath(update_directory),
				                 backup_file=os.path.abspath(backup_file))

			# Check what the user wants to do
			confirm = ("overwrite" if args.all_update else "")
			while confirm not in ["fetch", "overwrite", "cancel"]:
				confirm = printer.color_input(prompt, strip=True).lower().strip()

			# If they want to fetch the new repository
			if confirm == "fetch":
				git.Repo.clone_from(config["updateRepo"], update_directory) # Get the new repository

				# Inform them about it
				printer.color_print("""
				            New version located in:
				            {update_directory}
				            Run the following:
				            {start_script}
				            to use the new version.""",
				            	update_directory=os.path.abspath(update_directory),
				            	start_script=os.path.abspath(os.path.join(update_directory, "start.py")),
				            	strip=True)

			# If they want to overwrite their repository
			elif confirm == "overwrite":
				# Get a git repo object for the folder
				if not os.path.exists(os.path.join(os.path.pardir, ".git")):
					repo = git.Repo.init(os.path.pardir)
				else:
					repo = git.Repo(os.path.pardir)

				# If the repo doesn't have a connection to the remote, make one
				if "origin" not in [i.name for i in repo.remotes]:
					origin = repo.create_remote("origin", config["updateRepo"])
					origin.fetch()

				# Make a backup file
				try:
					tar_archive_file = open(backup_file, 'wb')
					repo.archive(tar_archive_file)
					gzip.GzipFile(fileobj=tar_archive_file, mode='wb')
				except:
					make_tarfile(backup_file, os.path.pardir)

				# Reset the repository
				repo.git.fetch("--all")
				repo.git.reset("--hard", "origin/master")
				save_config(config)
				return "restart" # Tells the start script to restart
	except Exception as e: # Error reporting
		printer.color_print(format_traceback(e, "Error updating:"), color=ansi_colors.DARKRED)



def update_password():
	"""
	Change the password if --new-password used.
	"""
	if args.newpass or not os.path.exists("hashpassword"):
		# Get password
		if args.newpass:
			new_password = printer.color_input("New password: ", func=getpass.getpass)
		else:
			new_password = printer.color_input("Please set the admin login password: ", func=getpass.getpass)

		# Hash the new password
		hash_object = hashlib.sha256(new_password.encode()).hexdigest()
		hashed_final = hashlib.sha256(hash_object.encode()).hexdigest()

		if os.path.exists("hashpassword"):
			# Read the old password
			old_file = open("hashpassword")
			old_data = old_file.read()
			old_file.close()

			# Make sure we don't overwrite the old password with itself
			if old_data == hashed_final:
				printer.color_print("Passwords identical. No action taken.")
				return

		try:
			# Write the password to the file
			write_file("hashpassword", hashed_final, printer)
			printer.color_print("Password changed to {starredpass}.", starredpass="*"*len(hashed_final))
		except Exception as e: # Error reporting
			printer.color_print(format_traceback(e, "Error changing password:"), color=ansi_colors.DARKRED)


def update_host():
	"""
	Make sure the config's "host" flag is correct
	"""
	data = open_config()
	# Change the host to localhost if -l was used (overriding -n)
	if args.local:
		data["host"] = "localhost"
	# Regenerate the host if -n was used, or if it doesn't exist
	elif args.host or "host" not in data and args.regen != []:
		data["host"] = get_IPs()[0]
	# Otherwise, reset the host from localhost (ignored by definition if -n is used)
	else:
		if "host" in data and data["host"] == "localhost":
			# Confirm they want to reset the host
			confirm = ""
			while confirm not in ["y", "n"]:
				confirm = printer.color_input("""Last time you ran this program, it was in local mode.
				                                 Do you want to regenerate the host? (y/n) """, strip=True).lower().strip()
			# Reset the host if they say yes
			if confirm == "y":
				data["host"] = get_IPs()[0]
	save_config(data)



def main():
	"""
	Run all subroutines for initialization.
	"""
	printer.color_print("Beginning initialization.")
	retcode = 0
	try: fetch_dependencies()
	except KeyboardInterrupt: print()
	try: update_config()
	except KeyboardInterrupt: print()
	try: update_password()	
	except KeyboardInterrupt: print()
	try: update_host()
	except KeyboardInterrupt: print()
	try:
		if update() == "restart":
			retcode += 0x1
	except KeyboardInterrupt: print()
	try: concat_plugins()
	except KeyboardInterrupt: print()
				
	printer.color_print("Initialization complete.")
	return retcode

if __name__ == "__main__":
	main()
