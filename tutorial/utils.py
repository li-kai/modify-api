import re


def fixHumanWrittenText(word):
    # 'change(corequisite)' to 'change (corequisite)'
    word = re.sub(r'(?<=\S)\(', ' (', word)
    word = word.replace(' OR', ' or ')
    # replace tabs with space
    word = word.replace('\t', ' ')
    # turns multiple whitespace to a single space
    word = re.sub('\s +', ' ', word)
    # add space before . , ; chars as needed
    word = re.sub(r'([\.|;|,])(?=\w)', r'\1 ', word)
    # minor fix
    word = word.replace('i. e. ', 'i.e. ')
    # turns 'man?s to man's and students? to students'
    word = re.sub(r'\?(?=[sS])|(?<=[sS])\?', '\'', word)
    # turns 'for example ? the' to 'for example - the'
    word = re.sub(r' \? ', ' - ', word)
    word = preventAllCaps(word)
    return word


def filterWord(rule):
    return lambda x: None if x == rule else x


def upperRoman(word):
    if word in {'Ii', 'Iia', 'Iib', 'Iii', 'Iv', 'Vi', 'Vii', 'Viii', 'Ix'}:
        word = word.upper()
    return word


def concatenateAvail(word):
    if 'Not available' in word:
        return u'\n' + word
    return word


def preventAllCaps(sentence):
    if sentence.isupper() and len(sentence) > 6 and '.' in sentence:
        return unicode.capitalize(sentence)
    return sentence


def parseWeekText(text):
    if text == u'' or text == u'Every Week':
        return u'Every week'
    elif '-' not in text and ',' in text and len(text) > 5:
        return commaSeparatedToRange(text)
    elif '-' in text or ',' in text:
        return text.replace('Wk', 'Weeks ')\
            .replace(',', ', ')
    else:
        return text.replace('Wk', 'Week ')


def commaSeparatedToRange(text):
    """ outputs '1,2,3,4,5' to '1-5' """
    # get rid of duplicates and convert to array of numbers
    noDuplicates = set(text.split(','))
    # check if every thing is a digit and convert it to list of numbers
    if all([x.strip().isdigit() for x in noDuplicates]):
        numberArray = [int(x) for x in noDuplicates]
        # sort in ascender order
        numberArray.sort()

    # return back original string
    else:
        return text

    # 2d array, where each sub array is a range
    arr = [[numberArray[0]]]
    index = 0
    for i in xrange(1, len(numberArray)):
        num = numberArray[i]
        # check if number belongs in current sub array
        if num == (arr[index][-1] + 1):
            arr[index].append(num)
        # create a new one
        else:
            index += 1
            arr[index] = [num]

    # join first and last if it contains more than 1 element
    # then join the ranges to form string
    def compact(range):
        if len(range) > 1:
            return '%s-%s' % (range[0], range[-1])
        return range[0]
    return ', '.join(map(compact, arr))
