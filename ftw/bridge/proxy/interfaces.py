from zope.interface import Interface


class IAuthorizationManager(Interface):
    """The authorization manager authorizes a request by delegating
    authorization to the ``IAuthorizationPlugin`` for the origin. If
    authorization fails a ``pyramid.exceptions.Forbidden`` is raised.
    """

    def __init__(request):
        """The ``IAuthorizationManager`` adapts the request.
        """

    def authorize():
        """Authorizes the request and raises a ``Forbidden`` exception if
        the request is not authorized.
        """


class IAuthorizationPlugin(Interface):
    """A adapter interface, adapting ``request``. A adapter with the name of
    the client will be looked up. If there is no such custom adapter, the
    fallback adapter (no name) is used.
    """

    def __init__(request):
        """The ``IAuthorizationPlugin`` adapts the ``request``.
        """

    def is_authorized():
        """Returns `True` if the request is authorized, otherwise ``False``.
        """