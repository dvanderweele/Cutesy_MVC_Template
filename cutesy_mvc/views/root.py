from ..helpers.client import Client 
from .menu import Menu
from .tab import Tab
import curses

class Root: 
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.win = props['win']
		self.exit = props['off']
		self.writable = props['writable']
		self.children = [
			[
				Menu, 
				Menu({
					'parent': self, 
					'win': self.win, 
					'writable': {
						'xmin': 1,
						'xmax': 34,
						'ymin': 1,
						'ymax': 1,
					}
				})
			], 
			[
				Tab,
				Tab({
					'parent': self,
					'win':self.win,
					'writable': {
						'xmin': 1,
						'xmax': 34,
						'ymin': 2,
						'ymax': 9
					}
				})
			]
		]
		self.activeChildIdx = 0
	def __del__(self):
		self.client.shutdown()
		del self.client
	def receiver(self, response):
		pass
	def render(self):
		for c in self.children:
			c[1].render() 
	def handleInput(self):
		self.win.nodelay(True)
		key = self.win.getch()
		if key != -1:
			if self.activeChildIdx == 0:
				self.children[0][1].handleInput(key)
			else:
				self.children[1][1].handleInput(key)
		curses.flushinp()
	def handleResponses(self):
		self.client.receive()