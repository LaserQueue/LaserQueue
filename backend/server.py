import os, serverux, serverwin
def main():
  if os.name == "nt": 
  	import serverwin
  	serverwin.main()
  else:                
  	import serverux
  	serverux.main()
if __name__ == "__main__":      main()