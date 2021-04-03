from ..helpers.model import Model

class Neck(Model):
	table = 'neck'
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}
