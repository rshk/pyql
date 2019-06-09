from enum import Enum

from graphql import GraphQLEnumType as _GraphQLNamedType
from graphql import GraphQLEnumValue
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

    @property
    def values(self):
        # Needed for introspection
        # NOTE: the actual value used in queries is ``name``; keys are
        # for internal use only.
        return [
            GraphQLEnumValue(value.value, name=value.value)
            for key, value in self.get_values().items()
        ]

    def get_values(self):
        return self._enum.__members__

    def get_value(self, name):
        return self._enum(name)

    def serialize(self, value):
        """Serialize value to the client

        Args:
            value: one of the members of the Enum

        Returns:
            str or int: value of the enum member
        """

        if not isinstance(value, self._enum):
            raise TypeError(
                'Value must be an instance of Enum: {}'
                .format(self._enum))
        return value.value

    def parse_value(self, value):
        """Parse value from variable

        Args:
            value: value, as passed in the GraphQL variable
        """

        return self.get_value(value)

    def parse_literal(self, value_ast):
        """Parse value from query

        Args:
            value_ast: AST value
        """

        if isinstance(value_ast, ast.EnumValue):
            return self.get_value(value_ast.value)

        if isinstance(value_ast, ast.IntValue):
            # We need this as there's no difference between an "enum
            # value" integer and an actual literal integer.
            # For strings we can be more strict, and won't accept
            # "VALUE" (StringValue) in place of VALUE (EnumValue).
            return self.get_value(int(value_ast.value))

        raise TypeError(
            'Invalid input value for Enum {}: {}'
            .format(repr(self._enum), repr(value_ast)))
