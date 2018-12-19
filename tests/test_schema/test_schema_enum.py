from enum import Enum

from pyql import ID, NonNull, Object, Schema

import pytest


@pytest.fixture
def sample_output_schema():

    class Color(Enum):
        RED = 'red'
        GREEN = 'green'
        BLUE = 'blue'

    Query = Object('Query')

    @Query.field('random_color')
    def resolve_random_color(root, info) -> Color:
        return Color.RED

    return Schema(query=Query)


@pytest.fixture
def sample_input_schema():

    class Color(Enum):
        RED = 'red'
        GREEN = 'green'
        BLUE = 'blue'

    Query = Object('Query')

    DESCRIPTIONS = {
        Color.RED: 'Cherry Red',
        Color.GREEN: 'Grass Green',
        Color.BLUE: 'Sky Blue',
    }

    @Query.field('describe_color')
    def resolve_describe_color(root, info, color: Color) -> str:
        assert isinstance(color, Color)
        return DESCRIPTIONS[color]

    return Schema(query=Query)


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
    assert str(result.errors) == '[ValueError("\'RED\' is not a valid Color")]'
    assert result.data is None


def test_enum_argument_variable(sample_input_schema):
    """Accept enum value as field argument, via a variable"""

    result = sample_input_schema.execute("""
    query describeColor($color: Color!) {
        describeColor (color: $color)
    }
    """, variables={'color': 'green'})
    assert result.errors is None
    assert result.data == {'describeColor': 'Grass Green'}


def test_enum_argument_variable_must_be_value(sample_input_schema):
    # Enum *values* are for external use, *names* for internal use.

    result = sample_input_schema.execute("""
    query describeColor($color: Color!) {
        describeColor (color: $color)
    }
    """, variables={'color': 'GREEN'})
    assert str(result.errors) == \
        '[ValueError("\'GREEN\' is not a valid Color")]'
    assert result.data is None


@pytest.fixture
def numeric_enum_schema():

    class Number(Enum):
        ONE = 1
        TWO = 2
        THREE = 3

    Query = Object('Query')

    @Query.field('get_number')
    def resolve_get_number(root, info) -> Number:
        return Number.ONE

    DESCRIPTIONS = {
        Number.ONE: 'One',
        Number.TWO: 'Two',
        Number.THREE: 'Three',
    }

    @Query.field('get_number_name')
    def resolve_get_number_name(root, info, num: Number) -> str:
        return DESCRIPTIONS[num]

    return Schema(query=Query)


def test_numeric_enum_output(numeric_enum_schema):
    result = numeric_enum_schema.execute('{getNumber}')

    assert result.errors is None
    assert result.data == {'getNumber': 1}


def test_numeric_enum_input_inline(numeric_enum_schema):

    result = numeric_enum_schema.execute('{getNumberName(num: 1)}')

    assert result.errors is None
    assert result.data == {'getNumberName': 'One'}


def test_numeric_enum_input_variable(numeric_enum_schema):

    result = numeric_enum_schema.execute("""
    query getNumberName($num: Number!) {
        getNumberName(num: $num)
    }
    """, variables={'num': 1})

    assert result.errors is None
    assert result.data == {'getNumberName': 'One'}


def test_numeric_enum_input_variable_type_mismatch(numeric_enum_schema):

    result = numeric_enum_schema.execute("""
    query getNumberName($num: Number!) {
        getNumberName(num: $num)
    }
    """, variables={'num': '1'})

    assert str(result.errors) == '[ValueError("\'1\' is not a valid Number")]'
    assert result.data is None
