import os
from setuptools import setup, find_packages

version = '3.0.0'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

if os.path.exists('CHANGELOG.rst'):
    with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
        longdesc += "\n\n" + fp.read()


INSTALL_REQUIRES = [

    # GraphQL schema definition
    'graphql-core >= 3',

    # ISO8601 date parsing
    'aniso8601',
]


EXTRAS_REQUIRE = {
    'dev': [
        'pytest',
        'pytest-cov',
        'sphinx',
        'pdbpp',
    ],
}


DEPENDENCY_LINKS = []


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
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    # entry_points={
    #     'console_scripts': ['PACKAGE_NAME=PACKAGE_NAME.cli:main'],
    # },
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
