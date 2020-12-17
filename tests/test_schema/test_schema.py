from typing import List

from graphql import GraphQLError

from pyql import Object, Schema


def test_create_basic_schema():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info) -> str:
        return 'Hello world'

    # ----------------------------------------------------------------

    result = schema.execute('{hello}')

    assert result.data == {'hello': 'Hello world'}
    assert result.errors is None


def test_simple_query_with_optional_argument():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info, name: str = 'world') -> str:
        return 'Hello {}'.format(name)

    # ----------------------------------------------------------------

    result = schema.execute('{hello}')

    assert result.data == {'hello': 'Hello world'}
    assert result.errors is None

    # ----------------------------------------------------------------

    result = schema.execute("""
    query hello($name: String!) {
        hello(name: $name)
    }
    """, variable_values={'name': 'WROLD!!1'})

    assert result.data == {'hello': 'Hello WROLD!!1'}
    assert result.errors is None


def test_simple_query_with_mandatory_argument():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info, name: str) -> str:
        return 'Hello {}'.format(name)

    # ----------------------------------------------------------------

    result = schema.execute('{hello}')

    assert result.data is None
    assert len(result.errors) == 1
    assert isinstance(result.errors[0], GraphQLError)
    assert result.errors[0].message == (
        "Field 'hello' argument 'name' of type 'String!' "
        "is required, but it was not provided."
    )

    # ----------------------------------------------------------------

    result = schema.execute("""
    query hello($name: String!) {
        hello(name: $name)
    }
    """, variable_values={'name': 'WROLD!!1'})

    assert result.data == {'hello': 'Hello WROLD!!1'}
    assert result.errors is None


def test_schema_with_nested_objects():

    schema = Schema()

    Post = Object('Post', fields={
        'title': str,
        'body': str,
    })

    @schema.query.field('post')
    def resolve_posts(root, info) -> Post:
        return Post(title='One', body='First post')

    # ----------------------------------------------------------------

    result = schema.execute('{post {title, body}}')

    assert result.data == {'post': {'title': 'One', 'body': 'First post'}}
    assert result.errors is None


def test_schema_with_nested_objects_list():

    schema = Schema()

    Post = Object('Post', fields={
        'title': str,
        'body': str,
    })

    @schema.query.field('posts')
    def resolve_posts(root, info) -> List[Post]:
        return [
            Post(title='One', body='First post'),
            Post(title='Two', body='Second post'),
        ]

    # ----------------------------------------------------------------

    result = schema.execute('{posts {title, body}}')

    assert result.data == {'posts': [
        {'title': 'One', 'body': 'First post'},
        {'title': 'Two', 'body': 'Second post'},
    ]}
    assert result.errors is None


def test_basic_schema_with_default_query_object():

    schema = Schema()

    @schema.query.field('hello')
    def resolve_hello(root, info) -> str:
        return 'Hello world'

    # ----------------------------------------------------------------

    result = schema.execute('{hello}')

    assert result.data == {'hello': 'Hello world'}
    assert result.errors is None


def test_omitted_fields_are_filled_with_none():

    schema = Schema()

    MyObj = Object('MyObj', fields={
        'foo': str,
        'bar': str,
    })

    @schema.query.field('my_obj')
    def resolve_my_obj(root, info) -> MyObj:
        return MyObj(foo='FOO')

    # ----------------------------------------------------------------

    result = schema.execute('{ myObj { foo, bar } }')

    assert result.errors is None
    assert result.data == {'myObj': {'foo': 'FOO', 'bar': None}}
