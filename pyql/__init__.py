from sanic import Sanic
from sanic_graphql import GraphQLView


def pyql(schema):
    """Create Sanic app exposing a graphql endpoint for the schema.
    """

    app = Sanic()

    app.add_route(GraphQLView.as_view(
        schema=schema, graphiql=True), '/graphql')

    # Optional, for adding batch query support (used in Apollo-Client)
    app.add_route(GraphQLView.as_view(
        schema=schema, batch=True), '/graphql/batch')

    return app
