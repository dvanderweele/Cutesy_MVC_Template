from .router import process

def run(requests, responses, lock, off):
	while not(off.is_set()):
		with lock:
			if not(requests.empty()):
				item = requests.get_nowait()
				res = process(item)
				responses.put(res)
				requests.task_done()