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
