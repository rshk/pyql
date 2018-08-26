PyQL
####

Python web framework for GraphQL.

Actually based on Sanic, provides dependencies and configuration to
get up and running quickly.

Uses Graphene for the GraphQL side of it.


Features
========

- Quickly get a GraphQL API up and running. All the web-framework side
  stuff is already configured for you.
- Support for GraphQL subscriptions, via websockets.
- Websocket support during development, along with realoading.


Usage example
=============


.. code-block:: python

    from pyql import pyql

    app = pyql(schema)  # Schema is a Graphene schema


To run a development server:


.. code-block:: python

    app.run(host='0.0.0.0', port=5000, debug=True, auto_reload=True)


Usage with Apollo Client
========================

Have a look at ``experiments/web-client`` for a simple example on
using Apollo client from a React app.


Running the examples
====================

Install this repository in a virtualenv using your favourite tools, for example::

    virtualenv --python=/usr/bin/python3.7 --no-site-packages .venv
    source .venv/bin/activate
    python setup.py develop


Start the API server::

    python examples/simple_api.py


Install dependencies for the web client::

    cd ./examples/web-client
    yarn install


Start a development server for the web client::

    yarn start


Then visit http://localhost:8000
