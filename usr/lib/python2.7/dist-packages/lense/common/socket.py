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
                LENSE.LOG.info('Initialized SocketIO proxy connection -> {0}:{1}'.format(LENSE.CONF.socket.host, LENSE.CONF.socket.port))
            else:
                LENSE.LOG.info('SocketIO proxy server disabled - skipping...')
            
        # Critical error when opening connection
        except Exception as e:
            LENSE.LOG.info('Failed to initialize SocketIO proxy connection: {}'.format(str(e)))
        
    def set(self, params=None):
        """
        Set the web socket client attributes.
        """
        self.params = set_arg(params, LENSE.REQUEST.data.get('socket', None))
        if self.params:
            LENSE.LOG.info('Received connection from web socket client: {}'.format(str(self.params)))
        return params
        
    def disconnect(self):
        """
        Disconnect the Socket.IO client.
        """
        try:
            self.io.disconnect()
            LENSE.LOG.info('Closing SocketIO proxy connection')
        except:
            pass
        
    def broadcast(self, t, d={}):
        """
        Broadcast data to all web socket clients.
        """
        if self.io and LENSE.CONF.socket.enable:
            self.io.emit('update', {'type': t, 'content': d})
        
    def loading(self, m=None):
        """
        Send a loading messages to a web socket client.
        """
        if self.params and self.io and LENSE.CONF.socket.enable:
            self.io.emit('update', { 'room': self.params['room'], 'type': 'loading', 'content': m})