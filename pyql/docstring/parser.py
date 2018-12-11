"""Parse resolver docstring.

This is used to extract documentation about fields and arguments from
the docstring.

Only supports Google-style docstrings at the moment, as they're the
most readable format.
"""

import re
import textwrap
from collections import namedtuple

from .tokenizer import Block, TextBlock, tokenize_docstring
from .ast import Docstring, Param


def parse_docstring(text):
    blocks = (parse_section(x) for x in tokenize_docstring(text))

    text_blocks = []
    params = {}

    for block in blocks:

        if isinstance(block, TextSection):
            text_blocks.append(block.text.rstrip() + '\n')

        elif isinstance(block, ParamsSection):
            for item in block.args:
                params[item.name] = item

    return Docstring(text='\n'.join(text_blocks), params=params)


TextSection = namedtuple('TextSection', 'text')
ParamsSection = namedtuple('ParamsSection', 'args')


def parse_section(section):
    if isinstance(section, TextBlock):
        return TextSection('\n'.join(section.lines) + '\n')

    assert isinstance(section, Block)
    sect_name = section.name.lower()
    _parse_section = SECTIONS.get(sect_name, parse_generic_section)
    return _parse_section(section)


def parse_parameters_section(section):
    """Parse a "parameters" section.

    Example:

        Args:
            foo: a foo argument
            bar (str): a bar argument
    """

    text = '\n'.join(section.lines)
    args = []
    for token in tokenize_docstring(text):
        if not isinstance(token, Block):
            raise ValueError('Bad parameters docstring')

        m = re.match(
            r'^(?P<name>.*?)\s*'
            r'(?:\((?P<type>.*?)\))?\s*$',
            token.name)

        name = m.group('name')
        type_ = m.group('type')
        text = textwrap.dedent('\n'.join(token.lines))

        args.append(Param(name, type_, text))
    return ParamsSection(args)


def parse_generic_section(section):
    """Any other section

    Will simply return a text section, similar to the original
    docstring.
    """

    text = '\n'.join('    {}'.format(x) for x in section.lines)
    return TextSection('{}:\n{}'.format(section.name, text))


SECTIONS = {
    'args': parse_parameters_section,
    'arguments': parse_parameters_section,
    # 'attention': partial(parse_admonition, 'attention'),
    # 'attributes': self._parse_attributes_section,
    # 'caution': partial(parse_admonition, 'caution'),
    # 'danger': partial(parse_admonition, 'danger'),
    # 'error': partial(parse_admonition, 'error'),
    # 'example': self._parse_examples_section,
    # 'examples': self._parse_examples_section,
    # 'hint': partial(parse_admonition, 'hint'),
    # 'important': partial(parse_admonition, 'important'),
    # 'keyword args': self._parse_keyword_arguments_section,
    # 'keyword arguments': self._parse_keyword_arguments_section,
    # 'methods': self._parse_methods_section,
    # 'note': partial(parse_admonition, 'note'),
    # 'notes': self._parse_notes_section,
    # 'other parameters': self._parse_other_parameters_section,
    'parameters': parse_parameters_section,
    # 'return': self._parse_returns_section,
    # 'returns': self._parse_returns_section,
    # 'raises': self._parse_raises_section,
    # 'references': self._parse_references_section,
    # 'see also': self._parse_see_also_section,
    # 'tip': partial(parse_admonition, 'tip'),
    # 'todo': partial(parse_admonition, 'todo'),
    # 'warning': partial(parse_admonition, 'warning'),
    # 'warnings': partial(parse_admonition, 'warning'),
    # 'warns': self._parse_warns_section,
    # 'yield': self._parse_yields_section,
    # 'yields': self._parse_yields_section,

    # TODO: deprecated section
}
