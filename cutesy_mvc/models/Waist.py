from ..helpers.model import Model

class Waist(Model):
	table = 'waist'
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}
