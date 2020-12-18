"""Make sure we can build all the schemas from Graphene examples.
"""


import typing
from datetime import datetime
from enum import Enum

from pyql import ID, NonNull, Object, Schema


class Color(Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"


class Episode(Enum):
    NEWHOPE = "NEWHOPE"
    EMPIRE = "EMPIRE"
    JEDI = "JEDI"


def test_basic_schema():
    schema = Schema()

    @schema.query.field("hello")
    def resolve_hello(root, info, argument: str = "stranger") -> str:
        return "Hello " + argument

    result = schema.execute("{ hello }")
    assert result.data == {"hello": "Hello stranger"}
    assert result.errors is None

    result = schema.execute('{ hello (argument: "world") }')
    assert result.data == {"hello": "Hello world"}
    assert result.errors is None


def test_enum_output():
    """Return value from an Enum"""

    Card = Object(
        "Card",
        fields={
            "name": str,
            "color": Color,
        },
    )

    schema = Schema()

    @schema.query.field("random_card")
    def resolve_random_card(root, info) -> Card:
        return Card(name="Hello", color=Color.RED)

    result = schema.execute("{ randomCard { name, color } }")
    assert result.errors is None
    assert result.data == {"randomCard": {"name": "Hello", "color": "RED"}}


def test_enum_argument():
    """Accept enum value as field argument"""

    schema = Schema()

    @schema.query.field("episode")
    def resolve_episode(root, info, episode: Episode) -> str:

        episode = Episode(episode)  # FIXME: this needs to happen in caller!

        return ({Episode.NEWHOPE: "A new hope"}).get(episode, "Unknown episode")

    result = schema.execute("{ episode (episode: NEWHOPE) }")
    assert result.errors is None
    assert result.data == {"episode": "A new hope"}

    result = schema.execute("{ episode (episode: FOOBAR) }")

    assert result.errors is not None
    assert [x.message for x in result.errors] == [
        "Expected value of type 'Episode!', found FOOBAR; "
        "'FOOBAR' is not a valid Episode",
    ]
    assert result.data is None


def test_base_scalars_output():

    Example = Object(
        "Example",
        fields={
            "my_str": str,
            "my_int": int,
            "my_float": float,
            "my_bool": bool,
            "my_id": ID,
        },
    )

    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info) -> Example:
        return Example(
            my_str="Some string", my_int=42, my_float=3.14, my_bool=True, my_id="1234"
        )

    result = schema.execute("{ example { myStr, myInt, myFloat, myBool, myId } }")
    assert result.errors is None
    assert result.data == {
        "example": {
            "myStr": "Some string",
            "myInt": 42,
            "myFloat": 3.14,
            "myBool": True,
            "myId": "1234",
        },
    }


def test_base_scalars_input():

    Example = Object(
        "Example",
        fields={
            "my_str": str,
            "my_int": int,
            "my_float": float,
            "my_bool": bool,
            "my_id": ID,
        },
    )

    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info) -> Example:
        return Example(
            my_str="Some string", my_int=42, my_float=3.14, my_bool=True, my_id="1234"
        )

    result = schema.execute("{ example { myStr, myInt, myFloat, myBool, myId } }")
    assert result.errors is None
    assert result.data == {
        "example": {
            "myStr": "Some string",
            "myInt": 42,
            "myFloat": 3.14,
            "myBool": True,
            "myId": "1234",
        },
    }


def test_datetime_output():

    schema = Schema()

    @schema.query.field("my_datetime")
    def resolve_my_datetime(root, info) -> datetime:
        return datetime(2018, 12, 11, 14, 28)

    result = schema.execute("{ myDatetime }")

    assert result.errors is None
    assert result.data == {"myDatetime": "2018-12-11T14:28:00"}


def test_datetime_input():

    schema = Schema()

    @schema.query.field("format_date")
    def resolve_my_datetime(root, info, dt: datetime) -> str:
        return dt.strftime("%a %b %d, %Y %H:%M")

    result = schema.execute('{ formatDate (dt: "2018-12-11T14:28:00") }')

    assert result.errors is None
    assert result.data == {"formatDate": "Tue Dec 11, 2018 14:28"}


