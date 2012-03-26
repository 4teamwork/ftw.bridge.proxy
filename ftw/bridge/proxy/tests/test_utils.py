from ftw.bridge.proxy.testing import PYRAMID_LAYER
from ftw.bridge.proxy.utils import protected
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.testing import DummyRequest
from unittest2 import TestCase


@protected
def example_view(request):
    return request


class ExampleView(object):

    def __init__(self, request):
        self.request = request

    @protected
    def __call__(self):
        return self.request


class TestProtectedDecorator(TestCase):

    layer = PYRAMID_LAYER

    def test_protected_function_raises_unauthorized_when_called(self):
        request = DummyRequest()

        with self.assertRaises(HTTPUnauthorized) as cm:
            example_view(request)

        exc = cm.exception
        self.assertEqual(exc.headers.get('WWW-Authenticate'),
                         'Basic realm="Manage bridge"')

    def test_protected_method_raises_unauthorized_when_called(self):
        request = DummyRequest()

        with self.assertRaises(HTTPUnauthorized) as cm:
            ExampleView(request)()

        exc = cm.exception
        self.assertEqual(exc.headers.get('WWW-Authenticate'),
                         'Basic realm="Manage bridge"')

    def test_protected_function_with_valid_credentials(self):
        request = DummyRequest(headers={
                'Authorization': 'Basic %s' % 'chef:1234'.encode('base64')})

        self.assertEqual(example_view(request), request)

    def test_protected_method_with_valid_credentials(self):
        request = DummyRequest(headers={
                'Authorization': 'Basic %s' % 'chef:1234'.encode('base64')})

        self.assertEqual(ExampleView(request)(), request)

    def test_protected_function_with_invalid_credentials(self):
        request = DummyRequest(headers={
                'Authorization': 'Basic %s' % 'hacker:hack'.encode('base64')})

        with self.assertRaises(HTTPUnauthorized) as cm:
            example_view(request)

        exc = cm.exception
        self.assertEqual(exc.headers.get('WWW-Authenticate'),
                         'Basic realm="Manage bridge"')

    def test_protected_method_with_invalid_credentials(self):
        request = DummyRequest(headers={
                'Authorization': 'Basic %s' % 'hacker:hack'.encode('base64')})

        with self.assertRaises(HTTPUnauthorized) as cm:
            ExampleView(request)()

        exc = cm.exception
        self.assertEqual(exc.headers.get('WWW-Authenticate'),
                         'Basic realm="Manage bridge"')
