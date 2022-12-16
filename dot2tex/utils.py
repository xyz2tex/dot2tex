from . import dotparsing

# Inch to bp conversion factor
INCH2BP = 72.0
SPECIAL_CHARS = ['$', '\\', '%', '_', '#', '{', r'}', '^', '&']
SPECIAL_CHARS_REPLACE = [r'\$', r'$\backslash$', r'\%', r'\_', r'\#',
                         r'\{', r'\}', r'\^{}', r'\&']
charmap = dict(zip(SPECIAL_CHARS, SPECIAL_CHARS_REPLACE))


def mreplace(s, chararray, newchararray):
    for a, b in zip(chararray, newchararray):
        s = s.replace(a, b)
    return s


def escape_texchars(string):
    r"""Escape the special LaTeX-chars %{}_^

    Examples:

    >>> escape_texchars('10%')
    '10\\%'
    >>> escape_texchars('%{}_^\\$')
    '\\%\\{\\}\\_\\^{}$\\backslash$\\$'
    """
    return "".join([charmap.get(c, c) for c in string])


def tikzify(s):
    if s.strip():
        return mreplace(s, r'\,:.()', '-+_*{}')
    else:
        return "d2tnn%i" % (len(s) + 1)


def nsplit(seq, n=2):
    """Split a sequence into pieces of length n

    If the length of the sequence isn't a multiple of n, the rest is discarded.
    Note that nsplit will strings into individual characters.

    Examples:
    >>> nsplit('aabbcc')
    [('a', 'a'), ('b', 'b'), ('c', 'c')]
    >>> nsplit('aabbcc',n=3)
    [('a', 'a', 'b'), ('b', 'c', 'c')]

    # Note that cc is discarded
    >>> nsplit('aabbcc',n=4)
    [('a', 'a', 'b', 'b')]
    """
    return [xy for xy in zip(*[iter(seq)] * n)]


def chunks(s, cl):
    """Split a string or sequence into pieces of length cl and return an iterator"""
    for i in range(0, len(s), cl):
        yield s[i:i + cl]


def replace_tags(template, tags, tagsreplace):
    """Replace occurrences of tags with tagsreplace

    Example:
    >>> replace_tags('a b c d',('b','d'),{'b':'bbb','d':'ddd'})
    'a bbb c ddd'
    """
    s = template
    for tag in tags:
        replacestr = tagsreplace.get(tag, '')
        if not replacestr:
            replacestr = ''
        s = s.replace(tag, replacestr)
    return s


def getboolattr(item, key, default):
    if str(getattr(item, key, '')).lower() == 'true':
        return True
    else:
        return False


def smart_float(number):
    if type(number) is str: # handle newlines
        number = number.strip('\\\r\n')
    number_as_string = "%s" % float(number)
    if 'e' in number_as_string:
        return "%.4f" % float(number)
    else:
        return number_as_string


def is_multiline_label(drawobject):
    # https://graphviz.gitlab.io/_pages/doc/info/attrs.html#k:escString
    if getattr(drawobject, "texlbl", None):
        return False

    label = getattr(drawobject, "label", "")
    return any(x in label for x in [r"\n", r"\l", r"\r"])


class EndOfGraphElement(object):
    def __init__(self):
        pass


def get_all_graph_elements(graph, l=None):
    """Return all nodes and edges, including elements in subgraphs"""
    if not l:
        l = []
        outer = True
        l.append(graph)
    else:
        outer = False
    for element in graph.allitems:
        if isinstance(element, dotparsing.DotSubGraph):
            l.append(element)
            get_all_graph_elements(element, l)
        else:
            l.append(element)

    if outer:
        return l
    else:
        l.append(EndOfGraphElement())