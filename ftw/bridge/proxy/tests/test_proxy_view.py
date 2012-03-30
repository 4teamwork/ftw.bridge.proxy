from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.proxy import Proxy
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from ftw.bridge.proxy.views import ProxyView
from mocker import ANY, MockerTestCase
from mocker import ARGS, KWARGS
from pyramid.exceptions import Forbidden
from pyramid.interfaces import IRequest
from pyramid.interfaces import IResponse
from pyramid.response import Response
from pyramid.testing import DummyRequest
from pyramid.threadlocal import get_current_registry


class TestProxyView(MockerTestCase):

    layer = PYRAMID_LAYER

    def setUp(self):
        MockerTestCase.setUp(self)

        # we do not expect requests, but lets just prevent accidental requests
        self.requests = self.mocker.replace('requests')
        self.expect(self.requests.request(ARGS, KWARGS)).count(0)

        self.proxy = self.mocker.mock(Proxy, count=False)
        ProxyMock = self.mocker.mock(count=False)
        self.expect(ProxyMock(ANY)).result(self.proxy)

        sm = get_current_registry()
        sm.registerAdapter(ProxyMock, [IRequest], IProxy, name='')

    def test_proxy_view_authorizes(self):
        request = DummyRequest(
            path='/proxy/foo/remote/path/@@view',
            headers={})

        self.mocker.replay()
        view = ProxyView(request)
        with self.assertRaises(Forbidden):
            view.__call__()

    def test_proxy_view(self):
        request = DummyRequest(
            path='/proxy/foo/remote/path/@@view',
            params={'foo': 'bar'},
            headers={'X-BRIDGE-ORIGIN': 'bar',
                     'X-BRIDGE-AC': 'john.doe'},
            environ={'REMOTE_ADDR': '127.0.0.1'})

        self.expect(self.proxy()).result(Response('proxied response'))
        self.mocker.replay()

        view = ProxyView(request)
        response = view.__call__()
        self.assertTrue(IResponse.providedBy(response))
        self.assertEqual(response.body, 'proxied response')
