from ftw.bridge.proxy.client import ClientManager
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.testing import CLIENT_BAR
from ftw.bridge.proxy.testing import CLIENT_FOO
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from pyramid.testing import DummyRequest
from unittest2 import TestCase
from zope.component import queryAdapter
from zope.interface.verify import verifyClass


class TestClientManager(TestCase):

    layer = PYRAMID_LAYER

    def test_component_is_registered(self):
        request = DummyRequest()
        manager = queryAdapter(request, IClientManager)
        self.assertNotEqual(manager, None)

    def test_implements_interface(self):
        self.assertTrue(IClientManager.implementedBy(
                ClientManager))
        verifyClass(IClientManager, ClientManager)

    def test_get_clients(self):
        request = DummyRequest()
        manager = queryAdapter(request, IClientManager)

        expected_clients = {
            'foo': CLIENT_FOO,
            'bar': CLIENT_BAR}

        self.assertEqual(manager.get_clients(), expected_clients)

    def test_get_client_by_id(self):
        request = DummyRequest()
        manager = queryAdapter(request, IClientManager)

        self.assertEqual(manager.get_client_by_id('unkown'), None)
        self.assertEqual(manager.get_client_by_id('foo'), CLIENT_FOO)
        self.assertEqual(manager.get_client_by_id('foo2'), CLIENT_FOO)
        self.assertEqual(manager.get_client_by_id('foo3'), None)
        self.assertEqual(manager.get_client_by_id('bar'), CLIENT_BAR)
