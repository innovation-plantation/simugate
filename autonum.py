import itertools

'''Two functions:
automum.get('foo') returns foo_1, etc.
after autonum.delete('foo_1') or autonum.delete('foo',1) foo_1 can be reused
'''

words = set()


def rootword(word):
    chop = word.rsplit('_')
    return word if len(chop) > 1 and not chop[1].isdigit() else chop[0]
    '''
    :param word:
    :return: the part of the word without the suffix _000  (where 000 is any number of digits)
    '''


def get(word):
    '''
    make the word unique by appending a numbered suffix as necessary
    :param word: such as 'foo'
    :return: word with suffix such as 'foo_1'
    '''
    global words
    if word not in words:
        words.add(word)
        return word
    # chop = word.rsplit('_')
    root = rootword(word)  # word if len(chop)>1 and not chop[1].isdigit() else chop[0]
    for n in itertools.count(1):
        candidate = '%s_%d' % (root, n)
        if candidate in words: continue
        words.add(candidate)
        return candidate


def delete(word):
    '''
    Allow a number to be reused with a word by get
    :param word: such as 'foo' or 'foo_1'
    '''
    global words
    if word in words: words.discard(word)
