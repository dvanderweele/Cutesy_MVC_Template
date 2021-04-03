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
						'xmax': self.writable['xmax'],
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
						'xmax': self.writable['xmax'],
						'ymin': 3,
						'ymax': self.writable['ymax'] - 1
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
		for ch in range(self.writable['xmin'], self.writable['xmax']):
			self.win.addch(2, ch, '—')
	def refocus(self, direction):
		if direction  == 'down':
			self.activeChildIdx = 1
			self.children[1][1].focus()
		elif direction == 'up':
			self.activeChildIdx = 0
			self.children[0][1].focus()
	def handleInput(self):
		try:
			key = self.win.getch()
			if key != -1:
				key = curses.keyname(key).decode('ascii')
				if self.activeChildIdx == 0:
					self.children[0][1].handleInput(key)
				else:
					self.children[1][1].handleInput(key)
			curses.flushinp()
		except:
			pass
	def handleResponses(self):
		self.client.receive()

