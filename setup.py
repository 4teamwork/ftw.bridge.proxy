from setuptools import setup, find_packages
import os

version = '1.1'
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.testing',
    'mocker',
    'unittest2',
    ]

extras_require = {
    'tests': tests_require,
    }

setup(name='ftw.bridge.proxy',
      version=version,
      description='A pyramid based proxy application for proxying ' + \
          'requests between plone instances.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Pylons',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        ],

      keywords='ftw bridge proxy requests',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.bridge.proxy',
      license='GPL2',

      packages=find_packages(),
      namespace_packages=['ftw', 'ftw.bridge'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'setuptools',
          'pyramid',
          'pyramid_zcml',
          'zope.component',
          'requests',
      ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points='''
      # -*- Entry points: -*-
      [paste.app_factory]
      main = ftw.bridge.proxy:main
      ''',
      )
