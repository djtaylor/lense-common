from lense import import_class

class LenseBase(object):
    def __init__(self, project):
        self.COLLECTION  = import_class('Collection', 'lense.common.collection', init=False)
        self.LOG         = import_class('create_project', 'lense.common.logger', args=[project])
        self.CONF        = import_class('parse', 'lense.common.config', args=[project])
        self.JSON        = import_class('JSONObject', 'lense.common.objects')
        self.FEEDBACK    = import_class('Feedback', 'feedback')
        
        # Generic storage
        self._storage = {}
        
    def retrieve(self, key, default=None):
        """
        Retrieve a key value from generic storage.
        """
        return self._storage.get(key, default)
        
    def store(self, key, value):
        """
        Store a key/value pair in generic storage.
        """
        self._storage[key] = value
        
    def ensure(self, result, **kwargs):
        """
        Ensure a result is equal to 'value' or is not equal to 'isnot'. Raise a RequestError otherwise.
        
        :param result: The result to check
        :type  result: mixed
        :param  value: The value to ensure (equal to)
        :type   value: mixed
        :param  isnot: The value to ensure (not equal to)
        :type   isnot: mixed
        :param  error: The error message to raise
        :type   error: str
        :param   code: The HTTP status code to return if error
        :type    code: int
        :param   call: Call the result object as a method
        :type    call: mixed
        :param   args: Arguments to pass to the object method
        :type    args: list
        :param kwargs: Keyword arguments to pass to the object method
        :type  kwargs: dict
        :param    log: Log a success message
        :type     log: str
        :param  debug: Log a debug message
        :type   debug: str
        :param    exc: The type of exception to raise
        :type     exc: object
        :rtype: result
        """
        
        # Code / error / call / log / debug
        code  = kwargs.get('code', 400)
        error = kwargs.get('error', 'An unknown request error has occurred')
        call  = kwargs.get('call', False)
        log   = kwargs.get('log', None)
        debug = kwargs.get('debug', None)
        exc   = kwargs.get('exc', EnsureError)
        
        # Cannot specify both value/isnot at the same time
        if ('value'in kwargs) and ('isnot' in kwargs):
            raise Exception('Cannot supply both "value" and "isnot" arguments at the same time')
        
        # Equal to / not equal to
        value = kwargs.get('value', None)
        isnot = kwargs.get('isnot', None)
        
        # If calling the result object as a method
        if call:
            
            # Args / kwargs
            call_args = kwargs.get('args', [])
            call_kwargs = kwargs.get('kwargs', {})
            
            # Method must be callable
            if not callable(result):
                raise exc('Cannot ensure <{0}>, object not callable'.format(repr(result)))
            
            # Attempt to run the method
            try:
                result = result(*call_args, **call_kwargs)
            except Exception as e:
                raise exc('Failed to call <{0}>: {1}'.format(repr(result, str(e))), 500)
        
        # Negative check (not equal to)
        if 'isnot' in kwargs:
            if result == isnot:
                raise exc(error, code)
        
        # Positive check (equal to)
        if 'value' in kwargs:
            if result != value:
                raise exc(error, code)
        
        # Log info/debug
        if log:
            self.LOG.info(log)   
        if debug:
            self.LOG.debug(debug)
        
        # Return the result
        return result
        
    def rmfile(self, file):
        """
        Remove a file/symlink if it exists.
        
        :param file: The target file
        :type  file: str
        """
        if os.path.isfile(file) or os.path.islink(file):
            unlink(file)
        
    def rmdir(self, path):
        """
        Recursively remove a directory.
        
        :param path: The directory to remove
        :type  path: str
        """
        if os.path.isdir(path):
            rmtree(path)
        
    def mvfile(self, src, dst):
        """
        Move a file from one place to another.
        
        :param src: The source file
        :type  src: str
        :param dst: The destination file
        :type  dst: str
        """
        move_file(src, dst)
        
    def mklink(self, target, link):
        """
        Make a symbolic link.
        
        :param target: The target file
        :type  target: str
        :param   link: The target link
        :type    link: str
        """
        os.symlink(target, link)
        
    def mkdir(self, dir_path):
        """
        Make a directory and return the path name.
        
        :rtype: str
        """
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path
        
    def shell_exec(self, cmd, show_stdout=True):
        """
        Run an arbitrary system command.
        
        :param cmd: The command list to run
        :type  cmd: list
        """
        
        # If showing stdout
        if show_stdout:
            proc = Popen(cmd, stderr=PIPE)
            err = proc.communicate()
            
        # If supressing stdout
        else:
            proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()

        # Return code, stderr
        return proc.returncode, err
        
    def thread(self, mapper):
        """
        Multithreading wrapper for calling methods and storing results.
        
        :param mapper: Multithreading mapper object
        :type  mapper: dict
        :rtype: dict
        """
        self.ensure(isinstance(mapper, dict), value=True, error='Argument must be a dictionary')
        
        # Threads / results / exceptions
        threads    = []
        results    = {}
        exceptions = []
        
        # Thread worker
        def worker(key, method, args, kwargs):
            """
            Internal thread worker to allow multiple thread namespaces.
            
            :param key: The namespace key
            :type  key: str
            :param method: The worker method
            :type  method: callable
            """
            try:
                results[key] = method(*args, **kwargs)
            except Exception as e:
                exceptions.append(e)
        
        # Process each mapper object
        for key, attrs in mapper.iteritems():
            self.ensure(callable(attrs.get('method', None)), value=True, error='Thread attributes must have a callable "method" argument')

            # Call the thread method
            thread = Thread(target=worker, args=(key, attrs['method'], attrs.get('args', []), attrs.get('kwargs', {})))
            threads.append(thread)
            thread.start()
            
        # Wait for threads to complete
        for thread in threads:
            thread.join()
            
        # Look for exceptions
        if exceptions:
            raise exceptions[0]
            
        # Return results
        return results
        
    def die(self, msg, code=1, pre=None, post=None):
        """
        Print to stderr and immediately exit
        
        :param  msg: The message to render
        :type   msg: str
        :param code: The exit code
        :type  code: int
        :param  pre: Pre-message method
        :type   pre: method
        :param post: Post-message method
        :type  post: method 
        """
        
        # Pre callback
        if callable(pre): pre()
        
        # If bootstrapping
        if getattr(__builtin__, 'BOOTSTRAP', None):
            self.FEEDBACK.error(msg)
            
        # Else write to stderr
        else:
            stderr.write('{0}\n'.format(msg) if not isinstance(msg, list) else '\n'.join([l for l in msg]))
        
        # Post callback
        if callable(post): post()
        
        # Attempt to log
        if LENSE and hasattr(LENSE, 'LOG'):
            self.LOG.error(msg)
        exit(code)