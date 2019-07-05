from pyql import ID, Object, Schema, InputObject, NonNull


def test_input_objects():

    Post = Object('Post', fields={
        'id': ID,
        'title': str,
        'body': str,
    })

    PostInput = InputObject('PostInput', fields={
        'title': NonNull(str),
        'body': str,
    })

    Query = Object('Query', fields={'dummy': str})
    Mutation = Object('Mutation')

    @Mutation.field('create_post')
    def resolve_create_post(root, info, post: PostInput) -> Post:
        return Post(
            id='1',
            title=post.title,
            body=post.body)

    schema = Schema(
        query=Query,
        mutation=Mutation)

    result = schema.execute("""
    mutation createPost($post: PostInput!) {
      createPost(post: $post) {
        id, title, body
      }
    }
    """, variables={'post': {'title': 'Hello', 'body': 'Hello world'}})

    assert result.errors is None
    assert result.data == {
        'createPost': {
            'id': '1',
            'title': 'Hello',
            'body': 'Hello world',
        }
    }


def test_input_objects_field_names_are_converted():

    MyInput = InputObject('MyInput', fields={
        'some_field_name': str,
    })

    # Need at least one query, for some reason...
    schema = Schema(query=Object('Query', {'q': str}))

    @schema.mutation.field('do_something')
    def resolve_do_something(root, info, obj: MyInput) -> str:
        return obj.some_field_name

    result = schema.execute("""
    mutation doSomething($obj: MyInput!) {
        doSomething(obj: $obj)
    }
    """, variables={'obj': {'someFieldName': 'HELLO'}})

    assert result.errors is None
    assert result.data == {
        'doSomething': 'HELLO'
    }
