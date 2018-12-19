Input objects
#############

Input objects are used to pass structured objects as arguments to
queries or mutations.

Create an instance of ``pyql.InputObject``:

.. code-block:: python

    PostInput = InputObject('PostInput', fields={
        'title': NonNull(str),
        'body': str,
    })


An example mutation making use of the input object:

.. code-block:: python

    Post = Object('Post', fields={
        'id': ID,
        'title': str,
        'body': str,
    })

    Mutation = Object('Mutation')

    @Mutation.field('create_post')
    def resolve_create_post(root, info, post: PostInput) -> Post:

        # The ``post`` argument is an instance of PostInput.
        # Attributes are accessible as expected.

        # Let's pretend we stored the data in our database and want to
        # return information about the newly created post:

        return Post(
            id='1',
            title=post.title,
            body=post.body)

    schema = Schema(
        query=Query,
        mutation=Mutation)


A query against the schema might look like this:

.. code-block:: python

    query = """
    mutation createPost($post: PostInput!) {
      createPost(post: $post) {
        id, title, body
      }
    }
    """

    variables = {'post': {'title': 'Hello', 'body': 'Hello world'}}

    schema.execute(query, variables=variables)

    assert result.errors is None
    assert result.data == {
        'createPost': {
            'id': '1',
            'title': 'Hello',
            'body': 'Hello world',
        }
    }
