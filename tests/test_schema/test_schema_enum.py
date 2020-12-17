from enum import Enum

import pytest

from pyql import Object, Schema


@pytest.fixture
def sample_output_schema():

    schema = Schema()

    @schema.query.field('random_color')
    def resolve_random_color(root, info) -> Color:
        return Color.RED

    return schema


@pytest.fixture
def sample_input_schema():

    schema = Schema()

    DESCRIPTIONS = {
        Color.RED: 'Cherry Red',
        Color.GREEN: 'Grass Green',
        Color.BLUE: 'Sky Blue',
    }

    @schema.query.field('describe_color')
    def resolve_describe_color(root, info, color: Color) -> str:
        assert isinstance(color, Color)
        return DESCRIPTIONS[color]

    return schema


def test_enum_output(sample_output_schema):
    """Return value from an Enum"""

    schema = sample_output_schema
    result = schema.execute('{ randomColor }')
    assert result.errors is None
    assert result.data == {'randomColor': 'red'}


def test_enum_argument(sample_input_schema):
    """Accept enum value as field argument"""

    result = sample_input_schema.execute("""
    { describeColor (color: red) }
    """)
    assert result.errors is None
    assert result.data == {'describeColor': 'Cherry Red'}


def test_enum_argument_must_be_value(sample_input_schema):
    # Enum *values* are for external use, *names* for internal use.

    result = sample_input_schema.execute("""
    { describeColor (color: RED) }
    """)
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "Expected value of type 'Color!', found RED; "
        "'RED' is not a valid Color"
    )

    assert result.data is None


def test_enum_argument_variable(sample_input_schema):
    """Accept enum value as field argument, via a variable"""

    result = sample_input_schema.execute("""
    query describeColor($color: Color!) {
        describeColor (color: $color)
    }
    """, variable_values={'color': 'green'})

    assert result.errors is None
    assert result.data == {'describeColor': 'Grass Green'}


def test_enum_argument_variable_must_be_value(sample_input_schema):
    # Enum *values* are for external use, *names* for internal use.

    result = sample_input_schema.execute("""
    query describeColor($color: Color!) {
        describeColor (color: $color)
    }
    """, variable_values={'color': 'GREEN'})

    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "Variable '$color' got invalid value 'GREEN'; "
        "Expected type 'Color'. 'GREEN' is not a valid Color"
    )
    assert result.data is None


def test_instrospect_enum(sample_output_schema):

    result = sample_output_schema.execute("""
    query IntrospectionQuery {
      __type(name: "Color") {
        name
        kind
        enumValues(includeDeprecated: true) {
            name
        }
      }
    }
    """)
    assert result.errors is None
    assert result.data == {
        '__type': {
            'name': 'Color',
            'kind': 'ENUM',
            'enumValues': [
                {'name': 'red'},
                {'name': 'green'},
                {'name': 'blue'},
            ]
        }
    }
