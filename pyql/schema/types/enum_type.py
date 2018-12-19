from enum import Enum

from graphql import GraphQLEnumType as _GraphQLNamedType
from graphql.language import ast


class GraphQLEnumType(_GraphQLNamedType):

    # Note: we're only subclassing _GraphQLNamedType so that
    # is_type(...) / is_output_type(...) calls will still work.
    # Maybe we can use __instancecheck__ instead? (Although having to
    # use metaclasses is never great..)

    def __init__(self, *, enum):
        assert isinstance(enum, type) and issubclass(enum, Enum), (
            'enum argument must be an Enum')
        self._enum = enum

    @property
    def name(self):
        return self._enum.__name__

    @property
    def description(self):
        return self._enum.__doc__

    def get_values(self):
        return self._enum.__members__

    def get_value(self, name):
        return self._enum(name)

    def serialize(self, value):
        # Serialize to client
        if not isinstance(value, self._enum):
            raise TypeError(
                'Value must be an instance of Enum: {}'
                .format(self._enum))
        return value.value

    def parse_value(self, value):
        # Parse from query variable
        return self.get_value(value)

    def parse_literal(self, value_ast):
        # Parse from query (inline literal)
        if not isinstance(value_ast, ast.EnumValue):
            # TODO: we can allow strings as well..?
            raise TypeError('Expected EnumValue, got {}'
                            .format(repr(value_ast)))
        return self.get_value(value_ast.value)
