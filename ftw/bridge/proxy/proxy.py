from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
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

        return Response(body=response.raw,
                        status=response.status_code)

    def _get_target_url(self):
        baseurl = self._get_client().internal_url
        if baseurl.endswith('/'):
            baseurl = baseurl[:-1]

        subpath = self.request.path
        if subpath.startswith('/'):
            subpath = subpath[1:]

        # remove bridge client part
        subpath = '/'.join(subpath.split('/')[1:])

        return baseurl + '/' + subpath

    def _get_client(self):
        if self._client is None:
            subpath = self.request.path
            if subpath.startswith('/'):
                subpath = subpath[1:]

            clientid = subpath.split('/')[0]

            manager = getUtility(IClientManager)
            self._client = manager.get_client_by_id(clientid)
        return self._client
