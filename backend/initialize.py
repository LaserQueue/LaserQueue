import json
import os.path

def copyconf():
	data = json.load(open(os.path.join("..", "www", "defaultconf.json")))
	json.dump(data, open(os.path.join("..", "www", "config.json"), "w"))

def main():
	copyconf()

if __name__ == "__main__":
	main()