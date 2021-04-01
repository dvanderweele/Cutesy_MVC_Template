from ..helpers.client import Client 

class Tab: 
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.win = props['win']
		self.writable = props['writable']
		self.children = []
	def __del__(self):
		self.client.shutdown()
		del self.client
	def receiver(self, response):
		pass
	def render(self):
		pass
	def handleInput(self, key):
		pass