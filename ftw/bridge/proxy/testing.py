from plone.testing import Layer
from pyramid import testing
import pyramid_zcml


class PyramidLayer(Layer):

    def setUp(self):
        settings = {
            'clients.foo.aliases': 'foo2',
            'clients.foo.ip_addresses': '127.0.0.1',
            'clients.foo.internal_url': 'http://127.0.0.1:8080/foo/',
            'clients.foo.public_url': 'http://localhost:8080/foo/',

            'clients.bar.ip_addresses': '127.0.0.1, 127.0.0.3',
            'clients.bar.internal_url': 'http://127.0.0.1:9080/bar/',
            'clients.bar.public_url': 'http://localhost:9080/bar/',

            'bridge.admin.username': 'chef',
            'bridge.admin.password': '1234',
            }

        self.config = testing.setUp(hook_zca=True, settings=settings)
        self.config.include(pyramid_zcml)
        self.config.load_zcml('ftw.bridge.proxy:configure.zcml')

    def tearDown(self):
        testing.tearDown()


PYRAMID_LAYER = PyramidLayer()
