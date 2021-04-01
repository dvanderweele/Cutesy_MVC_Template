from ..helpers.model import Model

class Waist(Model):
	relations = {
		'user': {
			'type': 'belongsTo',
			'model': 'User'
		}
	}