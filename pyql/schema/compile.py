import datetime
import functools
import typing
from enum import Enum
from typing import Any, Callable

import graphql
from graphql import (
    GraphQLArgument, GraphQLBoolean, GraphQLField, GraphQLFloat, GraphQLID,
    GraphQLInputField, GraphQLInputObjectType, GraphQLInt,
    GraphQLInterfaceType, GraphQLList, GraphQLNonNull, GraphQLObjectType,
    GraphQLSchema, GraphQLString, GraphQLUnionType)

from pyql.schema.types.core import (
    ID, Argument, Field, InputField, InputObject, Interface, List, NonNull,
    Object, ObjectContainer, Schema, Union)
from pyql.schema.types.enum_type import GraphQLEnumType
from pyql.schema.types.extra import GraphQLDate, GraphQLDateTime, GraphQLTime
from pyql.utils.str_converters import to_camel_case


def compile_schema(schema: Schema) -> GraphQLSchema:
    return GraphQLCompiler().compile_schema(schema)


DEFAULT_TYPE_MAP = {
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


class GraphQLCompiler:

    # We need to use a class here to keep local state (objects cache)

    def __init__(self, custom_types=None):
        self._cache = {}
        self._type_map = dict(DEFAULT_TYPE_MAP)
        if custom_types:
            self._type_map.update(custom_types)

    def get_from_cache(self, obj):
        return self._cache.get(obj)

    def add_to_cache(self, obj, compiled_type):
        self._cache[obj] = compiled_type

    def cache_compiled_object(fn: Callable) -> Any:

        @functools.wraps(fn)
        def wrapped(self, obj):
            result = self.get_from_cache(obj)
            if result is None:
                result = fn(self, obj)
                self.add_to_cache(obj, result)
            return result

        return wrapped

    def compile_schema(self, schema: Schema) -> GraphQLSchema:
        return GraphQLSchema(
            query=self._compile_object_or_none(schema.query),
            mutation=self._compile_object_or_none(schema.mutation),
            subscription=self._compile_object_or_none(schema.subscription),
            directives=schema.directives,
            types=self._compile_schema_types(schema.types))

    def _compile_object_or_none(self, obj):
        if obj is None:
            return None

        if not obj.has_fields():
            # Skip root objects with no fields, or graphql-core will complain
            return None

        return self.compile_object(obj)

    def _compile_schema_types(self, types):
        if not types:
            return None
        # TODO: do we need to support anything other than objects here?
        return tuple(self.compile_object(x) for x in types)

    @cache_compiled_object
    def compile_object(self, obj: Object) -> GraphQLObjectType:
        assert isinstance(obj, Object)

        is_type_of = obj.is_type_of
        if is_type_of is None:

            def is_type_of(val, info):
                # If it's an instance of a container type, it must be
                # the correct one.
                if isinstance(val, ObjectContainer):
                    return isinstance(val, obj.container_type)

                # Accept any other object
                return True

        compiled_type = GraphQLObjectType(

            # Object names are in CamelCase both in Python and GraphQL,
            # so no need for conversion here.
            name=obj.name,

            is_type_of=is_type_of,
            description=obj.description,

            fields={},  # placeholder
            interfaces=[],  # placeholder
        )

        # Need to stick it into cache before we start compiling fields.
        # This way, we already have a reference to this object and avoid
        # infinite recursion if there is a circular reference.
        self.add_to_cache(obj, compiled_type)

        compiled_type.fields = {
            _name_to_graphql(name): self.compile_field(field)
            for name, field in obj.fields.items()
        }

        compiled_type.interfaces = [
            self.compile_interface(x) for x in obj.interfaces
        ] if obj.interfaces else []

        return compiled_type

    @cache_compiled_object
    def compile_interface(self, obj: Interface) -> GraphQLInterfaceType:
        assert isinstance(obj, Interface)
        compiled_type = GraphQLInterfaceType(

            # Object names are in CamelCase both in Python and GraphQL,
            # so no need for conversion here.
            name=obj.name,

            fields={},  # placeholder

            # TODO: do we need to wrap this, so we can convert types
            #       on the fly?
            resolve_type=obj.resolve_type,

            description=obj.description)

        self.add_to_cache(obj, compiled_type)

        compiled_type.fields = {
            _name_to_graphql(name): self.compile_field(field)
            for name, field in obj.fields.items()
        }

        return compiled_type

    @cache_compiled_object
    def compile_field(self, field: Field) -> GraphQLField:
        assert isinstance(field, Field), \
            'Expected Field, got {}'.format(repr(field))

        _arg_names = field.args.keys() if field.args else []

        # NOTE: While we could just convert names back using
        # to_snake_case(), doing so would mean assuming names in Python
        # are in snake_case, which might not always be the case.

        ARG_NAMES_PYTHON_TO_GQL = {
            py_name: _name_to_graphql(py_name)
            for py_name in _arg_names
        }

        ARG_NAMES_GQL_TO_PYTHON = {
            gql_name: py_name
            for py_name, gql_name in ARG_NAMES_PYTHON_TO_GQL.items()
        }

        @functools.wraps(field.resolver)
        def _wrapped_resolver(root, info, **js_kwargs):
            kwargs = {}
            for js_name, py_name in ARG_NAMES_GQL_TO_PYTHON.items():

                # If an argument was omitted in the query (as opposed to
                # setting its value to NULL), it will be missing from the
                # keyword arguments passed to the resolver.

                # We want to make sure we preserve that behaviour when
                # converting names from camelCase to snake_case.

                try:
                    kwargs[py_name] = js_kwargs[js_name]
                except KeyError:
                    pass

            return field.resolver(root, info, **kwargs)

        compiled_type = GraphQLField(
            type_=self.get_graphql_type(field.type),
            args={},  # placeholder
            resolve=_wrapped_resolver,
            description=field.description,
            deprecation_reason=field.deprecation_reason)

        self.add_to_cache(field, compiled_type)

        compiled_type.args = {
            ARG_NAMES_PYTHON_TO_GQL[name]: self.compile_argument(arg)
            for name, arg in field.args.items()
        } if field.args else {}

        return compiled_type

    @cache_compiled_object
    def compile_argument(self, arg: Argument) -> GraphQLArgument:
        assert isinstance(arg, Argument)

        arg_type = self.get_graphql_type(arg.type)

        kwargs = {}
        if not isinstance(arg_type, GraphQLNonNull):
            kwargs['default_value'] = arg.default_value

        return GraphQLArgument(
            type_=arg_type,
            description=arg.description,
            **kwargs)

    @cache_compiled_object
    def compile_enum(self, enum: Enum) -> GraphQLEnumType:
        assert issubclass(enum, Enum)
        return GraphQLEnumType(enum=enum)

    @cache_compiled_object
    def compile_input_object(self, obj: InputObject) -> GraphQLInputObjectType:
        assert isinstance(obj, InputObject)

        # Create map between fields used internally and by the client.
        # Convert all names to camelCase, as that's the convention
        # normally used with GraphQL / Javascript.

        # NOTE: see note about name conversion in compile_field()

        FIELD_NAMES_PYTHON_TO_GQL = {
            py_name: _name_to_graphql(py_name)
            for py_name in obj.fields.keys()
        }

        FIELD_NAMES_GQL_TO_PYTHON = {
            gql_name: py_name
            for py_name, gql_name in FIELD_NAMES_PYTHON_TO_GQL.items()
        }

        # Create an instance of the object that will be passed as argument
        # to the resolver.
        # We need to convert names to their original form (usually
        # snake_case).
        def create_container(arg):
            return obj.container_type(**{
                FIELD_NAMES_GQL_TO_PYTHON[name]: value
                for name, value in arg.items()
            })

        compiled_type = GraphQLInputObjectType(
            name=obj.name,
            fields={},  # placeholder
            description=obj.description,
            out_type=create_container)

        self.add_to_cache(obj, compiled_type)

        compiled_type.fields = {
            FIELD_NAMES_PYTHON_TO_GQL[name]:
            self.compile_input_field(field)
            for name, field in obj.fields.items()
        }

        return compiled_type

    @cache_compiled_object
    def compile_input_field(self, field: InputField) -> GraphQLInputField:
        assert isinstance(field, InputField)
        return GraphQLInputField(
            type_=self.get_graphql_type(field.type),
            default_value=field.default_value,
            description=field.description,
            out_name=field.out_name)

    @cache_compiled_object
    def compile_union(self, union: Union) -> GraphQLUnionType:
        assert isinstance(union, Union)
        return GraphQLUnionType(
            name=union.name,
            types=tuple(
                self.get_graphql_type(t) for t in union.types),
            resolve_type=union.resolve_type,
            description=union.description)

    def get_graphql_type(self, pytype):
        """Resolve a Python type to equivalent GraphQL type
        """

        if isinstance(pytype, Object):
            return self.compile_object(pytype)

        if isinstance(pytype, Interface):
            return self.compile_interface(pytype)

        if isinstance(pytype, InputObject):
            return self.compile_input_object(pytype)

        if isinstance(pytype, Union):
            return self.compile_union(pytype)

        if isinstance(pytype, NonNull):
            return GraphQLNonNull(self.get_graphql_type(pytype.subtype))

        if isinstance(pytype, List):
            return GraphQLList(self.get_graphql_type(pytype.subtype))

        # If it's a GraphQL type already, just let it through
        # TODO: is this a good thing? W/O a good usecase, remove this
        if graphql.is_type(pytype):
            return pytype

        # Simple scalar types
        try:
            return self._type_map[pytype]
        except KeyError:
            pass

        # ----------------------------------------------------------------
        # Lists, defined using ``typing.List[subtype]``
        #
        # In Python 3.5 and 3.6, we could use issubclass(List[str], List).
        # In Python 3.7 this will fail, as "Subscribed generics cannot be
        # used with class and instance checks".
        #
        # As a fallback, we're checking the __origin__ attribute, but this
        # feels quite sub-optimal.
        #
        # Also, on Python 3.5 / 3.6 ``List[str].__origin__ is List``,
        # while on Python 3.7 ``List[str].__origin__ is list``.
        #
        # Search for a better alternative is under way.
        # ----------------------------------------------------------------
        pytype_origin = getattr(pytype, '__origin__', None)
        if pytype_origin is list or pytype_origin is typing.List:
            arg, = pytype.__args__
            return GraphQLList(self.get_graphql_type(arg))

        # TODO: support typing.Union type too!

        # Convert Python enum to graphql
        if isinstance(pytype, type) and issubclass(pytype, Enum):
            return self.compile_enum(pytype)

        raise TypeError(
            'Unable to map Python type to GraphQL: %s',
            repr(pytype))


def _name_to_graphql(name):
    """Convert Python snake_case names to GraphQL camelCase"""
    return to_camel_case(name)
