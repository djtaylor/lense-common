from __future__ import print_function
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

    def _shell_exec(self, cmd):
        """
        Private method for running an arbitrary shell command.
        
        :param cmd: The command list to run
        :type  cmd: list
        """
        proc = Popen(cmd, stderr=PIPE)
        err = proc.communicate()

        # Return code, stderr
        return proc.returncode, err

    def _chmod(self, file, mode, recursive=False):
        """
        Wrapper method for chmoding a file path.
        
        :param      file: The file path to chmod
        :type       file: str
        :param      mode: The new file mode
        :type       mode: str
        :param recursive: Chmod recursively or not
        :type  recursive: bool
        """
        chmod_cmd = ['chmod']
        if recursive:
            chmod_cmd.append('-R')
        chmod_cmd += [mode, file]
        
        # Change the permissions
        code, err = self._shell_exec(chmod_cmd)
    
        # If the command failed
        if not code == 0:
            self.die('Failed to chown file "{0}": {1}'.format(file, err))
        LENSE.FEEDBACK.success('Changed owner on file "{0}" -> "{1}"'.format(file, owner))

    def _chown(self, file, owner, recursive=False):
        """
        Wrapper method for chowning a file path.
        
        :param      file: The file path to chown
        :type       file: str
        :param     owner: The new file owner
        :type      owner: str
        :param recursive: Chown recursively or not
        :type  recursive: bool
        """
        chown_cmd = ['chown']
        if recursive:
            chown_cmd.append('-R')
        chown_cmd += [owner, file]
        
        # Change the owner
        code, err = self._shell_exec(chown_cmd)

        # If the command failed
        if not code == 0:
            self.die('Failed to chown file "{0}": {1}'.format(file, err))
        LENSE.FEEDBACK.success('Changed owner on file "{0}" -> "{1}"'.format(file, owner))

    def _create_system_user(self):
        """
        Create the lense system account.
        """
        try:
            getpwnam('lense')
            return LENSE.FEEDBACK.info('System account "lense" already exists, skipping...')
        except KeyError:
            pass
            
        # Create the user account
        code, err = self._shell_exec(['/usr/sbin/useradd', '-M', '-s', '/usr/sbin/nologin', 'lense'])
        
        # Make sure the command returned successfully
        if not code == 0:
            self.die('Failed to create system account: {0}'.format(str(err)))
        LENSE.FEEDBACK.success('Created system account "lense"')

    def _get_password(self, prompt, min_length=8):
        """
        Convenience method for retriving a user entered password.
        
        :param     prompt: The prompt to display when asking for a password
        :type      prompt: str
        :param min_length: The minimum length of the password
        :type  min_length: int
        """
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
        """
        Convenience method for retriving plain text user input.
        
        :param  prompt: The prompt to display when asking for input
        :type   prompt: str
        :param default: The default value if none provided by the user
        :type  default: str|int|dict|list
        """
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            LENSE.FEEDBACK.error('Must provide a value')
            return self._get_input(prompt, default)
        return _input

    def die(self, msg, log=True):
        """
        Quit the program.
        
        :param msg: The error message to display
        :type  msg: str
        :param log: Log the error or not
        :type  log: bool
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
        
        :param user: The user account to add to the lense group
        :type  user: str
        """
        try:
            getpwnam(user)
            
            # Create the user account
            code, err = self._shell_exec(['/usr/sbin/usermod', '-a', '-G', 'lense', user])
            
            # Make sure the command returned successfully
            if not code == 0:
                self.die('Failed to add user "{0}" to lense group: {1}'.format(user, str(err)))
            LENSE.FEEDBACK.success('Added user "{0}" to lense group'.format(user))
        except Exception as e:
            self.die('Could not add user "{0}" to lense group: {1}'.format(user, str(e)))        
            
    def dirname(self, file):
        """
        Return the parent directory of a file.
        
        :param file: The file path to find the parent directory of
        :type  file: str
        """
        return path.dirname(file)

    def deploy_apache(self):
        """
        Deploy Apache configuration files.
        """
        if hasattr(WSGI_CONFIG, self.project.upper()):
            
            # Deploy the virtual host if the project has one
            code, err = self._shell_exec(['a2ensite', getattr(WSGI_CONFIG, self.project.upper())])
        
            # Make sure the command returned successfully
            if not code == 0:
                self.die('Failed to enable virtual host: {0}'.format(str(err)))
            LENSE.FEEDBACK.success('Enabled virtual host configuration for Lense API {0}'.format(project))

    def mkdir(self, d):
        """
        Make sure a directory structure exists.
        
        :param d: The directory to created
        :type  d: str
        """
        if not path.isdir(d):
            LENSE.FEEDBACK.info('Created directory: {0}'.format(d))
            return makedirs(d)
        LENSE.FEEDBACK.info('Directory already exists: {0}'.format(d))

    def mkdirs(self, dirs):
        """
        Make required directories.
        
        :param dirs: A list of directories to create
        :type  dirs: list
        """
        for d in dirs: self.mkdir(d)
    
    def set_permissions(self, file, owner=None, mode=None, recursive=False, create=True, mkdir=True):
        """
        Convenience method for setting permissions on files.
        
        :param file:      The file path to modify permissions for
        :type  file:      str
        :param owner:     The new file owner (i.e., "user", "user:group")
        :type  owner:     str
        :param mode:      The new file mode (i.e., "755", "g+x")
        :type  mode:      str
        :param recursive: Change permissions recursively or not
        :type  recursive: bool
        :param create:    Create the file if it doesn't exist
        :type  create:    bool
        :param mkdir:     Create the directory structure if it doesn't exist
        :type  mkdir:     bool
        """
        
        # Make sure the directory exists if the flag is given
        if mkdir:
            self.mkdir(self.dirname(file))
        
        # Make sure the file exists if the flag is given
        if create and not path.isfile(file):
            open(file, 'w').close()
        
        if path.isfile(file):
            
            # Changing owner
            if owner:
                self._chown(file, owner, recursive)
            
            # Changing file permissions
            if mode:
                self._chmod(file, mode, recursive)
            
            # Permissions set
            return True
            
        # File does not exist
        return False
    
    def read_input(self, answers={}):
        """
        Read any required user input prompts
        
        :param answers: The optional answers object to look for pre-defined values
        :type  answers: dict
        """
        
        # Process each configuration section
        for section, obj in self.params.input.prompt.iteritems():
            print(obj['label'])
            print('-' * 20)
        
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
            print('')
    
    def update_config(self):
        """
        Update the deployed default server configuration.
        
        :param project: The target project ID
        :type  project: str
        """
        
        # Parse and update the configuration
        lce = LenseConfigEditor(self.project.upper())
        
        # Update each section
        for section, pair in self.params.get_config().iteritems():
            for key, val in pair.iteritems():
                lce.set('{0}/{1}'.format(section, key), val)
            
                # Format the value output
                LENSE.FEEDBACK.success('[{0}] Set key value for "{1}->{2}"'.format(self.ATTRS.CONF, section, key))
            
        # Apply the configuration changes
        lce.save()
        LENSE.FEEDBACK.success('Applied updated {0} configuration'.format(self.project))
    
    def bootstrap_preflight(self):
        """
        Methods to be run prior to bootstrapping specific projects.
        """
        
        # Make sure the system user/group exists
        self._create_system_user()
    
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