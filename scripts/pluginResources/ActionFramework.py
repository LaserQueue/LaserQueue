import sys, os
sys.path.append(
	os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from jsonhandler import SocketCommand, any_type, any_number