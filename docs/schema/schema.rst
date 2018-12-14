Schema definition
#################

To define a schema, simply create an instance of ``pywl.Schema``:

.. code-block:: python

    from pyql import Object, Schema

    schema = Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription)

You can pass your root query / mutation / subscription objects as
arguments to the ``Schema`` constructor.

.. warning::

   You **must** provide a root query object, and it must have at least
   one field. This requirement is enforced by ``graphql-core``.


Passing extra types
===================

If you are using :doc:`interfaces <interfaces>`, chances are you're
only using your interface type in the schema definition (so the
concrete types are not reachable from the root object).

If that's the case, you must pass them explicitly to the schema constructor:

.. code-blocK:: python

    from pyql import Object, Interface, Schema

    Character = Interface('Character', ...)
    Human = Object('Human', interfaces=[Character], ...)
    Droid = Object('Droid', interfaces=[Character], ...)

    schema = Schema(..., types=[Human, Droid])

.. note::

   This is likely not going to be necessary in a future version, as
   we're planning to track concrete objects using a given interface,
   so we can resolve them automatically behind the scenes.


Example schema definition
=========================

.. code-block:: python

    from pyql import Object, Schema

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, argument: str = 'stranger') -> str:
        return 'Hello ' + argument

    schema = Schema(query=Query)


Compilation
===========

To convert a ``pyql.Schema`` instance to a schema that's understood by
``graphql-core``, you need to compile it:


.. code-block:: python

    compiled = schema.compile()


Now you can use it, eg:

.. code-block:: python

    from graphql import graphql

    result = graphql(compiled, '{yourQuery}', ...)


Execution
=========

For convenience, we provide a ``schema.execute()`` method to quickly
run queries against the schema. This is especially useful during
testing:

.. code-block:: python

    schema.execute("""
    query foo($arg: String) {
        bar (arg: $arg) {
            baz, quux
        }
    }
    """, variables={'arg': 'VALUE'})


Behind the scenes, it will compile the schema and call ``graphql()``.

Return value is an object with ``errors`` and ``data`` attributes.
