"""
The ActionFramework for LaserQueue plugins.
"""

def _comparetypes(obj, expected):
	"""
	Compare types, allowing exceptions.
	"""
	if expected is any_type:
		return True
	elif expected is any_number:
		if type(obj) is int or type(obj) is float:
			return True
	return type(obj) is expected

# Type exceptions
class any_type: pass 
class any_number: pass 

class SocketCommand:
	"""
	A class used to define a socket command usable by `runSocketCommand`.
	"""
	def __init__(self, actionname, method, arglist):
		self.name = actionname
		self.method = method
		self.args = arglist
	def __str__(self):
		return self.name
	def run(self, **kwargs):
		args = kwargs["args"]
		# Check that each argument is correct
		for i in self.args:
			if i not in args:
				return "Expected '{}' argument, but didn't find it.".format(i)
			if not _comparetypes(args[i], self.args[i]):
				return "Expected '{}' argument to be an instance of '{}', but found an instance of '{}'.".format(
					i, self.args[i].__name__, type(args[i]).__name__)
		# Run the command if all is in order
		return self.method(**kwargs)