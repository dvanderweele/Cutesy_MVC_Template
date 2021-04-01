from ..helpers.client import Client 
from .menuItem import MenuItem
import curses

class Menu: 
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.parent = props['parent']
		self.win = props['win']
		self.xmin = props['writable']['xmin']
		self.xmax = props['writable']['xmax']
		self.ymin = props['writable']['ymin']
		self.ymax = props['writable']['ymax']
		self.children = [
			[
				MenuItem, 
				MenuItem({
					'parent': self, 
					'win': self.win, 
					'writable': {
						'xmin': self.xmin,
						'xmax': 11,
						'ymin': 1,
						'ymax': 1,
					},
					'selected': False,
					'text': 'New User'
				})
			],
			[
				MenuItem, 
				MenuItem({
					'parent': self, 
					'win': self.win, 
					'writable': {
						'xmin': 12,
						'xmax': 23,
						'ymin': 1,
						'ymax': 1,
					},
					'selected': True,
					'text': 'Users'
				}),
			],
			[
				MenuItem, 
				MenuItem({
					'parent': self, 
					'win': self.win, 
					'writable': {
						'xmin': 24,
						'xmax': self.xmax,
						'ymin': 1,
						'ymax': 1,
					},
					'selected': False,
					'text': 'Quit'
				})
			]
		]
	def __del__(self):
		self.client.shutdown()
		del self.client
	def receiver(self, response):
		pass
	def render(self):
		for c in self.children:
			c[1].render() 
	def handleInput(self, key):
		self.win.addstr(3,3,f'{key}')
		if key == curses.KEY_LEFT:
			for idx in range(len(self.children)):
				if self.children[idx].selected and idx > 0:
					self.children[idx].selected = False
					self.children[idx - 1].selected = True
					break
		elif key == curses.KEY_RIGHT:
			for idx in range(len(self.children)):
				if self.children[idx].selected and idx < len(self.children) - 1:
					self.children[idx].selected = False
					self.children[idx + 1].selected = True
					break
		elif key == curses.KEY_ENTER:
			for idx in range(len(self.children)):
				if self.children[idx].selected:
					self.children[idx].handleInput(key)
					break 