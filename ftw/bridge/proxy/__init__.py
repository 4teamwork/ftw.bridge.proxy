from pyramid.config import Configurator
import pyramid_zcml


def main(global_config, **settings):
    """Sets up the pyramid application.
    """
    config = Configurator(settings=settings)
    config.include(pyramid_zcml)
    config.hook_zca()
    config.load_zcml('configure.zcml')

    return config.make_wsgi_app()
