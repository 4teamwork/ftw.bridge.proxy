from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.utils import protected
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from zope.component import getUtility


class ProxyView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        IAuthorizationManager(self.request).authorize()
        return IProxy(self.request)()


class ManageView(object):

    def __init__(self, request):
        self.request = request

    @protected
    def __call__(self):
        if self.request.params.get('clientid'):
            clientid = self.request.params.get('clientid')
            status = self.request.params.get('status', 'online')
            client = getUtility(IClientManager).get_client_by_id(clientid)
            client.set_maintenance_mode(status == 'maintenance')
            return HTTPFound(location='/manage')

        return render_to_response(
            'ftw.bridge.proxy:templates/manage.pt',
            {'clients': self.get_clients()},
            request=self.request)

    def get_clients(self):
        return getUtility(IClientManager).get_clients()
