Getting started
###############


Installation
============

Install from PyPi::

  pip install pyql


Defining a basic schema
=======================


.. code-block:: python

    from pyql import Schema

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info, argument: str = 'stranger') -> str:
        return 'Hello ' + argument


Or you can create your root Query object explicitly if you prefer doing so:

.. code-block:: python

    from pyql import Object, Schema

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, argument: str = 'stranger') -> str:
        return 'Hello ' + argument

    schema = Schema(query=Query)


Querying
========


.. code-block:: python

    result = schema.execute('{ hello }')
    print(result.data['hello']) # "Hello stranger"

    # Passing the argument as a variable
    result = schema.execute("""
    query hello($arg: String) {
        hello (argument: $arg)
    }
    """, variables={'arg': 'World'})
    print(result.data['hello']) # "Hello World"



Useful links
============

- `PyQL on PyPi <https://pypi.org/project/PyQL/>`_
- `PyQL source code on GitHub <https://github.com/rshk/pyql>`_
- `PyQL documentation <https://pyql-lib.readthedocs.io/en/latest/>`_
