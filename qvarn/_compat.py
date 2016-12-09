try:
    # Python 2
    unicode = unicode
except NameError:  # pragma: no cover
    # Python 3
    unicode = str

try:
    # Python 2
    buffer = buffer
except NameError:  # pragma: no cover
    # Python 3
    buffer = memoryview
