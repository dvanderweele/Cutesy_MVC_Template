from ..helpers.client import Client 
import curses

class MenuItem: 
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.parent = props['parent']
		self.win = props['win']
		self.xmin = props['writable']['xmin']
		self.xmax = props['writable']['xmax']
		self.ymin = props['writable']['ymin']
		self.ymax = props['writable']['ymax']
		self.selected = props['selected']
		self.text = props['text']
	def __del__(self):
		self.client.shutdown()
		del self.client
	def receiver(self, response):
		pass
	def render(self):
		breadth = self.xmax - self.xmin
		padl = (breadth - len(self.text)) // 2
		if self.selected:
			self.win.addch(self.ymin, self.xmin + padl - 1, '~')
			self.win.addstr(self.ymin, self.xmin + padl, self.text, curses.A_UNDERLINE)
			self.win.addch(self.ymin, self.xmin + padl + len(self.text), '~')
		else:
			self.win.addstr(self.ymin, self.xmin + padl, self.text)
	def handleInput(self, key):
		if key == curses.KEY_ENTER:
			if self.text == 'Quit':
				self.parent.parent.exit()