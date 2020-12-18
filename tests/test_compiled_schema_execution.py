from collections import namedtuple

from pyql import Object, Schema


def test_resolver_can_return_container_instance():

    schema = Schema()

    Foo = Object("Foo", {"text": str})

    @schema.query.field("foo")
    def resolve_foo(root, info) -> Foo:
        return Foo(text="a")

    result = schema.execute(
        """
    { foo { text } }
    """
    )

    assert result.errors is None
    assert result.data == {"foo": {"text": "a"}}


def test_resolver_can_return_compatible_object():
    """
    Still a duck.
    """

    schema = Schema()

    Foo = Object("Foo", {"text": str})
    AnotherFoo = namedtuple("AnotherFoo", ("text",))

    @schema.query.field("foo")
    def resolve_foo(root, info) -> Foo:
        return AnotherFoo(text="a")

    result = schema.execute(
        """
    { foo { text } }
    """
    )

    assert result.errors is None
    assert result.data == {"foo": {"text": "a"}}


def test_resolver_cannot_return_different_container_instance():
    """
    An instance of a different "container" instance is considered a
    mistake, even if the two are compatible.
    """

    schema = Schema()

    Foo = Object("Foo", {"text": str})
    Bar = Object("Bar", {"text": str})

    @schema.query.field("foo")
    def resolve_foo(root, info) -> Foo:
        return Bar(text="a")

    result = schema.execute(
        """
    { foo { text } }
    """
    )

    assert result.data == {"foo": None}
    assert result.errors is not None
    assert len(result.errors) == 1
    assert (
        result.errors[0].message
        == "Expected value of type 'Foo' but got: <Bar instance>."
    )


def test_returning_an_incompatible_object_fails():

    schema = Schema()

    Foo = Object("Foo", {"text": str})
    Spam = namedtuple("Spam", ("spam",))

    @schema.query.field("foo")
    def resolve_foo(root, info) -> Foo:
        return Spam(spam="SPAM" * 10)

    result = schema.execute(
        """
    { foo { text } }
    """
    )

    assert result.data == {"foo": {"text": None}}
    assert result.errors is None


def test_resolver_can_return_dict():

    schema = Schema()

    Foo = Object("Foo", {"text": str})

    @schema.query.field("foo")
    def resolve_foo(root, info) -> Foo:
        return {"text": "a"}

    result = schema.execute(
        """
    { foo { text } }
    """
    )

    assert result.errors is None
    assert result.data == {"foo": {"text": "a"}}
