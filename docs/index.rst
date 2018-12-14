.. PyQL documentation master file, created by
   sphinx-quickstart on Tue Dec 11 15:32:23 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyQL's documentation!
################################

PyQL provides a high-level API for defining GraphQL_ schemas.

It uses graphql-core_ behind the scenes, which means generated schemas
are fully compatible with that library.

**What about Graphene?**

Graphene_ serves a similar purpose, but its object-based API is not
great for defining large schemas. Also, there are parts that are
confusing / error prone (eg. mixing field attributes with field
constructor parameters).

Also, we're trying to use Python facilities as much as possible for
the schema definition (type annotations in particular), which makes
the library friendlier to anyone already familiar with the Python
language (no need to invent / learn new concepts).

This of course means the **minimum supported Python version is 3.5**,
as type hints were first supported in that release.

.. _GraphQL: https://graphql.org/
.. _Graphene: https://graphene-python.org/
.. _graphql-core: https://github.com/graphql-python/graphql-core/


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   schema/index



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
