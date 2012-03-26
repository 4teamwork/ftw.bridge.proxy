# pylint: disable=W0212
# W0212: Access to a protected member of a client class

from ftw.bridge.proxy.authorization import AuthorizationManager
from ftw.bridge.proxy.authorization import DefaultAuthorizationPlugin
from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IAuthorizationPlugin
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from mocker import Mocker, expect
from pyramid.exceptions import Forbidden
from pyramid.testing import DummyRequest
from pyramid.threadlocal import get_current_registry
from unittest2 import TestCase
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class TestAuthorizationManager(TestCase):

    layer = PYRAMID_LAYER

    def test_component_is_registered(self):
        request = DummyRequest()
        manager = queryAdapter(request, IAuthorizationManager)
        self.assertNotEqual(manager, None)

    def test_implements_interface(self):
        self.assertTrue(IAuthorizationManager.implementedBy(
                AuthorizationManager))
        verifyClass(IAuthorizationManager, AuthorizationManager)

    def test_authorize_raises_forbidden_on_bad_request(self):
        request = DummyRequest()
        manager = queryAdapter(request, IAuthorizationManager)

        with self.assertRaises(Forbidden):
            manager.authorize()

    def test_get_authorization_plugin(self):
        request = DummyRequest()
        manager = queryAdapter(request, IAuthorizationManager)
        plugin = manager._get_authorization_plugin('unkown')
        self.assertNotEqual(plugin, None)
        self.assertEqual(type(plugin), DefaultAuthorizationPlugin)

    def test_get_client(self):
        request = DummyRequest(headers={'X-BRIDGE-ORIGIN': 'foo'})
        manager = queryAdapter(request, IAuthorizationManager)
        client = manager._get_client()
        self.assertNotEqual(client, None)
        self.assertEqual(client.clientid, 'foo')

    def test_get_client_with_invalid_request(self):
        request = DummyRequest()
        manager = queryAdapter(request, IAuthorizationManager)

        with self.assertRaises(Forbidden):
            manager._get_client()

    def test_get_client_with_unkown_origin(self):
        request = DummyRequest(headers={'X-BRIDGE-ORIGIN': 'unkown'})
        manager = queryAdapter(request, IAuthorizationManager)

        with self.assertRaises(Forbidden):
            manager._get_client()

    def test_authorize_raises_forbidden_when_plugin_returns_False(self):
        clientmanager = getUtility(IClientManager)
        client = clientmanager.get_client_by_id('foo')
        mocker = Mocker()
        request = DummyRequest(headers={'X-BRIDGE-ORIGIN': 'foo'})

        plugin = mocker.mock()
        expect(plugin(request)).result(plugin)
        expect(plugin.is_authorized(client)).result(False)
        sm = get_current_registry()
        sm.registerAdapter(plugin, [Interface], IAuthorizationPlugin,
                           name='foo', event=False)

        mocker.replay()

        manager = queryAdapter(request, IAuthorizationManager)
        with self.assertRaises(Forbidden):
            manager.authorize()

        mocker.restore()
        mocker.verify()

    def test_authorized_when_plugin_returns_True(self):
        clientmanager = getUtility(IClientManager)
        client = clientmanager.get_client_by_id('foo')
        mocker = Mocker()
        request = DummyRequest(headers={'X-BRIDGE-ORIGIN': 'foo'})

        plugin = mocker.mock()
        expect(plugin(request)).result(plugin)
        expect(plugin.is_authorized(client)).result(True)
        sm = get_current_registry()
        sm.registerAdapter(plugin, [Interface], IAuthorizationPlugin,
                           name='foo', event=False)

        mocker.replay()

        manager = queryAdapter(request, IAuthorizationManager)
        self.assertTrue(manager.authorize())

        mocker.restore()
        mocker.verify()


class TestDefaultAuthorization(TestCase):

    layer = PYRAMID_LAYER

    def setUp(self):
        clientmanager = getUtility(IClientManager)
        self.client_foo = clientmanager.get_client_by_id('foo')

    def test_component_is_registered(self):
        request = DummyRequest()
        auth = queryAdapter(request, IAuthorizationPlugin)
        self.assertNotEqual(auth, None)

    def test_implements_interface(self):
        self.assertTrue(IAuthorizationPlugin.implementedBy(
                DefaultAuthorizationPlugin))
        verifyClass(IAuthorizationPlugin, DefaultAuthorizationPlugin)

    def test_is_authorized_from_bad_ip_address(self):
        request = DummyRequest(
            headers={'X-BRIDGE-ORIGIN': 'foo'},
            environ={'REMOTE_ADDR': '192.168.1.1'})
        auth = queryAdapter(request, IAuthorizationPlugin)

        self.assertFalse(auth.is_authorized(self.client_foo))

    def test_is_authorized_from_correct_ip(self):
        request = DummyRequest(
            headers={'X-BRIDGE-ORIGIN': 'foo'},
            environ={'REMOTE_ADDR': '127.0.0.1'})
        auth = queryAdapter(request, IAuthorizationPlugin)

        self.assertTrue(auth.is_authorized(self.client_foo))

    def test_is_authorized_from_bad_proxy_ip(self):
        request = DummyRequest(
            headers={'X-BRIDGE-ORIGIN': 'foo'},
            environ={'REMOTE_ADDR': '127.0.0.1',
                     'HTTP_X_FORWARDED_FOR': '192.168.1.1'})
        auth = queryAdapter(request, IAuthorizationPlugin)

        self.assertFalse(auth.is_authorized(self.client_foo))

    def test_is_authorized_multi_proxied_ip(self):
        request = DummyRequest(
            headers={'X-BRIDGE-ORIGIN': 'foo'},
            environ={'REMOTE_ADDR': '192.168.1.1',
                     'HTTP_X_FORWARDED_FOR': '127.0.0.1, 192.168.10.10'})
        auth = queryAdapter(request, IAuthorizationPlugin)

        self.assertTrue(auth.is_authorized(self.client_foo))

    def test_is_authorized_without_remote_address(self):
        request = DummyRequest()
        auth = queryAdapter(request, IAuthorizationPlugin)

        self.assertFalse(auth.is_authorized(self.client_foo))
