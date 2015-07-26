import re
from subprocess import Popen, PIPE, STDOUT

class SysCtl:
    """
    Interface class for interacting with Linux kernel parameters and the
    sysctl.conf file.
    """
    def __init__(self):
        
        # Current parameters and config file
        self.params = {}
        self.config = []
        
        # Load sysctl parameters
        self._load_sysctl()
    
    def _load_sysctl(self):
        """
        Load kernel parameters by parsing 'sysctl -a' as well as the sysctl.conf
        configuration file. Load 'sysctl -a' into the params object, and the config
        file into the config object.
        """
        proc      = Popen(['sysctl', '-a'], stdout=PIPE, stderr=PIPE)
        out, err  = proc.communicate()
        exit_code = proc.returncode

        # Make sure parameters were retrieved
        if not exit_code == 0:
            self.params = {}
        else:
            for l in out.split('\n'):
                if l:
                    p = l.split('=')
                    k = p[0].rstrip()
                    v = p[1].lstrip()
                    self.params[k] = v

        # Load the sysctl configuration file
        with open('/etc/sysctl.conf', 'r') as f:
            for l in f.readlines():
                self.config.append(l.rstrip())
           
    def apply(self):
        """
        Apply updates to sysctl.
        
        Apply changes::
        
            # Create a sysctl instance
            from cloudscape.common.sysctl import SysCtl
            sc = SysCtl()
            
            # Unset a kernel parameter value
            sc.unset('net.ipv4.ip_nonlocal_bind')
            
            # Update/set a new kernel parameter
            sc.set('net.ipv4.conf.all.accept_source_route', '1')
            
            # Apply the new configuration
            sc.apply()
            
        """
        with open('/etc/sysctl.conf', 'w') as f:
            for l in self.config:
                f.write('%s\n' % l)
                
        # Reload sysctl
        proc      = Popen(['sysctl', '-p'], stdout=PIPE, stderr=PIPE)
        out, err  = proc.communicate()
        exit_code = proc.returncode
        if not exit_code == 0:
            raise Exception('Failed to apply kernel parameters')
        
        # Reload the config and params and return true
        self._load_sysctl()
        return True
            
    def get(self, k):
        """
        Retrieve a sysctl kernel parameter value by querying the key.
        
        Retrieve a kernel parameter::
        
            # Create a sysctl instance
            from cloudscape.common.sysctl import SysCtl
            sc = SysCtl()
            
            # Print a kernel parameter value
            print cs.get('net.ipv4.ip_nonlocal_bind')
            
        """
        if k in self.params:
            return self.params[k]

    def unset(self, k):
        """
        Unset a persistent parameter value in the config file.
        
        Unset a kernel parameter::
        
            # Create a sysctl instance
            from cloudscape.common.sysctl import SysCtl
            sc = SysCtl()
            
            # Unset a kernel parameter value
            sc.unset('net.ipv4.ip_nonlocal_bind')
            
        """
        for i,l in enumerate(self.config):
            if re.match(r'^%s.*$' % k, l):
                del self.config[i]
                break
        return True

    def set(self, k, v):
        """
        Set a persistent parameter value in the config file.
        
        Set a kernel parameter::
        
            # Create a sysctl instance
            from cloudscape.common.sysctl import SysCtl
            sc = SysCtl()
            
            # Set a kernel parameter value
            sc.set('net.ipv4.ip_nonlocal_bind', '1')
            
        """
        keyset = False
        for i,l in enumerate(self.config):

            # Key already set in config, replace
            if re.match(r'^%s.*$' % k, l):
                keyset = True
                self.config[i] = '%s = %s' % (k,v)
                break

        # Key not set, append
        if not keyset:
            self.config.append('%s = %s' % (k,v))
        return True