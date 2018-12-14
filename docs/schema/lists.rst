Lists
#####

You can use ``typing.List`` for defining list fields:

.. code-block:: python

    from typing import List

    @Query.field('example_list')
    def resolve_example_list(root, info) -> List[str]:
        return ['A', 'B', 'C']


In alternative, there's a ``pyql.List`` class you can use as well.

Note that you need to instantiate it, rather than subscripting:

.. code-block:: python

    from pyql import List

    @Query.field('example_list')
    def resolve_example_list(root, info) -> List(str):
        return ['A', 'B', 'C']
