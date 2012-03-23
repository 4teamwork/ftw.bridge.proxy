from zope.interface import Interface


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
