import os, mainux, mainwin
def main():
  if os.name is "nt": mainwin.main()
  else:                mainux.main()
if __name__ == "__main__":    main()