PyQL
####

GraphQL helpers for Python.

- `Documentation <https://pyql-lib.readthedocs.io/en/latest/>`_
- `PyPi package <https://pypi.org/project/PyQL/>`_
- `GitHub repository <https://github.com/rshk/pyql>`_


CI status: |ci-status|

.. |ci-status| image:: https://circleci.com/gh/rshk/pyql.svg?style=svg
    :target: https://circleci.com/gh/rshk/pyql


Schema definition
=================

PyQL provides a better / cleaner syntax for defining GraphQL schemas.

Using PyQL:

.. code-block:: python

    from pyql import Schema

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info, name: str = 'world') -> str:
        return 'Hello {}'.format(name)

    compiled = schema.compile()


Equivalent using graphql-core:

.. code-block:: python

    from graphql import (
        GraphQLObjectType, GraphQLField, GraphQLArgument, GraphQLString,
        GraphQLSchema)

    Query = GraphQLObjectType(
        'Query',
        fields=lambda: {
            'hello': GraphQLField(
                GraphQLString,
                args={
                    'name': GraphQLArgument(
                        type=GraphQLString,
                        default_value='world',
                    ),
                },
                resolver=lambda root, info, name = 'world': f'Hello, {name}'
            ),
        }
    )

    schema = GraphQLSchema(query=Query)


Graphene looks slightly better, but it's quite confusing, and makes
use of unncessary objects:

.. code-block:: python

    import graphene

    class Query(graphene.ObjectType):
        hello = graphene.Field(
            graphene.String,
            name=graphene.Argument(graphene.String))

        def resolve_hello(self, info, name='world'):
            return f'Hello {name}'

    schema = graphene.Schema(query=Query)


PyQL uses standard Python introspection when possible to figure out
things, so eg. argument definitions can be picked up automatically
from a resolver function, etc.


Limitations
===========

While there are plans for field argument documentation to be picked up
automatically from docstrings, it's not currently implemented as
reliably parsing docstrings is a non-trivial task.
