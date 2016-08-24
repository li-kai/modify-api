import scrapy
from utils import *
from titlecase import titlecase
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (Identity, Compose,
                                      MapCompose, Join, TakeFirst)


class Details(scrapy.Item):
    """General details item for both unis."""
    code = scrapy.Field()
    year = scrapy.Field()
    sem = scrapy.Field()
    title = scrapy.Field()
    credit = scrapy.Field()
    department = scrapy.Field()
    remarks = scrapy.Field()
    prerequisite = scrapy.Field()
    preclusion = scrapy.Field()
    availability = scrapy.Field()
    description = scrapy.Field()
    exam_time = scrapy.Field()
    exam_venue = scrapy.Field()
    exam_duration = scrapy.Field()


class Lesson(scrapy.Item):
    """General lesson item for both unis."""
    class_no = scrapy.Field()
    day_text = scrapy.Field()
    lesson_type = scrapy.Field()
    week_text = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    venue = scrapy.Field()


class NusModule(Details):
    """
    Item containing all the information
    for a single module for NUS, because
    everything is contained nicely thanks
    to NUSMODS.
    """
    timetable = scrapy.Field()


class NtuTimetables(scrapy.Item):
    """
    Item containing all the lessons for a
    single module for NTU. Does not contain
    details for the module.
    """
    code = scrapy.Field()
    year = scrapy.Field()
    sem = scrapy.Field()
    remark = scrapy.Field()
    timetable = scrapy.Field()
    '''
    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return repr({"code": self['code']})
    '''


class ModifyLoader(ItemLoader):
    """
    Generalized loader for all loaders below
    """
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = Join('')
    year_in = Identity()
    year_out = TakeFirst()
    sem_in = Identity()
    sem_out = TakeFirst()


class NtuDetailsLoader(ModifyLoader):
    """
    Parses all the details to the required form for
    input into database.
    """
    joinThenStripWhitespace = Compose(lambda x: ''.join(x), unicode.strip)
    title_in = MapCompose(
        unicode.strip,
        # proper titlecase
        titlecase,
        # turns roman chars to UPPER casing
        lambda x: ' '.join([upperRoman(word) for word in x.split(' ')])
    )

    grade_type_in = MapCompose(filterWord('Grade Type: '))

    prerequisite_in = MapCompose(
        lambda x: u'\n' if x == 'Prerequisite:' else x,
        fixHumanWrittenText
    )
    prerequisite_out = joinThenStripWhitespace

    preclusion_in = MapCompose(filterWord('Mutually exclusive with: '))

    availability_in = MapCompose(
        concatenateAvail,
        preventAllCaps
    )
    availability_out = joinThenStripWhitespace
    description_in = MapCompose(fixHumanWrittenText)
    description_out = joinThenStripWhitespace
    remarks_in = MapCompose(lambda x: x + u'\n')


class NusLoader(ModifyLoader):
    """
    Most details are nicely filed out thanks to NUSMODS, however
    some fields differ in format needed.
    """

    joinThenStripWhitespace = Compose(lambda x: ''.join(x), unicode.strip)
    title_in = MapCompose(
        unicode.strip,
        # proper titlecase
        titlecase,
        # turns roman chars to UPPER casing
        lambda x: ' '.join([upperRoman(word) for word in x.split(' ')])
    )

    department_in = MapCompose(titlecase, unicode.strip)

    description_in = MapCompose(fixHumanWrittenText)
    description_out = joinThenStripWhitespace

    remarks_in = MapCompose(lambda x: x + u'\n')
    remarks_out = joinThenStripWhitespace
    exam_duration_in = MapCompose(lambda x: x[0] + u'T' + x[1:])

    timetable_in = MapCompose()
    timetable_out = Identity()


class NtuTimetablesLoader(ModifyLoader):
    timetable_in = MapCompose()
    timetable_out = Identity()

    remark_in = MapCompose(lambda x: x + u'\n')
    remark_out = Join('')


class LessonLoader(ModifyLoader):
    lesson_type_in = MapCompose(lambda x: x[:3], unicode.upper)
    day_text_in = MapCompose(lambda x: x[:3], unicode.upper)
    week_text_in = MapCompose(unicode.strip, parseWeekText)
    start_time_in = MapCompose(lambda x: x[:2] + ":" + x[2:])
    end_time_in = MapCompose(lambda x: x[:2] + ":" + x[2:])
