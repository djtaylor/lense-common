import os
import re
import sys
import signal
import argparse
import platform
import subprocess
from feedback import Feedback

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.vars import L_BASE

class ServiceManager:
    """
    Lense services manager class designed to handle starting/stopping/restarting all
    Lense services. This includes the API server, Socket.IO proxy server, and the
    scheduler service.
    """
    def __init__(self, args):
        
        # Configuration / logger / feedback handler
        self.conf     = config.parse()
        self.log      = logger.create(__name__, self.conf.server.log)
        self.fb       = Feedback()
        
        # Actions mapper
        self.actions  = {
            'start': self._start,
            'stop': self._stop,
            'restart': self._restart,
            'status': self._status
        }
        
        # Services mapper
        self.services = {
            'portal':    {
                'apache': True,
                'label':  'portal'
            },
            'api': {
                'apache': True,
                'label':  'API server'
            },
            'socket':    {
                'apache': False,
                'pid':    self.conf.socket.pid,
                'label':  'API socket proxy',
                'start':  ['nohup', 'nodejs', self.conf.socket.exe]
            },
            'scheduler': {
                'apache': False,    
                'pid':    self.conf.scheduler.pid,
                'label':  'API scheduler',
                'start':  ['nohup', 'python', self.conf.scheduler.exe]
            }
        }
        
        # Target action / service
        self.action   = None
        self.service  = None
        
        # Argument parser
        self.ap       = self._parse_args(args)
        
        # Server distribution and Apache service name
        self.distro   = platform.linux_distribution()[0]
        
    def _parse_args(self, args):
        """
        Parse any command line arguments and look for the service action, and an optional service
        name if managing a specific service.
        """
        
        # Create a new ArgumentParser object
        ap = argparse.ArgumentParser(
            description     = self._return_help(),
            formatter_class = argparse.RawTextHelpFormatter
        )
        
        # Required action argument
        ap.add_argument('action', help=self._return_actions())
        
        # Optional service argument
        ap.add_argument('service', nargs='?', help=self._return_services())
        
        # Parse child arguments
        args.pop(0)
        args = vars(ap.parse_args(args))
        
        # Set the target action and service
        self.action  = None if not ('action' in args) else args['action']
        self.service = None if not ('service' in args) else args['service']
        
        # Return the argument parse object
        return ap
        
    def _return_help(self):
        """
        Return the utility help prompt.
        """
        return ('Lense Server Manager\n\n'
                'Manage the available Lense server processes. This utility is used to start, stop, and\n'
                'restart the Lense portal, API, socket proxy, and task scheduler. You may specify an\n'
                'optional service argument to manage individual services.')
    
    def _return_actions(self):
        """
        Return a list of available actions.
        """
        return ('stop       Stop all server processes or the target service\n'
                'start      Start all server processes or the target service\n'
                'restart    Restart all server processes or the target service\n'
                'status     Get the status of each server process or the target service')
        
    def _return_services(self):
        """
        Return a list of available services.
        """
        return ('portal     The web portal interface\n'
                'api        The API server\n'
                'socket     The socket proxy server\n'
                'scheduler  The API scheduler service')
        
    def _is_running(self, pid_file):
        """
        Check if a target process is running by the PID file.
        """
        try:
            pid_num = open(pid_file, 'r').read()
            try:
                os.kill(int(pid_num), 0)
                return pid_num
            except:
                os.remove(pid_file)
                return False
        except:
            return False

    def _apache(self):
        """
        Get the Apache service name depending on the current distribution.
        """
        if self.distro.lower() == 'centos':
            return 'httpd'
        if self.distro.lower() == 'ubuntu':
            return 'apache2'
        
    def _apache_running(self):
        """
        Check if Apache is running.
        """
        if self.distro.lower() == 'centos':
            check_apache_cmd = 'service httpd status'
        if self.distro.lower() == 'ubuntu':
            check_apache_cmd = 'service apache2 status'
        
        # Check if Apache is running
        process = subprocess.Popen(check_apache_cmd, shell=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        out, err = process.communicate()
        if re.match(r'^.*is[ ]running.*$', out):
            return True
        else:
            return False
    
    def _start(self):
        """
        Start the service process.
        """
        
        # Apache start flag
        apache_started = False
        
        # Process each service definition
        for srv_name, srv_attr in self.services.iteritems():
            
            # If targeting a specific service
            if self.service:
                if not self.service == srv_name:
                    continue
        
            # If the service is managed by Apache
            if srv_attr['apache']:
                
                # If Apache is not running
                if not self._apache_running():
                    
                    # Start Apache
                    try:
                        output = open(os.devnull, 'w')
                        proc   = subprocess.Popen(['service', self._apache(), 'start'], shell=False, stdout=output, stderr=output)
                    
                    # Failed to start Apache
                    except Exception as e:
                        self.fb.show('Lense %s failed to start...' % srv_attr['label']).error()
                        sys.exit(1)
                    
                    # Apache started
                    self.fb.show('Starting Lense %s...' % srv_attr['label']).success()
                    apache_started = True
                    
                # If Apache is already running
                else:
                    
                    # If Apache was started earlier
                    if apache_started:
                        self.fb.show('Starting Lense %s...' % srv_attr['label']).success()
                    else:
                        self.fb.show('Lense %s already running...' % srv_attr['label']).info()
                
            # If the service is an independent process
            else:
                
                # Check if the service is running
                pid = self._is_running(srv_attr['pid'])
        
                # If the service is not running
                if not pid:
                    try:
                    
                        # Set stdout/stderr redirection
                        output = open(os.devnull, 'w')
            
                        # Start the process and get the PID number
                        proc   = subprocess.Popen(srv_attr['start'], shell=False, stdout=output, stderr=output)
                        pnum   = str(proc.pid)
                        
                    # Failed to start the process
                    except Exception as e:
                        self.fb.show('Failed to start Lense %s...' % srv_attr['label']).error()
                        sys.exit(1)
                        
                    # Service started
                    self.fb.show('Starting Lense %s [PID %s]...' % (srv_attr['label'], pnum)).success()
                    
                    # Make sure the PID file directory exists
                    if not os.path.exists('%s/run' % L_BASE):
                        os.makedirs('%s/run' % L_BASE, 0750)
                        
                    # Create or update the PID file
                    open(srv_attr['pid'], 'w').write(pnum)
                    
                # If the service is already running
                else:
                    self.fb.show('Lense %s already running [PID %s]...' % (srv_attr['label'], pid)).info()
    
    def _stop(self):
        """
        Stop the Lense services.
        """
        
        # Apache stop flag
        apache_stopped = False
        
        # Process each service definition
        for srv_name, srv_attr in self.services.iteritems():
            
            # If targeting a specific service
            if self.service:
                if not self.service == srv_name:
                    continue
        
            # If the service is managed by Apache
            if srv_attr['apache']:
                
                # If Apache is running
                if self._apache_running():
                    try:
                        output = open(os.devnull, 'w')
                        proc   = subprocess.Popen(['service', self._apache(), 'stop'], shell=False, stdout=output, stderr=output)
                        pnum   = str(proc.pid)
                    
                    # Failed to stop Apache
                    except Exception as e:
                        self.fb.show('Failed to stop Lense %s...' % srv_attr['label']).error()
                        sys.exit(1)
                        
                    # Apache stopped
                    self.fb.show('Stopping Lense %s...' % srv_attr['label']).success()
                    apache_stopped = True
                    
                # If Apache is already stopped
                else:
                    
                    # If Apache was stopped earlier
                    if apache_started:
                        self.fb.show('Stopping Lense %s...' % srv_attr['label']).success()
                    else:
                        self.fb.show('Lense %s already stopped...' % srv_attr['label']).info()
                
            # If the service is an independent process
            else:
        
                # If the service is running
                if self._is_running(srv_attr['pid']):
            
                    # Get the PID number and kill the process
                    pnum = open(srv_attr['pid'], 'r').read()
                    os.kill(int(pnum), 9)
                    
                    # Remove the PID file
                    os.remove(srv_attr['pid'])
                    
                    # If the process failed to stop
                    if self._is_running(srv_attr['pid']):
                        self.fb.show('Failed to stop Lense %s...' % srv_attr['label']).error()
                        sys.exit(1)
                        
                    # Process successfully stopped
                    else:
                        self.fb.show('Stopping Lense %s...' % srv_attr['label']).success()
                    
                # If the service is already stopped
                else:
                    self.fb.show('Lense %s already stopped...' % srv_attr['label']).info()
    
    def _restart(self):
        """
        Restart the Lense services.
        """
        self._stop()
        self._start()
    
    def _status(self):
        """
        Get the Lense service status.
        """
        for srv_name, srv_attr in self.services.iteritems():
            
            # If targeting a specific service
            if self.service:
                if not self.service == srv_name:
                    continue
            
            # If the service is managed by Apache
            if srv_attr['apache']:
                
                # Set the status
                status = 'running' if (self._apache_running()) else 'stopped'
                
                # Show the managed service status
                self.fb.show('Lense %s is %s...' % (srv_attr['label'], status)).info()
                    
            # If the service is an independent process
            else:
                
                # Check if the service is running
                pid    = self._is_running(srv_attr['pid'])
                
                # Set the status
                status = 'running [PID %s]' % pid if pid else 'stopped'
        
                # Show the service status
                self.fb.show('Lense %s is %s...' % (srv_attr['label'], status)).info()
        
    def handler(self):
        """
        Worker method for launching the service handler.
        """
        
        # Make sure the action is valid
        if not self.action or not (self.action in self.actions):
            self.ap.print_help()
            self.ap.exit()
            
        # Make sure the service is valid if specified
        if self.service:
            if not self.service in self.services:
                self.ap.print_help()
                self.ap.exit()
        
        # Run the action handler
        self.actions[self.action]()
     
def cli():
    """
    Entry point method for the 'lense-server' command line utility.
    """
    ServiceManager(sys.argv).handler()