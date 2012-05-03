from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.interfaces import PORTAL_URL_PLACEHOLDER
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.interfaces import IRequest
from pyramid.response import Response
from webob.multidict import NestedMultiDict
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
import requests
import types


def replace_placeholder_in_data(data, public_url):
    if isinstance(data, types.StringTypes):
        return data.replace(PORTAL_URL_PLACEHOLDER, public_url)

    elif isinstance(data, (types.DictType, NestedMultiDict)):
        for key, value in data.items():
            data[key] = replace_placeholder_in_data(value, public_url)
        return data

    elif isinstance(data, (types.ListType, types.TupleType)):
        new = []
        for value in data:
            new.append(replace_placeholder_in_data(value, public_url))
        return new

    else:
        return data


class Proxy(object):
    implements(IProxy)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request
        self._target_client = None
        self._source_client = None

    def __call__(self):
        if self._get_target_client().is_in_maintenance_mode():
            raise HTTPServiceUnavailable()

        params = dict(self.request.params)

        replace_placeholder_in_data(
            params, self._get_source_client().get_public_url())

        kwargs = {'headers': self.request.headers}
        if self.request.method.lower() == 'get':
            kwargs['params'] = params
        else:
            kwargs['data'] = params

        response = requests.request(self.request.method.lower(),
                                    self._get_target_url(),
                                    **kwargs)

        body = response.raw.read().replace(
            PORTAL_URL_PLACEHOLDER,
            self._get_target_client().get_public_url())

        headers = dict(response.headers)
        if 'content-length' in headers:
            del headers['content-length']

        proxy_response = Response(body=body,
                                  status=response.status_code)
        proxy_response.headers.update(headers)
        return proxy_response

    def _get_target_url(self):
        baseurl = self._get_target_client().get_internal_url()
        if baseurl.endswith('/'):
            baseurl = baseurl[:-1]

        subpath = self.request.path
        if subpath.startswith('/'):
            subpath = subpath[1:]

        # remove view name and bridge client part
        subpath = '/'.join(subpath.split('/')[2:])

        return baseurl + '/' + subpath

    def _get_target_client(self):
        if self._target_client is None:
            subpath = self.request.path
            if subpath.startswith('/'):
                subpath = subpath[1:]

            # 0 = "proxy", 1 = clientid, 2+ = path on client
            clientid = subpath.split('/')[1]

            manager = getUtility(IClientManager)
            self._target_client = manager.get_client_by_id(clientid)
        return self._target_client

    def _get_source_client(self):
        if self._source_client is None:
            manager = getUtility(IClientManager)
            client_id = self.request.headers.get('X-BRIDGE-ORIGIN')
            self._source_client = manager.get_client_by_id(client_id)
        return self._source_client
