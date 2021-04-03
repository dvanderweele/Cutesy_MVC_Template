from ..helpers.client import Client
import time
import curses

class Users:
	def __init__(self, props = {}):
		self.client = Client(self.receiver)
		self.parent = props['parent']
		self.win = props['win']
		self.xmin = props['xmin']
		self.xmax = props['xmax']
		self.ymin = props['ymin']
		self.ymax = props['ymax']
		self.users = []
		self.page = 1
		r = self.client.freshRequest()
		r['header']['route'] = '/user/page'
		r['payload'] = {
			'page' = self.page,
			'size' = self.ymax - self.ymin - 2
		}
		self.client.send(r)
	def receiver(self, response):
		self.users = response['payload']['users']
	def render(self):
		sx = (self.xmax - self.xmin) // 6 - 2
		self.win.addstr(self.ymin, sx, 'NAME', curses.A_UNDERLINE)
		sx = (self.xmax - self.xmin) // 2 - 2
		self.win.addstr(self.ymin, sx, 'DOB', curses.A_UNDERLINE)
		sx = (self.xmax - self.xmin) // 6 * 5 - 2
		self.win.addstr(self.ymin, sx, 'ID', curses.A_UNDERLINE)
		if len(self.users) < 1:
			self.win.addstr(self.ymin + 1, sx + 2, 'None.')
		else: 
			for i in range(len(self.users)):				self.win.addstr(self.ymin + i + 1, self.xmin + 1, f'{self.users[i]["name"]} ~ {self.users[i]["DOBMonth"]}/{self.users[i]["DOBDay"]}/{self.users[i]["DOBYear"]} ~ {self.users[i]["id"]}')

	def handleInput(self, key):
		if key == 'w':
			self.parent.topOut()
