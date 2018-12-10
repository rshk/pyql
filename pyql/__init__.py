import datetime
import functools
import inspect
from enum import Enum

import aniso8601
import graphql
from graphql import (
    GraphQLArgument, GraphQLBoolean, GraphQLEnumType, GraphQLEnumValue,
    GraphQLField, GraphQLFloat, GraphQLID, GraphQLInt, GraphQLList,
    GraphQLNonNull, GraphQLObjectType, GraphQLScalarType, GraphQLSchema,
    GraphQLString)
from graphql.language import ast

from pyql.utils.str_converters import to_camel_case


class Schema:
    def __init__(self, *, query=None, mutation=None, subscription=None,
                 directives=None, types=None):

        self.query = query
        self.mutation = mutation
        self.subscription = subscription
        self.directives = directives
        self.types = types

    def compile(self):
        CACHE_KEY = '_compiled_schema'
        compiled = getattr(self, CACHE_KEY, None)

        if compiled is None:
            compiled = self._compile()
            setattr(self, CACHE_KEY, compiled)

        return compiled

    def _compile(self):
        query = self._compile_query()
        mutation = self._compile_mutation()
        subscription = self._compile_subscription()

        return GraphQLSchema(
            query=query,
            mutation=mutation,
            subscription=subscription,
            directives=self.directives,
            types=self.types)

    def set_query(self, query):
        self.query = query

    def set_mutation(self, mutation):
        self.mutation = mutation

    def set_subscription(self, subscription):
        self.subscription = subscription

    def _compile_query(self):
        if self.query is None:
            return None
        return _compile_object(self.query)

    def _compile_mutation(self):
        if self.mutation is None:
            return None
        return _compile_object(self.mutation)

    def _compile_subscription(self):
        if self.subscription is None:
            return None
        return _compile_object(self.subscription)

    def execute(self, *args, **kwargs):
        compiled = self.compile()
        return graphql.graphql(compiled, *args, **kwargs)


class Object:

    def __init__(self, name, fields=None, interfaces=None, is_type_of=None,
                 description=None):

        self._frozen = False
        self.name = name
        self.fields = {}
        self._load_field_args(fields)
        self.interfaces = interfaces
        self.is_type_of = is_type_of
        self.description = description

    def _load_field_args(self, fields):
        if fields is None:
            return
        for name, type in fields.items():
            self.define_field(name, type)

    def field(self, name):
        def decorator(resolver):
            self._assert_not_frozen()
            field = field_from_resolver(resolver)
            self._define_field(name, field)
            return field
        return decorator

    def define_field(
            self, name, type, args=None, resolver=None,
            deprecation_reason=None, description=None):

        self._assert_not_frozen()

        if resolver is None:
            resolver = make_default_resolver(name)

        kwargs = {
            'type': type,
            'args': args,
            'resolver': resolver,
            'deprecation_reason': deprecation_reason,
            'description': description,
        }
        field = Field(**kwargs)
        self._define_field(name, field)
        return field

    def namespace_field(self, name, type, **kwargs):
        def resolver(root, info):
            return type()
        return self.define_field(
            name, type, resolver=resolver, **kwargs)

    def _define_field(self, name, field):
        self._assert_not_frozen()
        self.fields[name] = field

    def __call__(self, **kwargs):
        return self.create_instance(**kwargs)

    def create_instance(self, **kwargs):
        container = self._container_object
        return container(**kwargs)

    def _freeze(self):
        # After the "container" object is created and cached,
        # we want to prevent any further changes to the schema.
        self._frozen = True

    def _assert_not_frozen(self):
        if self._frozen:
            raise RuntimeError('Cannot make changes to a frozen schema object')

    @property
    def _container_object(self):
        self._freeze()
        container = getattr(self, '_cached_container_object', None)
        if container is None:
            container = self._make_container_object()
            self._cached_container_object = container
        return container

    def _make_container_object(self):
        return type(
            self.name,
            (ObjectContainer,),
            {k: None for k in self.fields})


def make_default_resolver(name, default=None):

    def default_resolver(root, info):

        if root is None:
            if default is None:
                return None
            return default()

        # TODO: use subscript if mapping?

        return getattr(root, name)

    return default_resolver


class ObjectContainer:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Interface:

    def __init__(self, name, fields=None, resolve_type=None, description=None):
        self.name = name
        self.fields = fields
        self.resolve_type = resolve_type
        self.description = description


class Field:

    def __init__(self, type, args, resolver, description, deprecation_reason):
        self.type = type
        self.args = args
        self.resolver = resolver
        self.description = description
        self.deprecation_reason = deprecation_reason


