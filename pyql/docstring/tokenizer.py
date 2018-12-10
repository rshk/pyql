import re
import textwrap
from collections import namedtuple


def tokenize_docstring(text):
    """Tokenize a docstring into blocks.

    Args:
        text: docstring in Google-style format

    Yields:
        Either a Block or TextBlock, for each block encountered in
        the text.
    """

    current_section = None

    for token in _tokenize_docstring(text):

        if isinstance(token, T_SECTION_HEADER):
            if current_section is not None:
                yield current_section.export()
            current_section = Block(
                token.name,
                [token.text] if token.text else None)
            continue

        if current_section is None:
            current_section = TextBlock()

        if isinstance(token, T_TEXT):
            # Back ton indent 0: end of indented block
            if token.indent == 0 and isinstance(current_section, Block):
                yield current_section.export()
                current_section = TextBlock()

            current_section.append(' ' * token.indent + token.text)
            continue

        if isinstance(token, T_EMPTY) and current_section is not None:
            current_section.append('')

    if current_section is not None:
        yield current_section.export()


def _tokenize_docstring(text):
    text = textwrap.dedent(text).strip()
    for line in text.splitlines():
        yield _make_token(line.rstrip())


def _make_token(line):
    if not line:
        return T_EMPTY()
    indent, text = _parse_indent(line)
    if indent == 0:
        is_header, header_name, header_text = _parse_section_header(text)
        if is_header:
            return T_SECTION_HEADER(indent, header_name, header_text)
    return T_TEXT(indent, text)


T_EMPTY = namedtuple('T_EMPTY', '')
T_SECTION_HEADER = namedtuple('T_SECTION_HEADER', 'indent,name,text')
T_TEXT = namedtuple('T_TEXT', 'indent,text')


class TextBlock:

    def __init__(self, lines=None):
        self.lines = []
        if lines is not None:
            self.lines.extend(lines)

    def append(self, text):
        self.lines.append(text)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            repr(self.lines))

    def __eq__(self, other):
        return self is other or (
            type(self) == type(other)
            and self.lines == other.lines)

    def export(self):
        text = '\n'.join(self.lines).rstrip()
        dedented = textwrap.dedent(text)
        return TextBlock(dedented.splitlines())


class Block:

    def __init__(self, name, lines=None):
        self.name = name
        self.lines = []
        if lines is not None:
            self.lines.extend(lines)

    def append(self, text):
        self.lines.append(text)

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__,
            repr(self.name), repr(self.lines))

    def __eq__(self, other):
        return self is other or (
            type(self) == type(other)
            and self.name == other.name
            and self.lines == other.lines)

    def export(self):
        text = '\n'.join(self.lines).rstrip()
        dedented = textwrap.dedent(text)
        return Block(self.name, dedented.splitlines())


def _parse_indent(text):
    m = re.match(r'^(?P<indent>\s*)(?P<text>.*)$', text)
    return len(m.group('indent')), m.group('text')


def _parse_section_header(text):
    section_regex = re.compile(
        r'^\s*(?P<name>.+?):'

        # Allow extra text to be defined inline
        r'\s*(?P<text>.*?)\s*$')

    m = section_regex.match(text)
    if m is None:
        return False, None, None
    return True, m.group('name'), m.group('text')
