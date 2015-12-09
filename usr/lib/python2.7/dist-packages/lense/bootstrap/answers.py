from feedback import Feedback

class BootstrapAnswers(object):
    """
    Class object for storing answers supplied by a JSON file.
    """
    def __init__(self, file):
        self.file = file
        self.fb   = Feedback()
        
    def read(self):
        """
        Return the structure of any supplied answer file.
        """
        answers = {}
        if self.file :
            try:
                answers = BOOTSTRAP.JSON.from_file(self.file)
                self.fb.success('Loaded answers file: {0}'.format(self.file))
            except Exception as e:
                self.fb.warn('Could not read answer file: {0}'.format(str(e)))
        return answers