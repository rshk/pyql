from collections import namedtuple


class Docstring:

    """Parsed docstring

    Args:
        text:
        params: definition of parameters

    Attributes:
        text: extra text from the docstring
        params (list of Param): definition of arguments
    """

    def __init__(self, text, params=None):
        self.text = text
        self.params = {}
        if params:
            self.params.update(params)


Param = namedtuple('Param', 'name,type,docstring')
