from ftw.bridge.proxy.interfaces import IClientManager
from pyramid.interfaces import ISettings
from zope.component import getUtility
from zope.interface import implements


class ClientManager(object):
    implements(IClientManager)

    def get_clients(self):
        return self._parse_clients()

    def get_client_by_id(self, clientid):
        for client in self.get_clients().values():
            if clientid == client['clientid'] or \
                    clientid in client.get('aliases', []):
                return client

        return None

    def _parse_clients(self):
        clients = {}
        settings = getUtility(ISettings)

        for key, value in settings.items():
            if key.startswith('clients.'):
                prefix_, clientid, option = key.split('.')

                if clientid not in clients:
                    clients[clientid] = {'clientid': clientid}

                clients[clientid][option] = self._parse_option(option, value)

        return clients

    def _parse_option(self, name, value):
        if name in ('aliases', 'ip_addresses'):
            return [val.strip() for val in value.strip().split(',')]
        else:
            return value.strip()