class Argument:

    def __init__(self, type, default_value=None, description=None):
        self.type = type
        self.default_value = default_value
        self.description = description


def field_from_resolver(resolver):

    signature = inspect.signature(resolver)

    _params = iter(signature.parameters.items())

    try:
        next(_params)  # root
        next(_params)  # info
    except StopIteration:
        raise ValueError(
            'Resolver must accept "root" and "info" as first '
            'positional arguments')

    args = {}

    for name, param in _params:

        if param.kind == param.VAR_KEYWORD:
            raise ValueError(
                'Variable keyword arguments are not supported')

        if param.kind == param.VAR_POSITIONAL:
            raise ValueError(
                'Variable arguments are not supported')

        if param.kind == param.POSITIONAL_ONLY:
            raise ValueError(
                'Positional-only arguments are not supported')

        assert param.kind in (param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD)

        if param.annotation is None:
            raise ValueError('Resolver arguments must have a valid annotation')

        type_ = param.annotation
        default = param.default

        if default is param.empty:
            type_ = NonNull(type_)
            default = None

        args[name] = Argument(
            type=type_,
            default_value=default,
            description=None,  # TODO: parse docstring
        )

    if ((signature.return_annotation is None) or
            (signature.return_annotation is inspect._empty)):

        raise ValueError('Resolver return type must not be None')

    return Field(
        type=signature.return_annotation,
        args=args,
        resolver=resolver,
        description=None,  # TODO: parse docstring
        deprecation_reason=None,  # TODO: parse docstring
    )


class NonNull:
    def __init__(self, subtype):
        self.subtype = subtype


class List:
    def __init__(self, subtype):
        self.subtype = subtype


ID = object()

# --------------------------------------------------------------------
# Non-standard convenience types
# --------------------------------------------------------------------

# GraphQLFileUpload = GraphQLScalarType(
#     name="FileUpload",
#     description="Field for file uploads",
#     serialize=lambda value: None,
#     parse_value=lambda node: node,
#     parse_literal=lambda value: value,
# )


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


# --------------------------------------------------------------------


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

    if isinstance(pytype, Object):
        return _compile_object(pytype)

    # If it's a GraphQL type already, just let it through
    if graphql.is_type(pytype):
        return pytype

    try:
        return TYPE_MAP[pytype]
    except KeyError:
        pass

    # Process lists
    # TODO: is this the best way to do this comparison?
    if getattr(pytype, '__origin__', None) is list:
        arg, = pytype.__args__
        return GraphQLList(resolve_type(arg))

    if isinstance(pytype, NonNull):
        return GraphQLNonNull(resolve_type(pytype.subtype))

    if isinstance(pytype, List):
        return GraphQLList(resolve_type(pytype.subtype))

    # Convert Python enum to graphql
    if issubclass(pytype, Enum):
        return GraphQLEnumType(
            name=pytype.__name__,
            values={
                key: GraphQLEnumValue(name=key, value=val.value)
                for key, val in pytype.__members__.items()},
            description=pytype.__doc__)

    raise TypeError(
        'Unable to map Python type to GraphQL: %s',
        repr(pytype))


# --------------------------------------------------------------------
# Schema compilation
# --------------------------------------------------------------------


# Need to make sure we always return the same instance
COMPILED_OBJECTS_CACHE = {}


def cache_compiled_object(fn):
    @functools.wraps(fn)
    def wrapped(obj):
        result = COMPILED_OBJECTS_CACHE.get(obj)
        if result is None:
            result = fn(obj)
            COMPILED_OBJECTS_CACHE[obj] = result
        return result
    return wrapped


def _name_to_graphql(name):
    # Convert Python snake_case names to camelCase.
    return to_camel_case(name)


@cache_compiled_object
def _compile_object(obj):
    return GraphQLObjectType(
        obj.name,  # Object names are CamelCase
        fields={
            _name_to_graphql(name): _compile_field(field)
            for name, field in obj.fields.items()
        },
        interfaces=obj.interfaces,
        is_type_of=obj.is_type_of,
        description=obj.description)


@cache_compiled_object
def _compile_field(field):
    return GraphQLField(
        type=resolve_type(field.type),
        args={
            _name_to_graphql(name): _compile_argument(arg)
            for name, arg in field.args.items()
        } if field.args else None,
        resolver=field.resolver,
        description=field.description,
        deprecation_reason=field.deprecation_reason)


@cache_compiled_object
def _compile_argument(arg):
    return GraphQLArgument(
        type=resolve_type(arg.type),
        default_value=arg.default_value,
        description=arg.description)
