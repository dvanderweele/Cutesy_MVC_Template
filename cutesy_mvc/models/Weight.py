from ..helpers.model import Model

class Weight(Model):
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}