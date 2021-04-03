from ..helpers.model import Model

class Weight(Model):
	table = 'weight'
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}
