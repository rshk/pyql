import graphql.execution.executor
from graphql.execution.executor import complete_value as _complete_value_orig
from graphql.utils.undefined import Undefined


def _complete_value_patched(
        exe_context, return_type, field_asts, info, path, result):

    # We want to make sure Undefined values are passed through to
    # executor, so that fields are correctly excluded from the result
    if result is Undefined:
        return Undefined

    return _complete_value_orig(
        exe_context, return_type, field_asts, info, path, result)


graphql.execution.executor.complete_value = _complete_value_patched
