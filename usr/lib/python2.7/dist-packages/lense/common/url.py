class LenseURLConstructor(object):
    """
    Helper class for constructing endpoint URLs
    """
    @staticmethod
    def _map(self, proto, host, port, url_path):
        """
        Private method for mapping a URL.
        """
        
        # Account for non-default ports
        port_http  = '' if (port == 80) else ':{0}'.format(port)
        port_https = '' if (port == 443) else ':{0}'.format(port)
        
        # Set the port
        port       = port_http if (proto == 'http') else port_https
        
        # Return the formatted URL
        return '{0}://{1}{2}{3}'.format(proto, host, port, ('' if not url_path else '/{0}'.format(url_path)))
    
    @staticmethod
    def engine(self, url_path=None):
        """
        Return an engine API url.
        
        :param url_path: Optional path to append to the URL
        :type  url_path: str
        """
        
        # Extract the URL attributes from the config
        url_attrs = getattr(LENSE.CONF, 'engine')
        
        # Return the mapped URL
        return LenseURLConstructor._map(url_attrs.proto, url_attrs.host, url_attrs.port, url_path)
        
    @staticmethod
    def portal(self, url_path=None):
        """
        Return a portal API url.
        
        :param url_path: Optional path to append to the URL
        :type  url_path: str
        """
        
        # Extract the URL attributes from the config
        url_attrs = getattr(LENSE.CONF, 'portal')
        
        # Return the mapped URL
        return LenseURLConstructor._map(url_attrs.proto, url_attrs.host, url_attrs.port, url_path)
        
    @staticmethod
    def socket(self, url_path=None):
        """
        Return a socket API url.
        
        :param url_path: Optional path to append to the URL
        :type  url_path: str
        """
        
        # Extract the URL attributes from the config
        url_attrs = getattr(LENSE.CONF, 'socket')
        
        # Return the mapped URL
        return LenseURLConstructor._map(url_attrs.proto, url_attrs.host, url_attrs.port, url_path)