from lense.common import LenseCommon

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

class BootstrapAnswers(object):
    """
    Class object for storing answers supplied by a JSON file.
    """
    def __init__(self, file):
        self.file = file
        
    def read(self):
        """
        Return the structure of any supplied answer file.
        """
        if self.file :
            try:
                answers = JSONObject()
                return answers.from_file(self.file)
            except Exception as e:
                LENSE.FEEDBACK.warn('Could not read answer file: {0}'.format(str(e)))
                return {}