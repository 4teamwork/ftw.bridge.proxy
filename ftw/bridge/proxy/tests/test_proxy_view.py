from StringIO import StringIO
from ftw.bridge.proxy import LOG
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.proxy import Proxy
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from ftw.bridge.proxy.views import ProxyView
from logging import DEBUG
from logging import Formatter
from logging import StreamHandler
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

        # we do not expect requests, but lets just prevent accidental
        # requests
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


class TestProxyViewLogging(MockerTestCase):

    layer = PYRAMID_LAYER

    def setUp(self):
        MockerTestCase.setUp(self)

        # we do not expect requests, but lets just prevent accidental
        # requests
        self.requests = self.mocker.replace('requests')
        self.expect(self.requests.request(ARGS, KWARGS)).count(0)

        self.proxy = self.mocker.mock(Proxy, count=False)
        ProxyMock = self.mocker.mock(count=False)
        self.expect(ProxyMock(ANY)).result(self.proxy)

        sm = get_current_registry()
        sm.registerAdapter(ProxyMock, [IRequest], IProxy, name='')

        self.stream = StringIO()
        self.handler = StreamHandler(self.stream)
        self.handler.setFormatter(Formatter('%(levelname)s %(message)s'))
        LOG.addHandler(self.handler)
        self.ori_log_level = LOG.getEffectiveLevel()
        LOG.setLevel(DEBUG)

    def tearDown(self):
        LOG.removeHandler(self.handler)
        LOG.setLevel(self.ori_log_level)

    def read_log(self):
        self.stream.seek(0)
        data = self.stream.read()
        self.stream.seek(0)
        return data

    def test_normal_request_logged(self):
        url = 'http://bridge/proxy/foo/remote/path/@@view'
        request = DummyRequest(
            url=url,
            path='/proxy/foo/remote/path/@@view',
            headers={'X-BRIDGE-ORIGIN': 'bar',
                     'X-BRIDGE-AC': 'john.doe'},
            environ={'REMOTE_ADDR': '127.0.0.1'})

        self.expect(self.proxy()).result(Response('proxied response'))
        self.mocker.replay()

        view = ProxyView(request)
        response = view.__call__()
        self.assertEqual(response.body, 'proxied response')
        self.assertEqual(
            self.read_log().strip(),
            'INFO GET: "bar" 200 OK (%s)' % url)

    def test_forbidden_request_logged(self):
        url = 'http://bridge/proxy/foo/remote/path/@@view'
        request = DummyRequest(
            url=url,
            headers={'X-BRIDGE-ORIGIN': 'wrong-client',
                     'X-BRIDGE-AC': 'john.doe'})

        self.expect(self.proxy()).result(Response('proxied response'))
        self.mocker.replay()

        view = ProxyView(request)
        with self.assertRaises(Forbidden):
            view()

        self.assertEqual(
            self.read_log().strip(),
            'ERROR GET: "wrong-client" FAILED (%s): ' % url + \
                'HTTPForbidden: Access was denied to this resource.')
