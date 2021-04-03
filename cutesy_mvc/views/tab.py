from ..helpers.client import Client 
from .newUser import NewUser
from .users import Users

class Tab: 
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.win = props['win']
		self.writable = props['writable']
		self.parent = props['parent']
		self.children = [
			[
				NewUser,
				NewUser({
					'parent': self,
					'win': self.win,
					'xmin': self.writable['xmin'],
					'xmax': self.writable['xmax'],
					'ymin': self.writable['ymin'],
					'ymax': self.writable['ymax']
				})
			],
			[
				Users,
				Users({
					'parent': self,
					'win': self.win,
					'xmin': self.writable['xmin'],
					'xmax': self.writable['xmax'],
					'ymin': self.writable['ymin'],
					'ymax': self.writable['ymax']
				})
			]
		]
		self.renderChildIdx = 1
	def __del__(self):
		self.client.shutdown()
		del self.client
	def receiver(self, response):
		pass
	def render(self):
		for xc in range(self.writable['xmin'], self.writable['xmax']):
			for yc in range(self.writable['ymin'], self.writable['ymax'] + 1):
				self.win.addch(yc, xc, ' ')
		self.children[self.renderChildIdx][1].render()
	def topOut(self):
		self.parent.refocus('up')
	def handleInput(self, key):
		self.children[self.renderChildIdx][1].handleInput(key)
	def switchChildren(self, target):
		if target  == 'newUser':
			self.renderChildIdx = 0
		elif target == 'users':
			self.renderChildIdx = 1
	def focus(self):
		pass
