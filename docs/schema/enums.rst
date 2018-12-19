Enums
#####

You can use Enums as input / output types as you would with any scalar type.

Start by defining your Enum type:


.. code-block:: python

    from enum import Enum

    class Color(Enum):
        RED = 'red'
        GREEN = 'green'
        BLUE = 'blue'


Then, simply use it to annotate your resolvers:


.. code-block:: python

    @Query.field('random_color')
    def resolve_random_color(root, info) -> Color:
        return Color.RED


Or for an input type:


.. code-block:: python

    DESCRIPTIONS = {
        Color.RED: 'Cherry Red',
        Color.GREEN: 'Grass Green',
        Color.BLUE: 'Sky Blue',
    }

    @Query.field('describe_color')
    def resolve_episode(root, info, color: Color) -> str:
        return DESCRIPTIONS[color]


Values vs names
===============

Keep in mind that enum *values* will be used externally; member names
are for internal use only.

So, for example, the first query will return:

.. code-block:: json

    { "randomColor": "red" }

Likewise, the second and third query will accept ``red`` (the enum
value) and not ``"RED"`` as input value.

Valid query::

    { describeColor(color: red) }

Invalid query::

    { describeColor(color: RED) }
