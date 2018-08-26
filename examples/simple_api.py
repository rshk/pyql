import asyncio

import graphene
from pyql import pyql


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return 'Hello ' + name


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to):
        for i in range(up_to):
            yield i
            await asyncio.sleep(1.)
        yield up_to


schema = graphene.Schema(query=Query, subscription=Subscription)

app = pyql(schema)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, auto_reload=True)
