Scalar types
############

The following scalar types are currently defiened in the GraphQL spec,
and supported by PyQL:

- ``str`` -> ``String``
- ``int`` -> ``Int``
- ``float`` -> ``Float``
- ``bool`` -> ``Boolean``
- The ``ID`` type, defined as ``pyql.ID`` (there is no equivalent in
  Python). Will accept strings (or ints) as field value.


Non-nulls
=========

Resolver arguments without a default value will be considered
``NonNull`` automatically.

You can explicity wrap a type in ``pyql.NonNull`` for your output
types (although it doesn't make too much sense to validate your output
fields...).


Extra built-in scalar types
===========================

Some more scalar types, not defined by the GraphQL spec, are supported
for convenience:

- ``datetime.datetime``, in ISO 8601 format
- ``datetime.date``, in ISO 8601 format
- ``datetime.time``, in ISO 8601 format


Custom scalar types
===================

- TODO: document how to create / register custom GraphQL scalar types
- TODO: also provide an API to register custom scalar types
