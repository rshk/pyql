import os
from setuptools import setup, find_packages

version = '0.1'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

if os.path.exists('CHANGELOG.rst'):
    with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
        longdesc += "\n\n" + fp.read()


INSTALL_REQUIRES = [
    'sanic >= 0.7.0',
    'sanic-graphql',
    'graphene >= 2.0',
    'graphql-ws >= 0.2.0',
]

DEPENDENCY_LINKS = [
    'http://github.com/channelcat/sanic/tarball/30e6a310f132752669a74927530e8bc52a51e98e#egg=sanic-0.7.0',
    'http://github.com/graphql-python/graphql-ws/tarball/660a0e0d6de66416e57179c2633795de5823d347#egg=graphql-ws-0.2.0',
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
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: BSD License',

        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 2 :: Only',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',
        # 'Programming Language :: Python :: 3.1',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
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
