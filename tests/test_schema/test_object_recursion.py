from pyql import Object, Schema


def test_objects_can_reference_each_other():

    Foo = Object("Foo", {"name": str})
    Bar = Object("Bar", {"name": str})

    @Foo.field("bar")
    def resolve_foo_bar(root, info) -> Bar:
        return Bar(name="{} bar".format(root.name))

    @Bar.field("foo")
    def resolve_bar_foo(root, info) -> Foo:
        return Foo(name="{} foo".format(root.name))

    schema = Schema()

    @schema.query.field("foo")
    def resolve_query_foo(root, info) -> Foo:
        return Foo(name="FOO")

    @schema.query.field("bar")
    def resolve_query_bar(root, info) -> Bar:
        return Bar(name="BAR")

    result = schema.execute(
        """
    query {
        foo {
            name
            bar {
                name
                foo {
                    name
                }
            }
        }
    }
    """
    )

    assert result.errors is None
    assert result.data == {
        "foo": {
            "name": "FOO",
            "bar": {"name": "FOO bar", "foo": {"name": "FOO bar foo"}},
        }
    }
