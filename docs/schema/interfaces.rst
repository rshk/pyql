Interfaces
##########

To define an interface, instantiate ``pyql.Interface``:

.. code-block:: python

    from pyql import Interface

    Character = Interface('Character', fields={
        'id': ID,
        'name': str,
    })


To define an object using a given interface:

.. code-block:: python

    from pyql import Object

    Human = Object('Human', interfaces=[Character], fields={
        'id': ID,
        'name': str,
        'home_planet': str,
    })

    Droid = Object('Droid', interfaces=[Character], fields={
        'id': ID,
        'name': str,
        'primary_function': str,
    })


Automatic type resolution
=========================

**TL;DR:** if your resolver is returning instances of the correct
object container, i.e. ``Human(...)`` or ``Droid(...)`` in the above
example, the correct type will be figured out and everything will work
just fine.

GraphQL core requires you to either pass a ``resolve_type`` function
to your ``Interface``, or provide a ``is_type_of`` function on the
concrete ``Object``.

For convenience, if no ``is_type_of`` is passed to an ``Object``,
we'll simply recognise as belonging to that object all instances of
the "container" type for the object.

Or in better words:

.. code-block:: python

    MyObj = Object('MyObj', fields={'foo': str})

    obj = MyObj(foo='VALUE')

    # When compiling MyObj to a GraphQLObject, is_type_of
    # will be defined as:
    #
    # def is_type_of(value, info):
    #     return isinstance(value, MyObj.container_object)
