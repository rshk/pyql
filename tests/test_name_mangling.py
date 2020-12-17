"""
Test name conversion

Names in Python are snake_case. The API uses Javascript style
camelCase instead. We need to make sure conversions work as intended.
"""

from pyql import InputObject, Object, Schema


def test_schema_fields_are_converted_to_camel_case():

    schema = Schema()

    @schema.query.field("some_field_name")
    def resolve_some_field_name(root, info) -> str:
        return "A VALUE"

    # ----------------------------------------------------------------

    result = schema.execute(
        """
        query  {
            someFieldName
        }
        """
    )

    assert result.errors is None
    assert result.data == {"someFieldName": "A VALUE"}


def test_fields_are_converted_to_camel_case():

    schema = Schema()

    MyObject = Object("MyObject", fields={"some_field_name": str})

    @schema.query.field("hello")
    def resolve_hello(root, info) -> MyObject:
        return MyObject(some_field_name="A VALUE")

    # ----------------------------------------------------------------

    result = schema.execute(
        """
        query  {
            hello {
                someFieldName
            }
        }
        """
    )

    assert result.errors is None
    assert result.data == {"hello": {"someFieldName": "A VALUE"}}


def test_get_argument_names_from_snake_case():

    schema = Schema()

    @schema.query.field("hello")
    def resolve_hello(root, info, some_arg_name: str) -> str:
        return some_arg_name

    # ----------------------------------------------------------------

    result = schema.execute(
        """
        query {
            hello(someArgName: "A VALUE")
        }
        """
    )

    assert result.errors is None
    assert result.data == {"hello": "A VALUE"}


def test_input_fields_are_converted_from_snake_case():

    schema = Schema()

    MyInput = InputObject("MyInput", fields={"some_field_name": str})

    @schema.query.field("hello")
    def resolve_hello(root, info, arg: MyInput) -> str:
        return arg.some_field_name

    # ----------------------------------------------------------------

    result = schema.execute(
        """
        query ($arg: MyInput!) {
            hello(arg: $arg)
        }
        """,
        variable_values={"arg": {"someFieldName": "A VALUE"}},
    )

    assert result.errors is None
    assert result.data == {"hello": "A VALUE"}