def test_non_null_output_nulled():

    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info) -> NonNull(str):
        return None  # Will fail

    result = schema.execute("{example}")

    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "Cannot return null for non-nullable field Query.example."
    )
    assert result.data is None


def test_non_null_input_nulled():
    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info, foo: str) -> bool:
        return foo is not None

    result = schema.execute("{example}")

    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "Field 'example' argument 'foo' of type 'String!' "
        "is required, but it was not provided."
    )
    assert result.data is None


def test_non_null_input_provided():
    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info, foo: str) -> bool:
        return foo is not None

    result = schema.execute('{example(foo:"BAR")}')

    assert result.errors is None
    assert result.data == {"example": True}


def test_list_output():
    schema = Schema()

    @schema.query.field("example")
    def resolve_example(root, info) -> typing.List[str]:
        return ["foo", "bar", "baz"]

    result = schema.execute("{example}")

    assert result.errors is None
    assert result.data == {"example": ["foo", "bar", "baz"]}


def test_list_input():
    schema = Schema()

    @schema.query.field("reverse")
    def resolve_reverse(root, info, lst: typing.List[str]) -> typing.List[str]:
        return list(reversed(lst))

    result = schema.execute('{reverse (lst: ["foo", "bar", "baz"])}')

    assert result.errors is None
    assert result.data == {"reverse": ["baz", "bar", "foo"]}


def test_nested_objects():

    Baz = Object("Baz")

    @Baz.field("val")
    def resolve_baz_val(root, info) -> str:
        return "BAZ-VALUE!"

    Bar = Object("Bar", {"baz": Baz})

    @Bar.field("baz")
    def resolve_bar_baz(root, info) -> Baz:
        return Baz()

    Foo = Object("Foo", {"bar": Bar})

    @Foo.field("bar")
    def resolve_foo_bar(root, info) -> Bar:
        return Bar()

    Query = Object("Query", {"foo": Foo})

    @Query.field("foo")
    def resolve_query_foo(root, info) -> Foo:
        return Foo()

    schema = Schema(query=Query)

    result = schema.execute("{foo {bar {baz {val}}}}")

    assert result.errors is None
    assert result.data == {"foo": {"bar": {"baz": {"val": "BAZ-VALUE!"}}}}


def test_nested_objects_namespace():

    Baz = Object("Baz")

    @Baz.field("val")
    def resolve_baz_val(root, info) -> str:
        return "BAZ-VALUE!"

    Bar = Object("Bar")
    Bar.namespace_field("baz", Baz)

    Foo = Object("Foo")
    Foo.namespace_field("bar", Bar)

    Query = Object("Query")
    Query.namespace_field("foo", Foo)

    schema = Schema(query=Query)

    result = schema.execute("{foo {bar {baz {val}}}}")

    assert result.errors is None
    assert result.data == {"foo": {"bar": {"baz": {"val": "BAZ-VALUE!"}}}}


# TODO: interfaces
# TODO: unions
# TODO: input objects


def test_mutation():

    # ...graphql-core forces us to have at least a query
    Query = Object("Query", fields={"foo": str})

    Mutation = Object("Mutation")

    @Mutation.field("example")
    def resolve_mutate_something(root, info, text: str) -> bool:
        return True

    schema = Schema(query=Query, mutation=Mutation)

    result = schema.execute(
        """
    mutation foo {
        example(text: "HEY")
    }
    """
    )

    assert result.errors is None
    assert result.data == {"example": True}


def test_mutation_with_variables():

    # ...graphql-core forces us to have at least a query
    Query = Object("Query", fields={"foo": str})

    Mutation = Object("Mutation")

    @Mutation.field("letter_count")
    def resolve_letter_count(root, info, text: str) -> int:
        return len(text)

    schema = Schema(query=Query, mutation=Mutation)

    result = schema.execute(
        """
    mutation letterCount($text: String!) {
        result: letterCount(text: $text)
    }
    """,
        variable_values={"text": "HELLO"},
    )

    assert result.errors is None
    assert result.data == {"result": 5}
