from pyql import ID, Interface, Object, Schema


def test_interfaces():

    Character = Interface(
        "Character",
        fields={
            "id": ID,
            "name": str,
        },
    )

    Human = Object(
        "Human",
        interfaces=[Character],
        fields={
            "id": ID,
            "name": str,
            "home_planet": str,
        },
    )

    Droid = Object(
        "Droid",
        interfaces=[Character],
        fields={
            "id": ID,
            "name": str,
            "primary_function": str,
        },
    )

    Query = Object("Query")

    @Query.field("hero_for_episode")
    def resolve_hero_for_episode(root, info, episode: str) -> Character:

        if episode == "JEDI":
            return Droid(id="2001", name="R2-D2", primary_function="Astromech")

        if episode == "EMPIRE":
            return Human(id="1000", name="Luke Skywalker", home_planet="Tatooine")

        return None

    schema = Schema(query=Query, types=[Human, Droid])

    result = schema.execute(
        """
    query HeroForEpisode($ep: String!) {
      heroForEpisode(episode: $ep) {
        id
        name
        ... on Droid {
          primaryFunction
        }
      }
    }
    """,
        variable_values={"ep": "JEDI"},
    )

    assert result.errors is None
    assert result.data == {
        "heroForEpisode": {
            "id": "2001",
            "name": "R2-D2",
            "primaryFunction": "Astromech",
        }
    }
