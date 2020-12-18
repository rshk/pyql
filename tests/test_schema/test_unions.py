from typing import Union

import pytest

import pyql

from pyql import Object, Schema


@pytest.mark.xfail(reason="Unions of scalars are not supported")
class Test_union_of_scalars:

    # ================================================================
    # FIXME: Is this a bug or they're actually not allowed in GraphQL?
    # ================================================================

    @pytest.fixture
    def schema(self):
        schema = Schema()

        Result = pyql.Union("Result", [int, str])

        @schema.query.field("action")
        def resolve_action(root, info, id: int) -> Result:

            if id == 1:
                return 123

            if id == 2:
                return "hello"

            return None

        return schema

    def test_get_integer(self, schema):
        result = schema.execute(
            """
        query ($id: Int!) {
          action (id: $id)
        }
        """,
            variables={"id": 1},
        )

        assert result.errors is None
        assert result.data == {"action": 123}

    def test_get_string(self, schema):
        result = schema.execute(
            """
        query ($id: Int!) {
          action (id: $id)
        }
        """,
            variables={"id": 2},
        )

        assert result.errors is None
        assert result.data == {"action": "hello"}


class Test_union_of_objects:
    @pytest.fixture
    def schema(self):
        schema = Schema()

        Success = Object(
            "Success",
            {
                "ok": bool,
                "result_id": int,
            },
        )

        Error = Object(
            "Error",
            {
                "ok": bool,
                "error_message": str,
            },
        )

        Result = pyql.Union("Result", [Success, Error])

        @schema.query.field("action")
        def resolve_action(root, info, id: int) -> Result:

            if id == 1:
                return Success(ok=True, result_id=123)

            if id == 2:
                return Error(ok=False, error_message="Action failed")

            return None

        return schema

    def test_get_success_result(self, schema):
        result = schema.execute(
            """
        query ($id: Int!) {
          action (id: $id) {
            ... on Success { ok, resultId }
            ... on Error { ok, errorMessage }
          }
        }
        """,
            variables={"id": 1},
        )

        assert result.errors is None
        assert result.data == {"action": {"ok": True, "resultId": 123}}

    def test_get_error_result(self, schema):
        result = schema.execute(
            """
        query ($id: Int!) {
          action (id: $id) {
            ... on Success { ok, resultId }
            ... on Error { ok, errorMessage }
          }
        }
        """,
            variables={"id": 2},
        )

        assert result.errors is None
        assert result.data == {"action": {"ok": False, "errorMessage": "Action failed"}}
