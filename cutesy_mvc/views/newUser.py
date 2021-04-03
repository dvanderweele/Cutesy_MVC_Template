from ..helpers.client import Client

class NewUser:
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.parent = props['parent']
	def receiver(self, response):
		pass
	def render(self):
		pass
	def handleInput(self, key):
		if key == 'w':
			self.parent.topOut()
