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
						'xmax': self.xmax // 3,
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
						'xmin': self.xmax // 3 + 1,
						'xmax': (self.xmax // 3) + (self.xmax // 3),
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
						'xmin': 2 * (self.xmax // 3) + 1,
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
		for ch in range(self.xmin, self.xmax):
			self.win.addch(self.ymin, ch, ' ')
		for c in self.children:
			c[1].render() 
	def handleInput(self, key):
		if key == 'a':
			for idx in range(len(self.children)):
				if self.children[idx][1].selected and idx > 0:
					self.children[idx][1].selected = False
					self.children[idx - 1][1].selected = True
					break
		elif key == 'd':
			for idx in range(len(self.children)):
				if self.children[idx][1].selected and idx < len(self.children) - 1:
					self.children[idx][1].selected = False
					self.children[idx + 1][1].selected = True
					break
		elif key == ' ':
			for idx in range(len(self.children)):
				if self.children[idx][1].selected:
					self.children[idx][1].handleInput(key)
					break
		elif key == 's':
			for c in self.children:
				 c[1].selected = False
			self.parent.refocus('down')
	def focus(self):
		self.children[0][1].selected = True
