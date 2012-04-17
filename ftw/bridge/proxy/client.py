from ftw.bridge.proxy.interfaces import IClient
from ftw.bridge.proxy.interfaces import IClientManager
from pyramid.interfaces import ISettings
from zope.component import getUtility
from zope.interface import implements


class ClientManager(object):
    implements(IClientManager)

    def __init__(self):
        self._clients = None

    def get_clients(self):
        if self._clients is None:
            self._load_clients()
        return self._clients

    def get_client_by_id(self, clientid):
        for client in self.get_clients():
            if client.clientid == clientid or \
                    clientid in client.aliases:
                return client

        return None

    def _load_clients(self):
        self._clients = []
        for clientdata in self._parse_clients().values():
            self._clients.append(Client(**clientdata))

    def _parse_clients(self):
        clients = {}
        settings = getUtility(ISettings)

        for key, value in settings.items():
            if key.startswith('clients.'):
                _prefix, clientid, option = key.split('.')

                if clientid not in clients:
                    clients[clientid] = {'clientid': clientid}

                clients[clientid][option] = self._parse_option(option, value)

        return clients

    def _parse_option(self, name, value):
        if name in ('aliases', 'ip_addresses'):
            return [val.strip() for val in value.strip().split(',')]
        else:
            return value.strip()


class Client(object):

    implements(IClient)

    def __init__(self, clientid, ip_addresses, internal_url, public_url,
                 aliases=None):
        if not aliases:
            aliases = []

        self.clientid = clientid
        self.ip_addresses = ip_addresses
        self.internal_url = internal_url
        self.public_url = public_url
        self.aliases = aliases
        self._offline_for_maintenance = False

    def is_in_maintenance_mode(self):
        """Returns ``True`` if the client is in maintenance mode, otherwise
        ``False``.
        """
        return self._offline_for_maintenance

    def set_maintenance_mode(self, offline):
        """Sets the maintenance mode for this client.
        """
        self._offline_for_maintenance = offline

    def get_internal_url(self):
        """Returns the internal url of the client with a trailing slash.
        """
        if not self.internal_url.endswith('/'):
            return self.internal_url + '/'
        else:
            return self.internal_url

    def get_public_url(self):
        """Returns the public url of the client with a trailing slash.
        """
        if not self.public_url.endswith('/'):
            return self.public_url + '/'
        else:
            return self.public_url
