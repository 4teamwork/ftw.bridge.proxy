from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IAuthorizationPlugin
from pyramid.exceptions import Forbidden
from pyramid.interfaces import IRequest
from zope.component import adapts
from zope.interface import implements


class AuthorizationManager(object):
    implements(IAuthorizationManager)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request

    def authorize(self):
        raise Forbidden()


class DefaultAuthorizationPlugin(object):
    implements(IAuthorizationPlugin)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request

    def is_authorized(self):
        return True
