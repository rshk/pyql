import inspect

import graphql
from graphql.utils.undefined import Undefined

from pyql.utils.cache import cached_property


class Schema:
    def __init__(self, *, query=None, mutation=None, subscription=None,
                 directives=None, types=None):

        self.query = query or Object('Query')
        self.mutation = mutation or Object('Mutation')
        self.subscription = subscription or Object('Subscription')
        self.directives = directives
        self.types = types

    def compile(self):
        from pyql.schema.compile import compile_schema
        return compile_schema(self)

    def set_query(self, query):
        self.query = query

    def set_mutation(self, mutation):
        self.mutation = mutation

    def set_subscription(self, subscription):
        self.subscription = subscription

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

    def has_fields(self):
        return len(self.fields) > 0

    def __call__(self, **kwargs):
        return self.container_type(**kwargs)

    def _freeze(self):
        # After the "container" object is created and cached,
        # we want to prevent any further changes to the schema.
        self._frozen = True

    def _assert_not_frozen(self):
        if self._frozen:
            raise RuntimeError('Cannot make changes to a frozen schema object')

    @cached_property
    def container_type(self):
        self._freeze()
        # return make_container_type(self.name, {k: None for k in self.fields})
        return make_container_type(self.name, {})

    def __instancecheck__(self, instance):
        # Allow instances of the container type to look like
        # instances of the Object instance itself.
        return isinstance(instance, self.container_type)

    @property
    def container_object(self):
        # DEPRECATED!
        return self.container_type

    def __repr__(self):
        # TODO: show more info about the object?
        return '<pyql.Object {}>'.format(self.name)


def make_container_type(type_name, fields):
    """Make a "container type".

    Args:
        type_name:
            name for the new type
        fields:
            name for the new fields
        type_instance:
            object instance the new type object instances will pretend
            to be an instance of.
    """

    return type(
        type_name,
        (ObjectContainer,),
        {key: val for key, val in fields.items()})


def make_default_resolver(name, default=None):

    def default_resolver(root, info):

        if root is None:
            if default is None:
                return Undefined
            return default()

        # TODO: use subscript if mapping?

        return getattr(root, name, Undefined)

    return default_resolver


class ObjectContainer:
    """Base class for "data-structure" objects from GraphQL objects
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Interface:

    def __init__(self, name, fields=None, resolve_type=None, description=None):
        self.name = name
        self.fields = {}
        self._load_field_args(fields)
        self.resolve_type = resolve_type
        self.description = description

    def _load_field_args(self, fields):
        if fields is None:
            return
        for name, type in fields.items():
            self.define_field(name, type)

    def define_field(
            self, name, type, args=None, resolver=None,
            deprecation_reason=None, description=None):

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
        self.fields[name] = field
        return field


class Field:

    def __init__(self, type, args, resolver, description, deprecation_reason):
        self.type = type
        self.args = args
        self.resolver = resolver
        self.description = description
        self.deprecation_reason = deprecation_reason


class InputObject:

    def __init__(self, name, fields=None, description=None):
        self.name = name
        self.fields = {}
        self._load_field_args(fields)
        self.description = description

    def _load_field_args(self, fields):
        if fields is None:
            return
        for name, type in fields.items():
            self.define_field(name, type)

    def define_field(
            self, name, type, default_value=None, description=None,
            out_name=None):

        field = InputField(
            type=type,
            default_value=default_value,
            description=description,
            out_name=out_name)
        self.fields[name] = field

    @cached_property
    def container_type(self):
        return make_container_type(self.name, {k: None for k in self.fields})

    def __instancecheck__(self, instance):
        # Allow instances of the container type to look like
        # instances of the InputObject instance itself.
        return isinstance(instance, self.container_type)


class InputField:

    def __init__(
            self, type, default_value=None, description=None,
            out_name=None):

        self.type = type
        self.default_value = default_value
        self.description = description
        self.out_name = out_name  # ???


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


class Union:
    def __init__(self, name, types, resolve_type=None, description=None):
        self.name = name
        self.types = types
        self.resolve_type = resolve_type
        self.description = description


ID = object()
