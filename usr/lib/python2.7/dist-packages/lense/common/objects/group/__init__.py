from lense.common.objects.base import LenseBaseObject

class Group_Objects(LenseBaseObject):
    def __init__(self):
        super(Group_Objects, self).__init__('lense.common.objects.group.models', 'APIGroups')
        
    def add_member(self):
        return
    
    def remove_member(self):
        return
    
    def get_members(self):
        return