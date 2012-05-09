from ftw.bridge.proxy import LOG
from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.utils import protected
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.response import Response
from zope.component import getAdapter
from zope.component import getUtility


class ProxyView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        origin = self.request.headers.get('X-BRIDGE-ORIGIN', None)
        url = self.request.url
        try:
            response = self._handle()

        except Exception, exc:
            LOG.error('%s: "%s" FAILED (%s): %s: %s' % (
                    self.request.method, origin, url,
                    type(exc).__name__, str(exc)))
            raise

        else:
            LOG.info('%s: "%s" %s (%s)' % (
                    self.request.method,
                    origin, response.status, url))
            return response

    def _handle(self):
        auth_manager = getAdapter(self.request, IAuthorizationManager)
        auth_manager.authorize()
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
            LOG.info('manage: change status of %s to %s' % (
                    clientid, status))
            return HTTPFound(location=self.request.headers.get('Referer'))

        return render_to_response(
            'ftw.bridge.proxy:templates/manage.pt',
            {'clients': self.get_clients()},
            request=self.request)

    def get_clients(self):
        return getUtility(IClientManager).get_clients()


class StatusCheckView(object):
    """This view is used for status check, such as by supervisor.
    It always returns 'OK'.
    """

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return Response('OK')
