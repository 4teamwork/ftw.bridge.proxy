# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Attribute
from zope.interface import Interface


PORTAL_URL_PLACEHOLDER = '***portal_url***'


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

    def is_authorized(client):
        """Returns `True` if the request is authorized, otherwise ``False``.
        The origin ``client`` info is passed as dict.
        """


class IClientManager(Interface):
    """The client manager utility provides information about configured
    clients.
    """

    def get_clients():
        """Returns a list of clients. Each client is represented as dict.
        """

    def get_client_by_id(clientid):
        """Returns the dict of a client configuration.
        """


class IClient(Interface):
    """Represents a client configuration. Clients are managed by the
    ``IClientManager``.

    The configuration is read from the pyramid configuration file (ini).
    """

    clientid = Attribute('ID of the client.')
    aliases = Attribute('List of alias clientids of this client.')
    ip_addresses = Attribute('IP addresses of this client for authorization.')
    internal_url = Attribute(
        'URL which the bridge uses to contact the client internally.')
    public_url = Attribute('URL for user redirection, not used internally.')

    def __init__(clientid, ip_addresses, internal_url, public_url,
                 aliases=None):
        """Creates a new client object.
        """

    def is_in_maintenance_mode():
        """Returns ``True`` if the client is in maintenance mode, otherwise
        ``False``.
        """

    def set_maintenance_mode(offline):
        """Sets the maintenance mode for this client.
        """


class IProxy(Interface):
    """The proxy adapter adapts ``request`` and ``client``. It creates the
    request to the adapted target client and proxies the data from the
    request.
    """

    def __init__(request):
        """
        Attributes:
        ``request`` -- the incoming request to be passed.
        """

    def __call__():
        """Executes the request to the target client and returns its response.
        """
