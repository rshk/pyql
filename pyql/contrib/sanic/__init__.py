from graphql_ws.websockets_lib import WsLibSubscriptionServer
from sanic import Sanic
from sanic_cors import CORS
from sanic_graphql import GraphQLView


def pyql(schema):
    """Create Sanic app exposing a graphql endpoint for the schema.
    """

    app = Sanic()

    CORS(app, automatic_options=True)

    app.add_route(GraphQLView.as_view(
        schema=schema, graphiql=True), '/graphql')

    # Optional, for adding batch query support (used in Apollo-Client)
    app.add_route(GraphQLView.as_view(
        schema=schema, batch=True), '/graphql/batch')

    subscription_server = WsLibSubscriptionServer(schema)

    @app.websocket('/subscriptions', subprotocols=['graphql-ws'])
    async def subscriptions(request, ws):
        await subscription_server.handle(ws)
        return ws

    return app
