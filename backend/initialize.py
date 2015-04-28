import json
import os.path
import socket

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	data["host"] = socket.gethostbyname(socket.getfqdn())+":8765"
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

def main():
	copyconf()

if __name__ == "__main__":
	main()