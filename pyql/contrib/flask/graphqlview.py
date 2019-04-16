import flask_graphql
from flask import request
from graphql.error import GraphQLError
from graphql_server import default_format_error, load_json_body
from werkzeug.exceptions import HTTPException


class GraphQLView(flask_graphql.GraphQLView):

    def format_error(self, error):

        if isinstance(error, GraphQLError):
            if isinstance(error.original_error, HTTPException):
                return {
                    **default_format_error(error),
                    'extensions': {
                        'status_code': error.original_error.code,
                        'login_required': error.original_error.code == 401,
                    }
                }

        return default_format_error(error)

    def parse_body(self):

        content_type = request.mimetype

        if content_type == 'application/graphql':
            return {'query': request.data.decode('utf8')}

        elif content_type == 'application/json':
            return load_json_body(request.data.decode('utf8'))

        elif content_type == 'application/x-www-form-urlencoded':
            return request.form

        elif content_type == 'multipart/form-data':
            # --------------------------------------------------------
            # See spec:
            # https://github.com/jaydenseric/graphql-multipart-request-spec
            #
            # When processing multipart/form-data, we need to take
            # files (from "parts") and place them in the "operations"
            # data structure (list or dict) according to the "map".
            # --------------------------------------------------------

            operations = load_json_body(request.form['operations'])
            files_map = load_json_body(request.form['map'])

            return place_files_in_operations(
                operations, files_map, request.files)

        return {}


def place_files_in_operations(operations, files_map, files):
    # operations: dict or list
    # files_map: {filename: [path, path, ...]}
    # files: {filename: FileStorage}

    fmap = []
    for key, values in files_map.items():
        for val in values:
            path = val.split('.')
            fmap.append((path, key))

    return _place_files_in_operations(operations, fmap, files)


def _place_files_in_operations(ops, fmap, fobjs):
    for path, fkey in fmap:
        ops = _place_file_in_operations(ops, path, fobjs[fkey])
    return ops


def _place_file_in_operations(ops, path, obj):

    if len(path) == 0:
        return obj

    if isinstance(ops, list):
        key = int(path[0])
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return _insert_in_list(ops, key, sub)

    if isinstance(ops, dict):
        key = path[0]
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return _insert_in_dict(ops, key, sub)

    raise TypeError('Expected ops to be list or dict')


def _insert_in_dict(dct, key, val):
    return {**dct, key: val}


def _insert_in_list(lst, key, val):
    return [*lst[:key], val, *lst[key+1:]]
