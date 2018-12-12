import datetime
from enum import Enum

import graphql
from graphql import (
    GraphQLBoolean, GraphQLFloat, GraphQLID, GraphQLInt, GraphQLList,
    GraphQLNonNull, GraphQLString)

from pyql.schema.types.core import ID, List, NonNull, Object
from pyql.schema.types.extra import GraphQLDate, GraphQLDateTime, GraphQLTime

TYPE_MAP = {
    str: GraphQLString,
    int: GraphQLInt,
    float: GraphQLFloat,
    bool: GraphQLBoolean,
    ID: GraphQLID,

    datetime.datetime: GraphQLDateTime,
    datetime.date: GraphQLDate,
    datetime.time: GraphQLTime,

    # TODO: support JSONString too? (Like Graphene does)
    # TODO: Provide an API to extend this mapping (?)
}


def resolve_type(pytype):
    """Resolve a Python type to equivalent GraphQL type
    """

    from pyql.schema.compile import compile_object, compile_enum

    if isinstance(pytype, Object):
        return compile_object(pytype)

    if isinstance(pytype, NonNull):
        return GraphQLNonNull(resolve_type(pytype.subtype))

    if isinstance(pytype, List):
        return GraphQLList(resolve_type(pytype.subtype))

    # If it's a GraphQL type already, just let it through
    # TODO: is this a good thing? W/O a good usecase, remove this
    if graphql.is_type(pytype):
        return pytype

    # Simple scalar types
    try:
        return TYPE_MAP[pytype]
    except KeyError:
        pass

    # Lists, defined using ``typing.List[subtype]``
    # TODO: is this the best way to do this comparison?
    if getattr(pytype, '__origin__', None) is list:
        arg, = pytype.__args__
        return GraphQLList(resolve_type(arg))

    # Convert Python enum to graphql
    # TODO: make sure this pytype is a class before running issubclass()
    if issubclass(pytype, Enum):
        return compile_enum(pytype)

    raise TypeError(
        'Unable to map Python type to GraphQL: %s',
        repr(pytype))
