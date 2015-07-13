import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-p", "--port", help="Port to host from", dest="port",
	default=80, type=int)
parser.add_argument("-n", "--regen-host", help="Regenerate host in config", dest="host",
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
parser.add_argument("-nu", "--no-update", help="Skip update", dest="skipupdate",
	action="store_const",const=True,default=False)
parser.add_argument("--new-password", help="Set a new password", dest="newpass",
	action="store", required=False)
parser.add_argument("--backend", help="Loads backend but not frontend", dest="load_backend",
	action="store_const",const=True,default=False)
parser.add_argument("--frontend", help="Loads frontend but not backend", dest="load_frontend",
	action="store_const",const=True,default=False)
parser.add_argument("--init-only", help="Doesn't load frontend or backend", dest="load_none",
	action="store_const",const=True,default=False)
parser.add_argument("--no-init", help="Doesn't run setup", dest="no_init",
	action="store_const",const=True,default=False)
parser.add_argument("--install-all", help="Don't ask for confirmation on install", dest="all",
	action="store_const",const=True,default=False)
parser.add_argument("--install-update", help="Don't ask for confirmation on update", dest="allupdate",
	action="store_const",const=True,default=False)
parser.add_argument("-h", "--help", help="Show this help message and exit", action="help")
args = parser.parse_args()
