from graphql import graphql

from pyql import Object, Schema


def test_arguments_are_converted_to_snake_case():
    # Test for issue #5 (https://github.com/rshk/pyql/issues/5)

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, some_arg_name: str) -> str:
        return some_arg_name

    schema = Schema(query=Query)
    compiled = schema.compile()

    # ----------------------------------------------------------------

    result = graphql(
        compiled, """
        query ($arg: String!) {
            hello(someArgName: $arg)
        }
        """,
        variable_values={'arg': 'IT WORKS'})

    assert result.errors is None
    assert result.data == {'hello': 'IT WORKS'}


def test_optional_argument_can_be_omitted():
    # This works fine, even with issue #7

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, some_arg: str = 'DEFAULT') -> str:
        return 'Hello {}'.format(some_arg)

    schema = Schema(query=Query)
    compiled = schema.compile()

    # ----------------------------------------------------------------

    result = graphql(
        compiled, """
        query {
            hello
        }
        """)

    assert result.errors is None
    assert result.data == {'hello': 'Hello DEFAULT'}


def test_optional_argument_can_be_none():
    # Test for issue #7 (https://github.com/rshk/pyql/issues/7)

    Query = Object('Query')

    @Query.field('hello')
    def resolve_hello(root, info, some_arg: str = None) -> str:
        if some_arg is None:
            return 'DEFAULT VALUE'
        return 'Hello {}'.format(some_arg)

    schema = Schema(query=Query)
    compiled = schema.compile()

    # ----------------------------------------------------------------

    result = graphql(
        compiled, """
        query {
            hello
        }
        """)

    assert result.errors is None
    assert result.data == {'hello': 'DEFAULT VALUE'}
