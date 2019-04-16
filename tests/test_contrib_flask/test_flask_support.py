import json

from flask import Flask

from pyql import Schema
from pyql.contrib.flask import GraphQLView


def test_run_simple_query():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info) -> str:
        return 'Hello world'

    app = Flask(__name__)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql', schema=schema.compile(), graphiql=True))

    # ----------------------------------------------------------------

    client = app.test_client()

    resp = client.get('/graphql', query_string={
        'operationName': 'myQuery',
        'query': 'query myQuery { hello }',
        # 'variables': None,
    })

    assert resp.status_code == 200
    data = resp.get_json()

    assert data == {'data': {'hello': 'Hello world'}}


def test_run_query_with_arguments():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info, name: str) -> str:
        return 'Hello {}'.format(name)

    app = Flask(__name__)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql', schema=schema.compile(), graphiql=True))

    # ----------------------------------------------------------------

    client = app.test_client()

    resp = client.get('/graphql', query_string={
        'operationName': 'myQuery',
        'query': 'query myQuery($name: String!) { hello(name: $name) }',
        'variables': json.dumps({'name': 'FRIEND'}),
    })

    assert resp.status_code == 200
    data = resp.get_json()

    assert data == {'data': {'hello': 'Hello FRIEND'}}


def test_generic_exception_handling():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info) -> str:
        raise ValueError('Some error here')

    app = Flask(__name__)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql', schema=schema.compile(), graphiql=True))

    # ----------------------------------------------------------------

    client = app.test_client()

    resp = client.get('/graphql', query_string={
        'operationName': 'myQuery',
        'query': 'query myQuery { hello }',
    })

    assert resp.status_code == 200
    data = resp.get_json()

    assert data == {
        'data': {'hello': None},
        'errors': [{
            'locations': [{'column': 17, 'line': 1}],
            'message': 'Some error here',
            'path': ['hello'],
        }],
    }


def test_werkzeug_unauthorized_sets_extension():
    from werkzeug.exceptions import Unauthorized

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info) -> str:
        raise Unauthorized('You cannot do this!')

    app = Flask(__name__)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql', schema=schema.compile(), graphiql=True))

    # ----------------------------------------------------------------

    client = app.test_client()

    resp = client.get('/graphql', query_string={
        'operationName': 'myQuery',
        'query': 'query myQuery { hello }',
    })

    assert resp.status_code == 200
    data = resp.get_json()

    assert data == {
        'data': {'hello': None},
        'errors': [{
            'locations': [{'column': 17, 'line': 1}],
            'message': '401 Unauthorized: You cannot do this!',
            'path': ['hello'],
            'extensions': {
                'status_code': 401,
                'login_required': True,
            }
        }],
    }
