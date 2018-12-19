import datetime
import functools
from enum import Enum
from typing import Any, Callable

import graphql
from graphql import (
    GraphQLArgument, GraphQLBoolean, GraphQLField, GraphQLFloat, GraphQLID,
    GraphQLInputObjectField, GraphQLInputObjectType, GraphQLInt,
    GraphQLInterfaceType, GraphQLList, GraphQLNonNull, GraphQLObjectType,
    GraphQLSchema, GraphQLString, GraphQLUnionType)

from pyql.schema.types.core import (
    ID, Argument, Field, InputField, InputObject, Interface, List,
    NonNull, Object, Schema, Union)
from pyql.schema.types.enum_type import GraphQLEnumType
from pyql.schema.types.extra import GraphQLDate, GraphQLDateTime, GraphQLTime
from pyql.utils.str_converters import to_camel_case


def cache_compiled_object(fn: Callable) -> Any:
    """Decorator to cache compiled object result"""

    COMPILED_OBJECTS_CACHE = {}

    @functools.wraps(fn)
    def wrapped(obj):
        result = COMPILED_OBJECTS_CACHE.get(obj)
        if result is None:
            result = fn(obj)
            COMPILED_OBJECTS_CACHE[obj] = result
        return result

    return wrapped


def _name_to_graphql(name):
    """Convert Python snake_case names to GraphQL camelCase"""
    return to_camel_case(name)


def compile_schema(schema: Schema) -> GraphQLSchema:
    return GraphQLSchema(
        query=_compile_object_or_none(schema.query),
        mutation=_compile_object_or_none(schema.mutation),
        subscription=_compile_object_or_none(schema.subscription),
        directives=schema.directives,
        types=_compile_schema_types(schema.types))


def _compile_object_or_none(obj):
    if obj is None:
        return None
    return compile_object(obj)


def _compile_schema_types(types):
    if not types:
        return None
    # TODO: do we need to support anything other than objects here?
    return tuple(compile_object(x) for x in types)


@cache_compiled_object
def compile_object(obj: Object) -> GraphQLObjectType:
    assert isinstance(obj, Object)

    is_type_of = obj.is_type_of
    if is_type_of is None:
        # Checks whether an object returned from a resolver belongs to
        # this object type.
        # We allow users to override this, but the default
        # implementation should work fine in most cases, really..
        def is_type_of(val, info):
            return isinstance(val, obj.container_object)

    return GraphQLObjectType(

        # Object names are in CamelCase both in Python and GraphQL,
        # so no need for conversion here.
        name=obj.name,

        fields={
            _name_to_graphql(name): compile_field(field)
            for name, field in obj.fields.items()
        },

        interfaces=[
            compile_interface(x) for x in obj.interfaces
        ] if obj.interfaces else None,

        is_type_of=is_type_of,
        description=obj.description)


@cache_compiled_object
def compile_interface(obj: Interface) -> GraphQLInterfaceType:
    assert isinstance(obj, Interface)
    return GraphQLInterfaceType(

        # Object names are in CamelCase both in Python and GraphQL,
        # so no need for conversion here.
        name=obj.name,

        fields={
            _name_to_graphql(name): compile_field(field)
            for name, field in obj.fields.items()
        },

        # TODO: do we need to wrap this, so we can convert types on the fly?
        resolve_type=obj.resolve_type,

        description=obj.description)


@cache_compiled_object
def compile_field(field: Field) -> GraphQLField:
    assert isinstance(field, Field), \
        'Expected Field, got {}'.format(repr(field))
    return GraphQLField(
        type=get_graphql_type(field.type),
        args={
            _name_to_graphql(name): compile_argument(arg)
            for name, arg in field.args.items()
        } if field.args else None,
        resolver=field.resolver,
        description=field.description,
        deprecation_reason=field.deprecation_reason)


@cache_compiled_object
def compile_argument(arg: Argument) -> GraphQLArgument:
    assert isinstance(arg, Argument)
    return GraphQLArgument(
        type=get_graphql_type(arg.type),
        default_value=arg.default_value,
        description=arg.description)


@cache_compiled_object
def compile_enum(enum: Enum) -> GraphQLEnumType:
    assert issubclass(enum, Enum)
    return GraphQLEnumType(enum=enum)


@cache_compiled_object
def compile_input_object(obj: InputObject) -> GraphQLInputObjectType:
    assert isinstance(obj, InputObject)

    # We need to wrap this as "container_type" will receive a dict as
    # only argument, instead of keyword arguments.
    def create_container(arg):
        return obj.container_type(**arg)

    return GraphQLInputObjectType(
        name=obj.name,
        fields={
            _name_to_graphql(name): compile_input_field(field)
            for name, field in obj.fields.items()
        },
        description=obj.description,
        container_type=create_container)


@cache_compiled_object
def compile_input_field(field: InputField) -> GraphQLInputObjectField:
    assert isinstance(field, InputField)
    return GraphQLInputObjectField(
        type=get_graphql_type(field.type),
        default_value=field.default_value,
        description=field.description,
        out_name=field.out_name)


@cache_compiled_object
def compile_union(union: Union) -> GraphQLUnionType:
    assert isinstance(union, Union)
    return GraphQLUnionType(
        name=union.name,
        types=tuple(
            get_graphql_type(t) for t in union.types),
        resolve_type=union.resolve_type,
        description=union.description)


# --------------------------------------------------------------------
# Type resolution


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


def get_graphql_type(pytype):
    """Resolve a Python type to equivalent GraphQL type
    """

    from pyql.schema.compile import compile_object, compile_enum

    if isinstance(pytype, Object):
        return compile_object(pytype)

    if isinstance(pytype, Interface):
        return compile_interface(pytype)

    if isinstance(pytype, InputObject):
        return compile_input_object(pytype)

    if isinstance(pytype, Union):
        return compile_union(pytype)

    if isinstance(pytype, NonNull):
        return GraphQLNonNull(get_graphql_type(pytype.subtype))

    if isinstance(pytype, List):
        return GraphQLList(get_graphql_type(pytype.subtype))

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
        return GraphQLList(get_graphql_type(arg))

    # TODO: support typing.Union type too!

    # Convert Python enum to graphql
    if isinstance(pytype, type) and issubclass(pytype, Enum):
        return compile_enum(pytype)

    raise TypeError(
        'Unable to map Python type to GraphQL: %s',
        repr(pytype))
