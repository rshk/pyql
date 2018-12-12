"""Non-standard GraphQL types

The following types are not in the GraphQL spec, but are provided for
convenience, to allow handling some common types (eg. timestamps).
"""

import datetime

import aniso8601
from graphql import GraphQLScalarType
from graphql.language import ast


def datetime_serialize(dt):
    assert isinstance(
            dt, (datetime.datetime, datetime.date)
        ), 'Received not compatible datetime "{}"'.format(repr(dt))
    return dt.isoformat()


def datetime_parse_literal(node):
    if isinstance(node, ast.StringValue):
        return datetime_parse_value(node.value)


def datetime_parse_value(value):
    try:
        return aniso8601.parse_datetime(value)
    except ValueError:
        return None


GraphQLDateTime = GraphQLScalarType(
    name='DateTime',
    description='The `DateTime` scalar type represents a DateTime'
    'value as specified by'
    '[iso8601](https://en.wikipedia.org/wiki/ISO_8601).',
    serialize=datetime_serialize,
    parse_literal=datetime_parse_literal,
    parse_value=datetime_parse_value,
)


def date_serialize(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    assert isinstance(
        date, datetime.date
    ), 'Received not compatible date "{}"'.format(repr(date))
    return date.isoformat()


def date_parse_literal(node):
    if isinstance(node, ast.StringValue):
        return date_parse_value(node.value)


def date_parse_value(value):
    try:
        return aniso8601.parse_date(value)
    except ValueError:
        return None


GraphQLDate = GraphQLScalarType(
    name='Date',
    description='The `Date` scalar type represents a Date'
    'value as specified by'
    '[iso8601](https://en.wikipedia.org/wiki/ISO_8601).',
    serialize=date_serialize,
    parse_literal=date_parse_literal,
    parse_value=date_parse_value,
)


def time_serialize(time):
    assert isinstance(
        time, datetime.time
    ), 'Received not compatible time "{}"'.format(repr(time))
    return time.isoformat()


def time_parse_literal(node):
    if isinstance(node, ast.StringValue):
        return time_parse_value(node.value)


def time_parse_value(cls, value):
    try:
        return aniso8601.parse_time(value)
    except ValueError:
        return None


GraphQLTime = GraphQLScalarType(
    name='Time',
    description='The `Time` scalar type represents a Time'
    'value as specified by'
    '[iso8601](https://en.wikipedia.org/wiki/ISO_8601).',
    serialize=time_serialize,
    parse_literal=time_parse_literal,
    parse_value=time_parse_value,
)
