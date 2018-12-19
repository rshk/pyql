PyQL
####

GraphQL helpers for Python.

- `Documentation <https://pyql-lib.readthedocs.io/en/latest/>`_
- `PyPi package <https://pypi.org/project/PyQL/>`_
- `GitHub repository <https://github.com/rshk/pyql>`_


Schema definition
=================

PyQL provides a better / cleaner syntax for defining GraphQL schemas.

Using PyQL:

.. code-block:: python

    from pyql import Object, Schema

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, name: str = 'world') -> str:
        return 'Hello {}'.format(name)

    schema = Schema(query=Query)
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

The whole API is currently work in progress and might change in the future.

Documentation coming as soon as things get a bit more well defined.


Contributing: creating a release
================================

1. Update version number in ``setup.py``
2. Update version number in ``docs/conf.py``
3. Commit changes, eg::

     git add setup.py docs/conf.py
     git commit -m '0.2.1 ...'

4. Tag the version, eg::

     git tag -a -m 'Version 0.2.1' v0.2.1

5. Push changes to GitHub::

     git push
     git push --tags

6. Release on PyPI::

     rm -rf dist
     python setup.py sdist bdist_wheel
     twine upload dist/*
