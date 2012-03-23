from ftw.bridge.proxy.interfaces import IAuthorizationPlugin
from pyramid.interfaces import IRequest
from zope.component import adapts
from zope.interface import implements


class DefaultAuthorizationPlugin(object):
    implements(IAuthorizationPlugin)
    adapts(IRequest)

    def __init__(self, request):
        self.request = request

    def is_authorized(self):
        return True
