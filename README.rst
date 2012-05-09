Introduction
============

``ftw.bridge.proxy`` is a small pyramid based web application for proxying
requests between multiple plone instances. It's purpose is to isolate the
plone instances by routing through this proxy. This allows to easily move
plone instances to other servers.


Maintenance mode
----------------

Each configured client (plone site) can be switched into maintenance mode on
the bridge. When maintenance mode is enabled, the bridge answers every
request to this client with a HTTP 503 (Service Unavailable).

The maintenance mode can be enabled in the manage view of the bridge
(``/manage``).


Installing the bridge
---------------------

Install pyramid and ``ftw.bridge.proxy`` and configure the bridge in the
pyramid ``.ini`` configuration file::

    [app:main]
    use = egg:ftw.bridge.proxy

    clients.intranet.aliases = dashboard
    clients.intranet.ip_addresses = 127.0.0.1
    clients.intranet.internal_url = http://127.0.0.1:8080/intranet/
    clients.intranet.public_url = http://intranet.com/

    clients.otherapp.ip_addresses = 192.168.1.10
    clients.otherapp.internal_url = http://192.168.1.10:8080/platform/
    clients.otherapp.public_url = http://otherapp.intranet.com/

    bridge.admin.username = admin
    bridge.admin.password = secret


Installing the plone addon
--------------------------

For interacting with the bridge there is a plone addon package named
`ftw.bridge.client`_, providing a PAS plugin for authenticating requests
from the bridge and providing tools for making requests. See the readme of
`ftw.bridge.client`_ for more details.


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.bridge.proxy
- Issue tracker: https://github.com/4teamwork/ftw.bridge.proxy/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.bridge.proxy
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.bridge.proxy


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.bridge.proxy`` is licensed under GNU General Public License, version 2.

.. _ftw.bridge.client: https://github.com/4teamwork/ftw.bridge.client
