def freshResponse(request, includeRequest = False):
	return {
		'header': {
			'type': 'response',
			'request': request if includeRequest else None,
			'requester': request['header']['requester']
		},
		'payload': None
	}