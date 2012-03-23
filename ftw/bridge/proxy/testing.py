from plone.testing import Layer
from pyramid import testing


class PyramidLayer(Layer):

    def setUp(self):
        self.config = testing.setUp()
        # settings = self.config.registry.settings
        # settings['izug.portal_url'] = 'http://localhost:9080/izug/platform'
        # settings['izug.ip_address'] = '127.0.0.1'

    def tearDown(self):
        testing.tearDown()


PYRAMID_LAYER = PyramidLayer()
