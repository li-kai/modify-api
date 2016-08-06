import scrapy
from titlecase import titlecase
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, Join
import re


class NtuDetails(scrapy.Item):
    code = scrapy.Field()
    title = scrapy.Field()
    credit = scrapy.Field()
    gradeType = scrapy.Field()
    department = scrapy.Field()
    prerequisite = scrapy.Field()
    preclusion = scrapy.Field()
    availability = scrapy.Field()
    description = scrapy.Field()


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
    remark = scrapy.Field()
    timetable = scrapy.Field()


def filterWord(rule):
    return lambda x: None if x == rule else x


def upperRoman(word):
    if word in {'Ii', 'Iii', 'Iv', 'Vi', 'Vii', 'Viii', 'Ix'}:
        word = word.upper()
    return word


class ModifyLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = Join('')


class NtuDetailsLoader(ModifyLoader):
    title_in = MapCompose(
        unicode.strip,
        # proper titlecase
        titlecase,
        # turns roman chars to UPPER casing
        lambda x: ' '.join([upperRoman(word) for word in x.split(' ')])
    )

    gradeType_in = MapCompose(filterWord('Grade Type: '))
    prerequisite_in = MapCompose(
        filterWord('Prerequisite:'),
        # change(corequisite) to change (corequisite)
        lambda x: re.sub(r'(?<=\S)\(', ' (', x),
        # replace OR with lower cased ones
        lambda x: x.replace(' OR', ' or ')
    )
    preclusion_in = MapCompose(filterWord('Mutually exclusive with: '))
    availability_out = Identity()

    description_in = MapCompose(
        # turns 'man?s to man's and students? to students'
        lambda x: re.sub(r'\?(?=[sS])|(?<=[sS])\?', '\'', x),
        # turns 'for example ? the' to 'for example - the'
        lambda x: re.sub(r' \? ', ' - ', x),
        # turns multiple whitespace to a single space
        lambda x: re.sub('\s +', ' ', x),
        # lastly replace tabs with space and
        # strip starting and ending whitespace
        lambda x: x.replace('\t', ' ').strip()
    )


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
    weekText_in = MapCompose(unicode.strip, parseWeekText)
