from queue import Queue 
from threading import Thread, Lock, Event
from .server import run  
from uuid import uuid4

class Client: 
	off = Event()
	requests = Queue()
	responses = Queue()
	lock = Lock()
	server = Thread(target=run, args=(requests, responses, lock, off))
	server.start()
	clients = {}
	def __init__(self, receiver):
		self.id = uuid4()
		self.receiver = receiver
		self.__class__.clients[self.id] = self
	def __del__(self):
		self.__class__.clients.pop(self.id)
	def valid(self, identifier):
		if identifier in self.__class__.clients.keys(): 
			return True 
		else: 
			return False
	def shutdown(self):
		self.__class__.off.set()
		self.__class__.server.join()
	def freshRequest(self, route = '/'):
		return {
			'header': {
				'type': 'request',
				'route': route,
				'requester': self.id 
			},
			'payload': None 
		}
	def send(self, request):
		if not(self.__class__.off.is_set()):
			self.__class__.requests.put(request)
	def receive(self):
		with self.__class__.lock:
			if not(self.__class__.responses.empty()):
				item = self.__class__.responses.get_nowait()
				self.__class__.responses.task_done()
				if self.valid(item['header']['requester']):
					self.__class__.clients[item['header']['requester']].receiver(item)
		return None 