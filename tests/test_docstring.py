from pyql.docstring import parse_docstring
from pyql.docstring.ast import Param
from pyql.docstring.tokenizer import Block, TextBlock, tokenize_docstring


class Test_tokenize_docstring:

    def test_empty_text(self):
        docstring = """
        """

        assert list(tokenize_docstring(docstring)) == []

    def test_single_text_line(self):
        docstring = """
        This is a single line of text
        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock(['This is a single line of text'])
        ]

    def test_single_text_section(self):
        docstring = """
        First line of text
        Second line of text
        Third line of text
        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock([
                'First line of text',
                'Second line of text',
                'Third line of text'])
        ]

    def test_single_text_section_two_paragraphs(self):
        docstring = """
        First line of text
        Second line of text

        Third line of text
        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock([
                'First line of text',
                'Second line of text',
                '',
                'Third line of text'])
        ]

    def test_extra_whitelines_are_stripped(self):
        docstring = """


        Single line of text


        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock(['Single line of text'])
        ]

    def test_parse_single_named_section(self):
        docstring = """
        Example:
            Hello world
        """

        assert list(tokenize_docstring(docstring)) == [
            Block('Example', ['Hello world'])
        ]

    def test_parse_text_then_section(self):
        docstring = """
        Some text here
        Example:
            Hello world
        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock(['Some text here']),
            Block('Example', ['Hello world'])
        ]

    def test_parse_text_then_whiteline_then_section(self):
        docstring = """
        Some text here

        Example:
            Hello world
        """

        assert list(tokenize_docstring(docstring)) == [
            TextBlock(['Some text here']),
            Block('Example', ['Hello world']),
        ]

    def test_parse_section_then_text(self):
        docstring = """
        Example:
            Hello world
        Some text here
        """

        assert list(tokenize_docstring(docstring)) == [
            Block('Example', ['Hello world']),
            TextBlock(['Some text here']),
        ]

    def test_parse_section_then_whiteline_then_text(self):
        docstring = """
        Example:
            Hello world

        Some text here
        """

        assert list(tokenize_docstring(docstring)) == [
            Block('Example', ['Hello world']),
            TextBlock(['Some text here']),
        ]

    def test_parse_two_sections(self):
        docstring = """
        Example:
            foo bar
        Hello:
            world
        """

        assert list(tokenize_docstring(docstring)) == [
            Block('Example', ['foo bar']),
            Block('Hello', ['world']),
        ]

    def test_section_with_inline_text(self):
        docstring = """
        Example: Hello world
        """

        assert list(tokenize_docstring(docstring)) == [
            Block('Example', ['Hello world']),
        ]


class Test_parse_docstring:

    def test_parse_no_args(self):
        docstring = """
        Hello world
        """

        parsed = parse_docstring(docstring)
        assert parsed.text == 'Hello world\n'
        assert parsed.params == {}

    def test_parse_two_args_no_type(self):
        docstring = """
        Hello world

        Args:
            foo: A foo
            bar: A bar
        """

        parsed = parse_docstring(docstring)
        assert parsed.text == 'Hello world\n'
        assert parsed.params == {
            'foo': Param('foo', None, 'A foo'),
            'bar': Param('bar', None, 'A bar'),
        }

    def test_parse_two_args_with_type(self):
        docstring = """
        Hello world

        Args:
            foo (str): A foo
            bar (int): A bar
        """

        parsed = parse_docstring(docstring)
        assert parsed.text == 'Hello world\n'
        assert parsed.params == {
            'foo': Param('foo', 'str', 'A foo'),
            'bar': Param('bar', 'int', 'A bar'),
        }
