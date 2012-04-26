from ftw.bridge.proxy.testing import PYRAMID_LAYER
from ftw.bridge.proxy.views import StatusCheckView
from pyramid.testing import DummyRequest
from unittest2 import TestCase


class TestManageView(TestCase):

    layer = PYRAMID_LAYER

    def test_view_returns_ok(self):
        request = DummyRequest()
        response = StatusCheckView(request)()
        self.assertEqual(response.body, 'OK')
        self.assertEqual(response.status, '200 OK')
