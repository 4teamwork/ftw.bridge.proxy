from ftw.bridge.proxy.client import Client
from ftw.bridge.proxy.client import ClientManager
from ftw.bridge.proxy.interfaces import IClient
from ftw.bridge.proxy.interfaces import IClientManager
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from unittest2 import TestCase
from zope.component import queryUtility
from zope.interface.verify import verifyClass


class TestClientManager(TestCase):

    layer = PYRAMID_LAYER

    def test_component_is_registered(self):
        manager = queryUtility(IClientManager)
        self.assertNotEqual(manager, None)

    def test_implements_interface(self):
        self.assertTrue(IClientManager.implementedBy(
                ClientManager))
        verifyClass(IClientManager, ClientManager)

    def test_get_clients(self):
        manager = queryUtility(IClientManager)

        foo, bar = manager.get_clients()
        self.assertEqual(foo.clientid, 'foo')
        self.assertEqual(bar.clientid, 'bar')

    def test_get_client_by_id(self):
        manager = queryUtility(IClientManager)

        foo = manager.get_client_by_id('foo')
        self.assertTrue(IClient.providedBy(foo))
        self.assertEqual(foo.clientid, 'foo')
        self.assertEqual(manager.get_client_by_id('foo2'), foo)

        bar = manager.get_client_by_id('bar')
        self.assertTrue(IClient.providedBy(bar))
        self.assertEqual(bar.clientid, 'bar')

        self.assertEqual(manager.get_client_by_id('unkown'), None)
        self.assertEqual(manager.get_client_by_id('foo3'), None)

    def test_maintenance_persistent(self):
        manager = queryUtility(IClientManager)
        client = manager.get_client_by_id('foo')
        self.assertFalse(client.is_in_maintenance_mode())
        client.set_maintenance_mode(True)
        self.assertTrue(client.is_in_maintenance_mode())

        manager = queryUtility(IClientManager)
        client = manager.get_client_by_id('foo')
        self.assertTrue(client.is_in_maintenance_mode())
        client.set_maintenance_mode(False)
        self.assertFalse(client.is_in_maintenance_mode())


class TestClient(TestCase):

    def test_implements_interface(self):
        self.assertTrue(IClient.implementedBy(Client))
        verifyClass(IClient, Client)

    def test_attributes(self):
        client = Client('clientid',
                        ['ip', 'addresses'],
                        internal_url='http://internal/host',
                        public_url='http://public/host',
                        aliases=['otherid'])

        self.assertEqual(client.clientid, 'clientid')
        self.assertEqual(client.ip_addresses, ['ip', 'addresses'])
        self.assertEqual(client.internal_url, 'http://internal/host')
        self.assertEqual(client.public_url, 'http://public/host')
        self.assertEqual(client.aliases, ['otherid'])

    def test_maintenance_mode(self):
        client = Client('clientid',
                        ['ip', 'addresses'],
                        internal_url='http://internal/host',
                        public_url='http://public/host',
                        aliases=['otherid'])

        self.assertFalse(client.is_in_maintenance_mode())
        client.set_maintenance_mode(True)
        self.assertTrue(client.is_in_maintenance_mode())
        client.set_maintenance_mode(False)
        self.assertFalse(client.is_in_maintenance_mode())

    def test_get_public_url_has_trailing_slash(self):
        client = Client(None, None, None,
                        public_url='http://public/host')

        self.assertEquals(client.get_public_url(),
                          'http://public/host/')

        client = Client(None, None, None,
                        public_url='http://public/host/')

        self.assertEquals(client.get_public_url(),
                          'http://public/host/')

    def test_get_internal_url_has_trailing_slash(self):
        client = Client(None, None,
                        internal_url='http://internal/host',
                        public_url=None)

        self.assertEquals(client.get_internal_url(),
                          'http://internal/host/')

        client = Client(None, None,
                        internal_url='http://internal/host/',
                        public_url=None)

        self.assertEquals(client.get_internal_url(),
                          'http://internal/host/')
