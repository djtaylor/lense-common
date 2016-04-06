from json import loads
from feedback import Feedback

# Lense Libraries
from lense.common.vars import SHARE

class BootstrapAnswers(object):
    """
    Class object for storing answers supplied by a JSON file.
    """
    @classmethod
    def _read(cls, file):
        """
        Private class method for reading an answer file.
        
        :param file: Path to the answers file
        :type  file: str
        :rtype: dict
        """
        answers = {}
        if file:
            try:
                answers = loads(open(file, 'r').read())
                BOOTSTRAP.FEEDBACK.success('Loaded answers file: {0}'.format(file))
            except Exception as e:
                BOOTSTRAP.FEEDBACK.warn('Could not read answer file: {0}'.format(str(e)))
        return answers
    
    @classmethod
    def get(cls, file=BOOTSTRAP.ARGS.get('answers', None), default='{0}/defaults/answers.json'.format(SHARE.BOOTSTRAP), mapper=None):
        """
        Return the structure of any supplied answer file.
        
        :param    file: The path to the answers file
        :type     file: str
        :param default: The default answers file
        :type  default: str
        :param  mapper: Method for loading a mapper object and passing method answers
        :type   mapper: callable
        :rtype: dict
        """
        user_answers = cls._read(file)
        answers      = cls._read(default)
         
        # Merge answer files
        def merge_dict(d1, d2):
            for k,v2 in d2.items():
                v1 = d1.get(k)
                if (isinstance(v1, Mapping) and 
                    isinstance(v2, Mapping)):
                    merge_dict(v1, v2)
                else:
                    d1[k] = v2
            
        # If user defined file
        if user_answers:
            merge_dict(answers, user_answers)
            
            # Initialize
            if 'init' in answers:
                for k,m in mapper.iteritems():
                    m(answers['init'][k])
            del answers['init']
            return answers
        return {}