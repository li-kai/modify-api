import scrapy
from titlecase import titlecase
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (Identity, Compose,
                                      MapCompose, Join, TakeFirst)
import re


class NtuDetails(scrapy.Item):
    code = scrapy.Field()
    year = scrapy.Field()
    sem = scrapy.Field()
    title = scrapy.Field()
    credit = scrapy.Field()
    gradeType = scrapy.Field()
    department = scrapy.Field()
    prerequisite = scrapy.Field()
    preclusion = scrapy.Field()
    availability = scrapy.Field()
    description = scrapy.Field()
    exam = scrapy.Field()


class NtuLesson(scrapy.Item):
    classNo = scrapy.Field()
    dayText = scrapy.Field()
    lessonType = scrapy.Field()
    weekText = scrapy.Field()
    startTime = scrapy.Field()
    endTime = scrapy.Field()
    venue = scrapy.Field()


class NtuTimetables(scrapy.Item):
    code = scrapy.Field()
    year = scrapy.Field()
    sem = scrapy.Field()
    remark = scrapy.Field()
    timetable = scrapy.Field()
    

    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return repr({"code": self['code']})


def fixHumanWritenText(word):
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


class ModifyLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = Join('')
    year_in = Identity()
    year_out = TakeFirst()
    sem_in = Identity()
    sem_out = TakeFirst()


class NtuDetailsLoader(ModifyLoader):
    joinThenStripWhitespace = Compose(lambda x: ''.join(x), unicode.strip)
    title_in = MapCompose(
        unicode.strip,
        # proper titlecase
        titlecase,
        # turns roman chars to UPPER casing
        lambda x: ' '.join([upperRoman(word) for word in x.split(' ')])
    )

    gradeType_in = MapCompose(filterWord('Grade Type: '))

    prerequisite_in = MapCompose(
        lambda x: u'\n' if x == 'Prerequisite:' else x,
        fixHumanWritenText
    )
    prerequisite_out = joinThenStripWhitespace

    preclusion_in = MapCompose(filterWord('Mutually exclusive with: '))

    availability_in = MapCompose(
        concatenateAvail,
        preventAllCaps
    )
    availability_out = joinThenStripWhitespace
    description_in = MapCompose(
        fixHumanWritenText
    )
    description_out = joinThenStripWhitespace


class NtuTimetablesLoader(ModifyLoader):
    timetable_in = MapCompose()
    timetable_out = Identity()


def parseWeekText(text):
    if text == u'':
        return u'Every week'
    elif '-' in text or ',' in text:
        return text.replace('Wk', 'Weeks ')\
            .replace(',', ', ')
    else:
        return text.replace('Wk', 'Week ')


class NtuLessonLoader(ModifyLoader):
    lessonType_in = MapCompose(lambda x: x[:3])
    weekText_in = MapCompose(unicode.strip, parseWeekText)
    startTime_in = MapCompose(lambda x: x[:2] + ":" + x[2:])
    endTime_in = MapCompose(lambda x: x[:2] + ":" + x[2:])
