# UserController.py

from ..helpers.response import freshResponse
from ..models.User import User

class UserController:
	@staticmethod
	def page(request):
		u = User().orderBy('name').offset(request['payload']['page'] * request['payload']['size']).limit(request['payload']['size']).get()
		c = User().count()
		r = freshResponse(request)
		r['header']['request'] = request
		if c > 0:
			r['header']['code'] = 200
		else:
			r['header']['code'] = 404
		r['payload']  = {
			'users': u,
			'total': c
		}
		return r

    @staticmethod
    def index(request):
        u = User().allModels()
        r = freshResponse(request)
        r['header']['request'] = request
        if len(u) > 0:
            r['header']['code'] = 200
        else:
            r['header']['code'] = 404
        r['payload'] = {
			'users': u
		}
        return r

    @staticmethod
    def show(request):
        u = User().find(request['payload']['id'])
        r = freshResponse()
        r['header']['request'] = request
        if u != None:
            r['header']['code'] = 200
        else:
            r['header']['code'] = 404
        r['payload']['user'] = u
        return r

    @staticmethod
    def store(request):
        r = freshResponse()
        r['header']['request'] = request
        nu = request['payload']['user']
        u = User()
        r['header']['code'] = 201
        reqatts = [k for k in User.attributes.keys() if User.attributes[k][1]]
        for key in nu.keys():
            if (key == None and key in reqatts) or (not(isinstance(nu[key], User.attributes[key][0]))):
                r['header']['code'] = 400
                break
            else:
                u[key] = nu[key]
        if r['header']['code'] == 201:
            u.save()
        r['payload']['user'] = u
        return r
        
    @staticmethod
    def update(request):
        r = freshResponse()
        r['header']['request'] = request
        nu = request['payload']['user']
        u = User().find(request['payload']['id'])
        if u == None:
            r['header']['code'] = 404
            return r 
        else: 
            r['header']['code'] = 201
            reqatts = [k for k in User.attributes.keys() if User.attributes[k][1]]
            for key in nu.keys():
                if (key == None and key in reqatts) or (not(isinstance(nu[key], User.attributes[key][0]))):
                    r['header']['code'] = 400
                    break
                else:
                    u[key] = nu[key]
            if r['header']['code'] == 201:
                u.save()
            r['payload']['user'] = u
            return r

    @staticmethod
    def destroy(request):
        r = freshResponse()
        r['header']['request'] = request
        User().delete(r['payload']['id'])
        r['header']['code'] = 200
        return r
