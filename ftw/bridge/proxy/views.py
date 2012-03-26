from ftw.bridge.proxy.interfaces import IAuthorizationManager
from ftw.bridge.proxy.interfaces import IProxy


class ProxyView(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        IAuthorizationManager(self.request).authorize()
        return IProxy(self.request)()
