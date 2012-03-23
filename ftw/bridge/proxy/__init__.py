from pyramid.config import Configurator


def main(global_config, **settings):
    """Sets up the pyramid application.
    """
    config = Configurator(settings=settings)
    return config.make_wsgi_app()
