import os
def main():
  if os.name == "nt": 
  	import mainwin
  	mainwin.main()
  else:           
  	import mainux     
  	mainux.main()
if __name__ == "__main__":    main()