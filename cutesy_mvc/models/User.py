from ..helpers.model import Model

class User(Model):
	table = 'user'
	relations = {
		'necks': {
			'type': 'hasMany',
			'model': 'Neck'
		},
		'waists': {
			'type': 'hasMany',
			'model': 'Waist'
		},
		'weights': {
			'type': 'hasMany',
			'model': 'Waist'
		}
	}
	attributes = {
		'name': (str, True),
		'height': (float, True),
		'sex': (str, True),
		'DOBDay': (int, True),
		'DOBMonth': (int, True),
		'DOBYear': (int, True),
		'metric': (int, True),
		'created_at': (float, False),
		'updated_at': (float, False)
	}
