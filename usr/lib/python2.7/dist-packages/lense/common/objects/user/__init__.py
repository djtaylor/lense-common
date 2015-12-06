from lense.common.objects.base import LenseBaseObject

class User_Objects(LenseBaseObject):
    def __init__(self):
        super(User_Objects, self).__init__('lense.common.objects.user.models', 'APIUser')