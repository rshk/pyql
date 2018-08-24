import graphene
from pyql import pyql


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return 'Hello ' + name


schema = graphene.Schema(query=Query)

app = pyql(schema)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
