from sys import exit
from pwd import getpwnam
from os import path, makedirs, system
from subprocess import Popen, PIPE

# Lense Libraries
from lense.common import LenseCommon
from lense.common.config import LenseConfigEditor
from lense.common.vars import WSGI_CONFIG, PROJECTS, CONFIG

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

class BootstrapCommon(object):
    """
    Common class object for bootstrap handlers.
    """
    def __init__(self, project=None):
        self.project = project
        self.ATTRS   = getattr(PROJECTS, project.upper())

    def die(self, msg, log=True):
        """
        Quit the program
        """
        
        # Log the message unless explicitly specified otherwise
        if log:
            LENSE.LOG.error(msg)
            
        # Show the error and quit
        LENSE.FEEDBACK.error(msg)
        exit(1)

    def group_add_user(self, user):
        """
        Add a user account to the lense system group.
        """
        try:
            pwd.getpwnam(user)
            
            # Create the user account
            proc = Popen(['/usr/sbin/usermod', '-a', '-G', 'lense', user], stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            
            # Make sure the command returned successfully
            if not proc.returncode == 0:
                self.die('Failed to add user "{0}" to lense group: {1}'.format(user, str(err)))
            LENSE.FEEDBACK.success('Added user "{0}" to lense group'.format(user))
        except Exception as e:
            self.die('Could not add user "{0}" to lense group: {1}'.format(user, str(e)))        

    def create_system_user(self):
        """
        Create the lense system account.
        """
        try:
            pwd.getpwnam('lense')
            return LENSE.FEEDBACK.info('System account "lense" already exists, skipping...')
        except KeyError:
            pass
            
        # Create the user account
        proc = Popen(['/usr/sbin/useradd', '-M', '-s', '/usr/sbin/nologin', 'lense'], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        
        # Make sure the command returned successfully
        if not proc.returncode == 0:
            self.die('Failed to create system account: {0}'.format(str(err)))
        LENSE.FEEDBACK.success('Created system account "lense"')
            
    def get_file_path(self, file):
        """
        Return the parent directory of a file.
        """
        return path.dirname(file)

    def deploy_apache(self, project):
        """
        Deploy Apache configuration files.
        """
        
        # Project configurations
        _project_config = {
            'engine': WSGI_CONFIG.ENGINE[0],
            'portal': WSGI_CONFIG.PORTAL[0]
        }
    
        # Enable the site configuration
        proc = Popen(['a2ensite', _project_config[project]], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        
        # Make sure the command returned successfully
        if not proc.returncode == 0:
            self.die('Failed to enable virtual host: {0}'.format(str(err)))
        LENSE.FEEDBACK.success('Enabled virtual host configuration for Lense API {0}'.format(project))

    def mkdirs(self, dirs):
        """
        Make required directories.
        """
    
        # Create the log and run directories
        for d in dirs:
            if not path.isdir(d):
                makedirs(d)
                LENSE.FEEDBACK.info('Created directory "{0}"'.format(d))
            else:
                LENSE.FEEDBACK.info('Directory "{0}" already exists, skipping...'.format(d))

    def chown_logs(self, project, user='root', group='root'):
        """
        Set permissions on log files.
        """
        log_file = '/var/log/lense/{0}.log'.format(project)
        
        # Make sure the log file exists
        if not path.isfile(log_file):
            open(log_file, 'a').close()
        
        # Change log file permissions
        proc = Popen(['chown', '-R', '{0}:{1}'.format(user,group), log_file], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        
        # Make sure the command returned successfully
        if not proc.returncode == 0:
            self.die('Failed to set log permissions: {0}'.format(str(err)))
        LENSE.FEEDBACK.success('Set log permissions for Lense project: {0}'.format(project))

    def _get_password(self, prompt, min_length=8):
        _pass = getpass(prompt)
        
        # Make sure the password is long enough
        if not len(_pass) >= min_length:
            LENSE.FEEDBACK.error('Password cannot be empty and must be at least {0} characters long'.format(str(min_length)))
            return self._get_password(prompt, min_length)
            
        # Confirm the password
        _pass_confirm = getpass('Please confirm the password: ')
            
        # Make sure the passwords match
        if not _pass == _pass_confirm:
            LENSE.FEEDBACK.error('Passwords do not match, try again')
            return self._get_password(prompt, min_length)
        return _pass

    def _get_input(self, prompt, default=None):
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            LENSE.FEEDBACK.error('Must provide a value')
            return self._get_input(prompt, default)
        return _input
    
    def read_input(self, answers={}):
        """
        Read any required user input prompts
        """
        
        # Process each configuration section
        for section, obj in self.params.input.prompt.iteritems():
            print obj['label']
            print '-' * 20
        
            # Process each section input
            for key, attrs in obj['attrs'].iteritems():
                
                # If an answer already defined
                if key in answers:
                    LENSE.FEEDBACK.info('Value for {0} found in answer file'.format(key))
                    val = answers[key]
                    
                else:
                
                    # Regular string input
                    if attrs['type'] == 'str':
                        val = self._get_input(attrs['prompt'], attrs['default'])
                        
                    # Password input
                    if attrs['type'] == 'pass':
                        val = self._get_password(attrs['prompt'])
            
                # Store in response object
                self.params.input.set_response(key, val)
            print ''
    
    def update_config(self, project):
        """
        Update the deployed default server configuration.
        """
        
        # Parse and update the configuration
        lce = LenseConfigEditor(project.upper())
        
        # Update each section
        for section, pair in self.params.get_config().iteritems():
            for key, val in pair.iteritems():
                lce.set('{0}/{1}'.format(section, key), val)
            
                # Format the value output
                LENSE.FEEDBACK.success('[{0}] Set key value for "{1}->{2}"'.format(getattr(CONFIG, project.upper()), section, key))
            
        # Apply the configuration changes
        lce.save()
        LENSE.FEEDBACK.success('Applied updated {0} configuration'.format(project))
    
    def bootstrap_info(self):
        """
        Show a brief introduction and summary on the bootstrapping process.
        """
        LENSE.FEEDBACK.block([
            'Lense Bootstrap Utility',
            'The bootstrap utility is used to get a new Lense installation up and',
            'running as quickly as possible. This will set up the database, make sure',
            'any required users exists, and populate the tables with seed data.'   
        ], 'ABOUT')