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
        variables={'arg': 'IT WORKS'})

    assert result.errors is None
    assert result.data == {'hello': 'IT WORKS'}
