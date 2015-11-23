class JSONException(Exception):
    """
    Custom exceptions when encountering JSON object errors.
    """
    pass

class InvalidProjectID(Exception):
    """
    Wrapper class for handling invalid project names.
    """
    def __init__(self, project):
        super(InvalidProjectID, self).__init__('Invalid project ID: {0}'.format(project))