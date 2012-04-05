from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.interfaces import PORTAL_URL_PLACEHOLDER
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.interfaces import IRequest
from pyramid.response import Response
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
import requests


class Proxy(object):
    implements(IProxy)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request
        self._client = None

    def __call__(self):
        if self._get_client().is_in_maintenance_mode():
            raise HTTPServiceUnavailable()

        response = requests.request(self.request.method.lower(),
                                    self._get_target_url(),
                                    params=self.request.params,
                                    data=self.request.body,
                                    headers=self.request.headers)

        data = self._replace_portal_url(response.raw.read())

        return Response(body=data,
                        status=response.status_code)

    def _get_target_url(self):
        baseurl = self._get_client().internal_url
        if baseurl.endswith('/'):
            baseurl = baseurl[:-1]

        subpath = self.request.path
        if subpath.startswith('/'):
            subpath = subpath[1:]

        # remove view name and bridge client part
        subpath = '/'.join(subpath.split('/')[2:])

        return baseurl + '/' + subpath

    def _get_client(self):
        if self._client is None:
            subpath = self.request.path
            if subpath.startswith('/'):
                subpath = subpath[1:]

            # 0 = "proxy", 1 = clientid, 2+ = path on client
            clientid = subpath.split('/')[1]

            manager = getUtility(IClientManager)
            self._client = manager.get_client_by_id(clientid)
        return self._client

    def _replace_portal_url(self, data):
        public_url = self._client.public_url
        if not public_url.endswith('/'):
            public_url = public_url + '/'
        return data.replace(PORTAL_URL_PLACEHOLDER, public_url)
