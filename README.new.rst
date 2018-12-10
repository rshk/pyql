PyQL
####

A better library for defining GraphQL schemas in Python.

::

    from typing import List
    import pyql

    # Base for the schema

    schema = pysql.Schema()  # query/mutation/subscription/directives/types

    # Define our objects

    User = schema.Object(
        'User',
        description='A user',
        fields={
            'id': int,
            'name': str,
            'picture': None,  # defined later
        },
    )

    @User.field('picture')
    def resolve_note_author(root, info, size: int = 50) -> str:
        return User(id=..., name=...)

    Note = schema.Object(
        'Note',
        description='A note',
        fields={
            'id': int,
            'title': str,
            'body': str,
            'author_id': int,
            'author': User,  # Defined later though
        },
        interfaces=[],
    )

    @Note.field('author')
    def resolve_note_author(root, info) -> User:
        return User(id=..., name=...)

    schema.query.field()
    def list_notes() -> List[Note]:
        pass

    schema.query.field()
    def get_note(id: int):
        pass
