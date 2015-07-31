import os
import sys
from subprocess import Popen

class LSBInit(object):
    def __init__(self, name, pid, lock, exe, output=None):
        self.name      = name
        
        # Service command / executable
        self.command   = argv[1]
        self.exe       = exe
        
        # PID file / directory
        self.pid_file  = pid
        self.pid_dir   = os.path.dirname(pid) 

        # Lock file / directory
        self.lock_file = lock
        self.lock_dir  = os.path.dirname(lock)

        # Command output
        self.output    = output

    def die(self, msg, code=1):
        sys.stderr.write('{}\n'.format(self.srvc_string(msg)))
        sys.exit(code)

    def write_stdout(self, msg, code=None):
        sys.stdout.write('{}\n'.format(self.srvc_string(msg)))
        if code:
            sys.exit(code)

    def srvc_string(self, msg):
        """
        Prepend service name to a string.
        """
        return '[{}]: {}'.format(self.name, msg)

    def get_pid(self):
        """
        Retrieve the process ID from the PID file.
        """
        if os.path.isfile(self.pid_file):
            return open(self.pid_file, 'r').read()
        return None

    def mk_pid(self):
        """
        Make a PID file and populate with PID number.
        """
        try:
        
            # Make sure the PID directory exists
            if not os.path.isdir(self.pid_dir):
                os.makedirs(self.pid_dir, 0755)
                
            # Create the PID file
            pid_file = open(self.pid_file, 'w').write(self.get_pid())
            pid_file.close()
        except Exception as e:
            self.die('Failed to generate PID file: {}'.format(str(e)))
    
    def rm_pid(self):
        """
        Remove the PID file.
        """
        if os.path.isfile(self.pid_file):
            try:
                os.remove(self.pid_file)
            except Exception as e:
                self.die('Failed to remove PID file: {}'.format(str(e)))
        else:
            return True

    def kill_pid(self):
        """
        Kill the running process and remove the PID/lock file.
        """
        try:
            os.kill(self.get_pid(), 9)
            
        # Failed to kill the process
        except Exception as e:
            self.die('Failed to kill process: {}'.format(str(e)))
            
        # Remove the stale PID file
        self.rm_pid()
          
    def mk_lock(self):
        """
        Make the lock file for the service.
        """
        try:
        
            # Make sure the PID directory exists
            if not os.path.isdir(self.lock_dir):
                os.makedirs(self.lock_dir, 0755)
                
            # Create the lock file
            open(self.lock_file, 'w').close()
        except Exception as e:
            self.die('Failed to generate lock file: {}'.format(str(e)))
            
    def rm_lock(self):
        """
        Remove the service lock file.
        """
        if os.path.isfile(self.lock_file):
            try:
                os.remove(self.lock_file)
            except Exception as e:
                self.die('Failed to remove lock file: {}'.format(str(e)))
        else:
            return True
            
    def is_running(self):
        """
        Check if the service is running.
        """
        try:
            os.kill(self.get_pid(), 0)
        
        # Process not running, remove PID/lock file if it exists
        except:
            self.rm_pid()
            self.rm_lock()
            
    def set_output(self):
        """
        Set the output for the service command.
        """
        if not self.output:
            return os.devnull
        
        # Get the output file path
        output_dir = os.path.dirname(self.output)
        
        # Make the path if it doesn't exist
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
                return self.output
            except Exception as e:
                self.die('Failed to create output directory "{}": {}'.format(output_dir, str(e)))
            
    def do_start(self):
        if not self.is_running():
            try:
                output = self.set_output()
        
                # Generate the run command
                cmd  = ['nohup', self.exe] if isinstance(self.exe, str) else ['nohup'] + self.exe
            
                # Start the process and get the PID number
                proc = Popen(command, shell=False, stdout=output, stderr=output)
                pnum = str(proc.pid)
                
                # Generate the PID and lock files
                self.mk_pid()
                self.mk_lock()
                self.write_stdout('Service is running [PID {}]...'.format(pnum))
                
            # Failed to start process
            except Exception as e:
                self.die('Failed to start service: {}'.format(str(e)))
             
        # Service already running   
        else:
            self.write_stdout('Service already running [PID {}]...'.format(self.get_pid()))
    
    def do_stop(self):
        if self.is_running():
            self.kill_pid()
            self.rm_lock()
            
            # If the service failed to stop
            if self.is_running():
                self.die('Failed to stop service...')
            self.write_stdout('Service stopped...')
            
        # Service already stopped
        else:
            self.write_stdout('Service already stopped...')
    
    def do_status(self):
        pid    = self.get_pid()
        status = 'running [PID {}]'.format(pid) if pid else 'stopped'
        self.write_stdout('Service is {}...'.format(status))
            
    def do_systemd_start(self):
        self.do_start()
    
    def do_restart(self):
        self.do_stop()
        self.do_start()
            
    def interface(self):
        """
        Public method for handling service command argument.
        """
        
        # Possible control arguments
        controls = {
            'start': self.do_start,
            'stop': self.do_stop,
            'status': self.do_status,
            'systemd-start': self.do_systemd_start,
            'restart': self.do_restart,
            'force-reload': self.do_restart    
        }
        
        # Process the control argument
        try:
            controls[self.command]()
        except KeyError:
            self.write_stdout('Usage: {} {{start|stop|status|restart|force-reload|systemd-start}}'.format(self.name), 3)
        sys.exit(0)