Objects
#######

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
===================

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
=========================

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
================

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
================

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
