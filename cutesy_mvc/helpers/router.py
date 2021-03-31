from ..routes import definitions 

def process(request = {'header':{'type':'request','route':'/', 'requester':None},'payload': None}):
	for r in definitions:
		if r[0] == request['header']['route']:
			return r[1](request)
	return {
		'header': {
			'type': 'response',
			'request': request
		},
		'payload': None
	}
		