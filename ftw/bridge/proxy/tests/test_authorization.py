from ftw.bridge.proxy.authorization import DefaultAuthorizationPlugin
from ftw.bridge.proxy.interfaces import IAuthorizationPlugin
from ftw.bridge.proxy.testing import PYRAMID_LAYER
from pyramid.testing import DummyRequest
from unittest2 import TestCase
from zope.component import queryAdapter
from zope.interface.verify import verifyClass


class TestDefaultAuthorization(TestCase):

    layer = PYRAMID_LAYER

    def test_component_is_registered(self):
        request = DummyRequest()
        auth = queryAdapter(request, IAuthorizationPlugin)
        self.assertNotEqual(auth, None)

    def test_implements_interface(self):
        self.assertTrue(IAuthorizationPlugin.implementedBy(
                DefaultAuthorizationPlugin))
        verifyClass(IAuthorizationPlugin, DefaultAuthorizationPlugin)
