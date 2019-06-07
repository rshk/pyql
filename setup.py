import os
from setuptools import setup, find_packages

version = '0.2.9'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

if os.path.exists('CHANGELOG.rst'):
    with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
        longdesc += "\n\n" + fp.read()


INSTALL_REQUIRES = [

    # GraphQL schema definition
    'graphql-core',

    # ISO8601 date parsing
    'aniso8601',
]


EXTRAS_REQUIRE = {
    'sanic': {
        'sanic >= 0.7.0',
        'sanic-graphql',
        'sanic-cors >= 0.9.4',
        'graphene >= 2.0',
        'graphql-ws >= 0.2.0',
    },
    'flask': {
        'flask',
        'flask-graphql',
        'graphql-core',
    },
    'dev': [
        'pytest',
        'pytest-cov',
        'sphinx',
    ],
}


DEPENDENCY_LINKS = [
    'http://github.com/channelcat/sanic/tarball/30e6a310f132752669a74927530e8bc52a51e98e#egg=sanic-0.7.0',
    'http://github.com/graphql-python/graphql-ws/tarball/660a0e0d6de66416e57179c2633795de5823d347#egg=graphql-ws-0.2.0',
    'https://github.com/ashleysommer/sanic-cors/tarball/a17067967e0d447c870c48feca9cc53572316c3c#egg=sanic-cors-0.9.4',
]


setup(
    name='PyQL',
    version=version,
    packages=find_packages(),
    url='https://github.com/rshk/pyql',
    license='BSD License',
    author='Samuele Santi',
    author_email='samuele.santi@reinventsoftware.io',
    description='',
    long_description=longdesc,
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    extras_require=EXTRAS_REQUIRE,
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',

        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # 'Programming Language :: Python :: Implementation :: Stackless',
    ],
    # entry_points={
    #     'console_scripts': ['PACKAGE_NAME=PACKAGE_NAME.cli:main'],
    # },
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
