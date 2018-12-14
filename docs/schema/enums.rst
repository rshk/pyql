Enums
#####

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
