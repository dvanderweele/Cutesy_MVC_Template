from ..helpers.model import Model

class Neck(Model):
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}