"""
enum Episode { NEWHOPE, EMPIRE, JEDI }

interface Character {
  id: String!
  name: String
  friends: [Character]
  appearsIn: [Episode]
}

type Human implements Character {
  id: String!
  name: String
  friends: [Character]
  appearsIn: [Episode]
  homePlanet: String
}

type Droid implements Character {
  id: String!
  name: String
  friends: [Character]
  appearsIn: [Episode]
  primaryFunction: String
}

type Query {
  hero(episode: Episode): Character
  human(id: String!): Human
  droid(id: String!): Droid
}
"""

from enum import Enum


schema = Schema()


class Episode(Enum):
    NEWHOPE = 'NEWHOPE'
    EMPIRE = 'EMPIRE'
    JEDI = 'JEDI'


Character = Interface(
    'Character',
    fields={
        'id': str,
        'name': str,
        'friends': None,
        'appears_in': [Episode],
    },
)


Character.define_field('friends', [Character])

Human = Object(
    'Human',
    implements=[Character],
    fields={
        'id': str,
        'name': str,
        'friends': None,
        'appears_in': [Episode],
        'home_planet': str,
    },
)

Droid = Object(
    'Droid',
    implements=[Character],
    fields={
        'id': str,
        'name': str,
        'friends': None,
        'appears_in': [Episode],
        'primary_function': str,
    },
)


Query = Object(
    'Query',
    fields={
        'hero': Character,
        'human': Human,
        'droid': Droid,
    },
)


@Query.field('hero')
def resolve_hero(episode: Episode = None) -> Character:
    pass


@Query.field('human')
def resolve_human(id: str) -> Character:
    pass


@Query.field('droid')
def resolve_droid(id: str) -> Character:
    pass
