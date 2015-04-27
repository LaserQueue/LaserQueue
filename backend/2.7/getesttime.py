import autoit
import re


worktime = re.compile(r"\d{2}:\d{2}:\d{2}", 0)

maintitle = "Laser system 5.3[Jinan King Rabbit Technology Development Co.,Ltd. www.rabbitlaser.com]"
calctitle = "Laser output"
filetitle = "Stand-alone file manager"
downloadtitle = "Donwload [{0}%]"

def gettime():
	# Clear all previous calculate windows
	prfin = autoit.win_exists("[Title:"+calctitle+"]")
	while prfin:
		autoit.control_click("[Title:"+calctitle+"]", "Button1", clicks=2)
		prfin = autoit.win_exists("[Title:"+calctitle+"]")

	# Create updated calculate window
	autoit.control_click("[Title:"+maintitle+"]", "ToolbarWindow321", x=185, y=7)
	prfin = autoit.win_exists("[Title:"+calctitle+"]")
	while not prfin:
		prfin = autoit.win_exists("[Title:"+calctitle+"]")

	# Read calculate window and get hms data
	unparsed = autoit.win_get_text("[Title:"+calctitle+"]")
	while not unparsed:
		unparsed = autoit.win_get_text("[Title:"+calctitle+"]")
	regfind = worktime.search(unparsed).group()
	(h, m, s) = regfind.split(':')

	# Close calculate window
	autoit.control_click("[Title:"+calctitle+"]", "Button1", clicks=2)
	
	# Return seconds
	return int(h)*3600 + int(m)*60 + int(s)


def ondownloadpressed():
	# Wait for download window to close
	dlfin = autoit.win_exists("[Title:"+filetitle+"]")
	while dlfin:
		dlfin = autoit.win_exists("[Title:"+filetitle+"]")

	# Get calculated time
	return gettime()

def _dlexists():
	for i in xrange(1, 100):
		if autoit.win_exists("[Title"+downloadtitle.format(i)+"]"):
			return True
	return False


