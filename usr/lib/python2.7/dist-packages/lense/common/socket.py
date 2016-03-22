from lense import set_arg
from socketIO_client import SocketIO

class LenseSocketIO(object):
    """
    Class objects for handling SocketIO interactions.
    """
    def __init__(self):
        self.io     = None
        self.params = None
        
        # Try to open the connection
        try:
            if LENSE.CONF.socket.enable:
                self.io = SocketIO(LENSE.CONF.socket.host, int(LENSE.CONF.socket.port))
                
                # Socket connection opened sucessfully
                self.log('Initialized SocketIO proxy connection -> {0}:{1}'.format(LENSE.CONF.socket.host, LENSE.CONF.socket.port), level='info', method='__init__')
            else:
                self.log('SocketIO proxy administratively disabled: conf.socket.enable = {0}'.format(repr(LENSE.CONF.socket.enable)), level='info', method='__init__')
            
        # Critical error when opening connection
        except Exception as e:
            self.log('Failed to initialize SocketIO connection', level='exception', method='__init__')
        
    def log(self, msg, level='info', method=None):
        """
        Wrapper method for logging with a prefix.
        
        :param    msg: The message to log
        :type     msg: str
        :param  level: The desired log level
        :type   level: str
        :param method: Optionally append the method to log prefix
        :type  method: str
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<SOCKET{0}> {1}'.format(
            '' if not method else '.{0}'.format(method),
            msg
        ))
        
    def set(self, params=None):
        """
        Set the web socket client attributes.
        """
        self.params = set_arg(params, LENSE.REQUEST.data.get('socket', None))
        if self.params:
            self.log('Received connection from web socket client: {0}'.format(self.params), method='set')
        return params
        
    def disconnect(self):
        """
        Disconnect the Socket.IO client.
        """
        try:
            self.io.disconnect()
            self.log('Closing SocketIO connection', method='disconnect')
        except:
            pass
        
    def broadcast(self, t, d={}):
        """
        Broadcast data to all web socket clients.
        """
        if self.io and LENSE.CONF.socket.enable:
            self.io.emit('update', {'type': t, 'content': d})
            self.log('Broadcasting message: type={0}, content={1}'.format(t, d), level='debug', method='broadcast')
        
    def loading(self, m=None):
        """
        Send a loading messages to a web socket client.
        """
        if self.params and self.io and LENSE.CONF.socket.enable:
            self.io.emit('update', { 'room': self.params['room'], 'type': 'loading', 'content': m})
            self.log('Sending loading message: room={0}, type=loading, content={1}'.format(self.params['room'], m), level='debug', method='loading')