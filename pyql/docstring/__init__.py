"""Parse resolver docstring.

This is used to extract documentation about fields and arguments from
the docstring.

Only supports Google-style docstrings at the moment, as they're the
most readable format.
"""

from .parser import parse_docstring  # noqa
