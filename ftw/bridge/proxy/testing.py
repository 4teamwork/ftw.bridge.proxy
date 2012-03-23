from plone.testing import Layer
from pyramid import testing
import pyramid_zcml


class PyramidLayer(Layer):

    def setUp(self):
        self.config = testing.setUp(hook_zca=True)
        self.config.include(pyramid_zcml)
        self.config.load_zcml('ftw.bridge.proxy:configure.zcml')

    def tearDown(self):
        testing.tearDown()


PYRAMID_LAYER = PyramidLayer()
