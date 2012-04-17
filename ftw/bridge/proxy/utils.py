from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.interfaces import IRequest
from pyramid.interfaces import ISettings
from zope.component import getUtility


def protected(fun):
    """Decorator for protecting a view, so that basic authentication with the
    configured admin user is required.
    """

    def _authorize(*args, **kwargs):
        login_required = HTTPUnauthorized()
        login_required.headers['WWW-Authenticate'] = \
            'Basic realm="Manage bridge"'

        if IRequest.providedBy(args[0]):
            request = args[0]
        else:
            request = args[0].request

        authorization = request.headers.get('Authorization', None)
        if not authorization:
            raise login_required

        _basic, authorization = authorization.split(' ', 1)
        username, password = authorization.decode('base64').split(':', 1)

        settings = getUtility(ISettings)
        admin_user = settings.get('bridge.admin.username', object())
        admin_pass = settings.get('bridge.admin.password', object())

        if username != admin_user or password != admin_pass:
            raise login_required

        return fun(*args, **kwargs)

    return _authorize
