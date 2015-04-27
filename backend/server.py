import os, serverux, serverwin
def main():
	if os.name is "nt": serverwin.main()
	else:                serverux.main()
if __name__ == "__main__":      main()