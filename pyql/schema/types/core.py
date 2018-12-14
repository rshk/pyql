import inspect

import graphql


class Schema:
    def __init__(self, *, query=None, mutation=None, subscription=None,
                 directives=None, types=None):

        self.query = query
        self.mutation = mutation
        self.subscription = subscription
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

    def __call__(self, **kwargs):
        return self.create_instance(**kwargs)

    def create_instance(self, **kwargs):
        container = self.container_object
        return container(**kwargs)

    def _freeze(self):
        # After the "container" object is created and cached,
        # we want to prevent any further changes to the schema.
        self._frozen = True

    def _assert_not_frozen(self):
        if self._frozen:
            raise RuntimeError('Cannot make changes to a frozen schema object')

    @property
    def container_object(self):
        CACHE_KEY = '_cached_container_object'
        self._freeze()
        container = getattr(self, CACHE_KEY, None)
        if container is None:
            container = self._make_container_object()
            setattr(self, CACHE_KEY, container)
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
    """Base class for "data-structure" objects from GraphQL objects
    """

    # TODO: make isinstance(<self>, <Object instance>) work!

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

    def __init__(
            self, name, fields=None, description=None, container_type=None):

        self.name = name
        self.fields = {}
        self._load_field_args(fields)
        self.description = description
        self.container_type = container_type

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
        self._fields[name] = field


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
