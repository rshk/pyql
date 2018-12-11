#################
Schema definition
#################

One of the main goals of PyQL is providing a clean way of defining
GraphQL schemas.

In contrast with Graphene, we attempt at providing a cleaner schema
definition API, that also reduces ambiguity and verboseness. We
attempt to use existing facilities in Python as much as possible
(eg. type annotations).


Defining a basic schema
=======================

.. code-block:: python

    from pyql import Object, Schema

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, argument: str = 'stranger') -> str:
        return 'Hello ' + argument

    schema = Schema(query=Query)


Execution
=========

For convenience, we provide a ``schema.execute()`` method that can be
used for running GraphQL queries against the schema:

.. code-block:: python

    schema.execute("""
    query foo($arg: String) {
        bar (arg: $arg) {
            baz, quux
        }
    }
    """, variables={'arg': 'VALUE'})

To get a ``graphql-core`` compatible schema, simply call the
``schema.compile()`` method:


.. code-block:: python

    from graphql import graphql

    compiled = schema.compile()

    graphql(compiled, '{yourQuery}', ...)



Object definition
=================

Create an instance of ``pyql.Object``:

.. code-block:: python

    Example = Object(
        'Example',
        description='An example object',
        fields={
            'my_str': str,
            'my_int': int,
            'my_float': float,
            'my_bool': bool,
            'my_id': ID,
        })

.. note::

   Field names will be converted automatically from ``snake_case`` to
   ``camelCase`` for you, so you can use the right naming convention
   in your Python / JavaScript code.


Field from resolver
-------------------

You can define a field quickly by using the ``Object.field``
decorator. Field type and arguments will be picked up automatically by
inspecting type annotations:

.. code-block:: python

    Example = Object('Example')

    @Example.field('hello')
    def resolve_hello(root, info, name: str = 'stranger') -> str:
        return 'Hello ' + name


Python types will be converted automatically to ``GraphQL`` types.

If you need to use custom types, simply annotate your resolver accordingly.


Resolver returning object
-------------------------

``Object`` instances can be instantiated and treated as normal Python
objects.


.. code-block:: python

    Example = Object('Example', {'foo': str, 'bar': str})

    Query = Object('Query')

    @Query.field('example')
    def resolve_example(root, info) -> Example:
        return Example(foo='A', bar='B')

    schema = Schema(query=Query)


Default resolver
----------------

The default resolver for a field will simply attempt to pick the
same-named attribute from the root object.

This way you don't have to define something like this for every simple
field you have on your objects:

.. code-block:: python

    @User.field('name')
    def resolve_user_name(root, info) -> str:
        return root.name

    @User.field('email')
    def resolve_user_email(root, info) -> str:
        return root.email

    # ...


Namespace fields
----------------

Sometimes it's convenient to "namespace" objects. Problem is, field
resolution will stop when an object resolver returns ``None``, so you
need to define your resolvers like this:

.. code-block:: python

    from pyql import ID, Object

    User = Object('User', {'id': ID, 'name': str})

    Users = Object('Users')

    @Users.field('list')
    def resolve_list_users(root, info) -> List[User]:
        pass

    @Users.field('search')
    def resolve_search_users(root, info, query: str) -> List[User]:
        pass

    Query = Object('Query')

    @Query.field('users')
    def resolve_users(root, info) -> Users:
        # Needs to return something other than None, or the resolvers
        # for list / search will never be called
        return Users()

You can replace the ``resolve_users`` definition with:

.. code-block:: python

    Query.namespace_field('users', Users)

This allows you to run queries like::

    {
        users {
            list {
                id
                name
            }
        }
    }



Scalar types
============

The following scalar types are currently defiened in the GraphQL spec,
and supported by PyQL:

- ``str`` -> ``String``
- ``int`` -> ``Int``
- ``float`` -> ``Float``
- ``bool`` -> ``Boolean``
- The ``ID`` type, defined as ``pyql.ID`` (there is no equivalent in
  Python). Will accept strings (or ints) as field value.


Custom scalar types
===================

A few extra types are provided for convenience:

- ``datetime.datetime``, in ISO 8601 format
- ``datetime.date``, in ISO 8601 format
- ``datetime.time``, in ISO 8601 format


Non-nulls
=========

Resolver arguments without a default value will be considered
``NonNull`` automatically.

You can explicity wrap a type in ``pyql.NonNull`` for your output
types (although it doesn't make too much sense to validate your output
fields...).


List fields
===========

You can use ``typing.List`` for defining list fields:

.. code-block:: python

    from typing import List

    @Query.field('example_list')
    def resolve_example_list(root, info) -> List[str]:
        return ['A', 'B', 'C']



Enum fields
===========

You can just use ``enum.Enum`` as normal:


.. code-block:: python

    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    Query = Object('Query')

    @Query.field('random_color')
    def resolve_random_color(root, info) -> Color:
        return Color.RED


They can be used as input types too:


.. code-block:: python

    class Episode(Enum):
        NEWHOPE = 4
        EMPIRE = 5
        JEDI = 6

    DESCRIPTIONS = {
        Episode.NEWHOPE: 'A new hope',
    }

    Query = Object('Query')

    @Query.field('episode')
    def resolve_episode(root, info, episode: Episode) -> str:

        # FIXME: this needs to happen in caller!
        episode = Episode(episode)

        return DESCRIPTIONS.get(episode, 'Unknown episode')


.. warning::

    Currently, the enumerated field *value* will be passed to the
    resolver, **not** the enum member as it would be expected
    (i.e. ``episode`` in the above example is ``4``, not
    ``Episode.NEWHOPE``).


Interfaces
==========

WIP


Unions
======

WIP


Documentation
=============

Documentation loading from objects / resolvers is currently work in
progress, but it's going to use Python docstrings as much as possible.

Argument documentation will also be obtained from parsing the resolver
docstring.
