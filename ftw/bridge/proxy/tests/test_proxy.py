from StringIO import StringIO
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.interfaces import IProxy
from ftw.bridge.proxy.interfaces import PORTAL_URL_PLACEHOLDER
from ftw.bridge.proxy.proxy import Proxy
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from mocker import ARGS, KWARGS
from mocker import MockerTestCase
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.interfaces import IResponse
from pyramid.testing import DummyRequest
from requests.models import Response
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface.verify import verifyClass


class TestProxy(MockerTestCase):

    layer = PYRAMID_LAYER

    def setUp(self):
        MockerTestCase.setUp(self)

        self.requests = self.mocker.replace('requests')
        # this mocks any unexpected request:
        self.expect(self.requests.request(ARGS, KWARGS)).count(0)

    def test_component_is_registered(self):
        self.mocker.replay()

        request = DummyRequest()
        proxy = queryAdapter(request, IProxy)
        self.assertNotEqual(proxy, None)

    def test_implements_interface(self):
        self.mocker.replay()

        self.assertTrue(IProxy.implementedBy(
                Proxy))
        verifyClass(IProxy, Proxy)

    def test_GET_request(self):
        request = DummyRequest(
            path='/proxy/bar/remote/path/@@view',
            params={'foo': 'bar'},
            headers={'X-BRIDGE-ORIGIN': 'foo',
                     'X-BRIDGE-AC': 'john.doe'})

        response = Response()
        response.status_code = 200
        response.raw = StringIO('the response data')

        self.expect(self.requests.request(
                'get',
                'http://127.0.0.1:9080/bar/remote/path/@@view',
                params={'foo': 'bar'},
                data='',
                headers={'X-BRIDGE-ORIGIN': 'foo',
                         'X-BRIDGE-AC': 'john.doe'})).result(
            response)

        self.mocker.replay()
        proxy = queryAdapter(request, IProxy)

        response = proxy()
        self.assertTrue(IResponse.providedBy(response))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'the response data')

    def test_POST_request(self):
        request = DummyRequest(
            path='/proxy/foo/remote/path/@@view',
            params={'foo': 'bar'},
            headers={'X-BRIDGE-ORIGIN': 'bar',
                     'X-BRIDGE-AC': 'john.doe'},
            post=True)
        request.body = '{"some": "data"}'

        response = Response()
        response.status_code = 200
        response.raw = StringIO('the response data')

        self.expect(self.requests.request(
                'post',
                'http://127.0.0.1:8080/foo/remote/path/@@view',
                params={'foo': 'bar'},
                data='{"some": "data"}',
                headers={'X-BRIDGE-ORIGIN': 'bar',
                         'X-BRIDGE-AC': 'john.doe'})).result(
            response)

        self.mocker.replay()
        proxy = queryAdapter(request, IProxy)

        response = proxy()
        self.assertTrue(IResponse.providedBy(response))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'the response data')

    def test_client_unavailable(self):
        clientmanager = getUtility(IClientManager)
        foo = clientmanager.get_client_by_id('foo')
        foo.set_maintenance_mode(True)

        request = DummyRequest(
            path='/proxy/foo/remote/path/@@view',
            params={'foo': 'bar'},
            headers={'X-BRIDGE-ORIGIN': 'bar',
                     'X-BRIDGE-AC': 'john.doe'})

        self.mocker.replay()

        proxy = queryAdapter(request, IProxy)

        with self.assertRaises(HTTPServiceUnavailable):
            proxy()

        foo.set_maintenance_mode(False)

    def test_proxy_replaces_portal_url(self):
        request = DummyRequest(
            path='/proxy/bar/remote/path/@@view',
            params={'foo': 'bar'},
            headers={'X-BRIDGE-ORIGIN': 'foo',
                     'X-BRIDGE-AC': 'john.doe'})

        response = Response()
        response.status_code = 200
        response.raw = StringIO(
            'response containing %s as a portal url placeholder.' % (
                PORTAL_URL_PLACEHOLDER))

        self.expect(self.requests.request(
                'get',
                'http://127.0.0.1:9080/bar/remote/path/@@view',
                params={'foo': 'bar'},
                data='',
                headers={'X-BRIDGE-ORIGIN': 'foo',
                         'X-BRIDGE-AC': 'john.doe'})).result(
            response)

        self.mocker.replay()
        proxy = queryAdapter(request, IProxy)

        response = proxy()
        self.assertTrue(IResponse.providedBy(response))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(
            response.body,
            'response containing http://localhost:9080/bar/ as a portal '
            'url placeholder.')
