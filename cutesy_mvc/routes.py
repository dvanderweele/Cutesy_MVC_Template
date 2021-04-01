# routes.py
from .controllers.NeckController import NeckController
from .controllers.UserController import UserController
from .controllers.WaistController import WaistController
from .controllers.WeightController import WeightController

definitions = (
    ('/neck/list', NeckController.index),
    ('/neck/show', NeckController.show),
    ('/neck/store', NeckController.store),
    ('/neck/update', NeckController.update),
    ('/neck/destroy', NeckController.destroy),
    ('/user/list', UserController.index),
    ('/user/show', UserController.show),
    ('/user/store', UserController.store),
    ('/user/update', UserController.update),
    ('/user/destroy', UserController.destroy),
    ('/waist/list', WaistController.index),
    ('/waist/show', WaistController.show),
    ('/waist/store', WaistController.store),
    ('/waist/update', WaistController.update),
    ('/waist/destroy', WaistController.destroy),
    ('/weight/list', WeightController.index),
    ('/weight/show', WeightController.show),
    ('/weight/store', WeightController.store),
    ('/weight/update', WeightController.update),
    ('/weight/destroy', WeightController.destroy),
)