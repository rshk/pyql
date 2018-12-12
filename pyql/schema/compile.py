import functools
from enum import Enum
from typing import Any, Callable

from graphql import (
    GraphQLArgument, GraphQLEnumType, GraphQLEnumValue, GraphQLField,
    GraphQLInputObjectField, GraphQLInputObjectType, GraphQLInterfaceType,
    GraphQLObjectType, GraphQLUnionType)

from pyql.schema.resolve import resolve_type
from pyql.schema.types.core import (
    Argument, Field, InputField, InputObject, Interface, Object, Union)
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


@cache_compiled_object
def compile_object(obj: Object) -> GraphQLObjectType:
    assert isinstance(obj, Object)
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

        is_type_of=obj.is_type_of,
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
    assert isinstance(field, Field)
    return GraphQLField(
        type=resolve_type(field.type),
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
        type=resolve_type(arg.type),
        default_value=arg.default_value,
        description=arg.description)


@cache_compiled_object
def compile_enum(enum: Enum) -> GraphQLEnumType:
    assert issubclass(enum, Enum)
    return GraphQLEnumType(
        name=enum.__name__,
        values={
            key: GraphQLEnumValue(name=key, value=val.value)
            for key, val in enum.__members__.items()},
        description=enum.__doc__)


@cache_compiled_object
def compile_input_object(obj: InputObject) -> GraphQLInputObjectType:
    assert isinstance(obj, InputObject)
    return GraphQLInputObjectType(
        name=obj.name,
        fields={
            _name_to_graphql(name): compile_input_field(field)
            for name, field in obj.fields.items()
        },
        description=obj.description,
        container_type=obj.container_type)


@cache_compiled_object
def compile_input_field(field: InputField) -> GraphQLInputObjectField:
    assert isinstance(field, InputField)
    return GraphQLInputObjectField(
        type=resolve_type(field.type),
        default_value=field.default_value,
        description=field.description,
        out_name=field.out_name)


@cache_compiled_object
def compile_union(union: Union) -> GraphQLUnionType:
    assert isinstance(union, Union)
    return GraphQLUnionType(
        name=union.name,
        types=union.types,
        resolve_type=union.resolve_type,
        description=union.description)
