from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IAuthorizationPlugin
from ftw.bridge.proxy.interfaces import IClientManager
from pyramid.exceptions import Forbidden
from pyramid.interfaces import IRequest
from zope.component import adapts
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implements


class AuthorizationManager(object):
    implements(IAuthorizationManager)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request

    def authorize(self):
        client = self._get_client()
        plugin = self._get_authorization_plugin(client.clientid)

        if plugin.is_authorized(client) != True:
            raise Forbidden()
        else:
            return True

    def _get_client(self):
        """If the request can be identified and a client configuration for
        the client is found, the client (dict) is returned.
        Otherwise `Forbidden` is raised.
        """
        origin = self.request.headers.get('X-BRIDGE-ORIGIN', None)
        if origin is None:
            raise Forbidden()

        client = getUtility(IClientManager).get_client_by_id(origin)
        if client is None:
            raise Forbidden()

        return client

    def _get_authorization_plugin(self, clientid):
        plugin = queryAdapter(self.request, IAuthorizationPlugin,
                              name=clientid)
        if plugin is not None:
            return plugin
        else:
            return getAdapter(self.request, IAuthorizationPlugin)


class DefaultAuthorizationPlugin(object):
    implements(IAuthorizationPlugin)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request
        self._client = None

    def is_authorized(self, client):
        return self._get_request_ip() in client.ip_addresses

    def _get_request_ip(self):
        """Returns the IP address of the host which sent the request initally.
        """
        ips = self.request.environ.get(
            'HTTP_X_FORWARDED_FOR',
            self.request.environ.get('REMOTE_ADDR'))

        if ips is None or not hasattr(ips, 'split'):
            return ips
        else:
            return ips.split(',')[0].strip()
