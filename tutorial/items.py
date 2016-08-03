import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, Join
import re


class Module(scrapy.Item):
    code = scrapy.Field()
    title = scrapy.Field()
    credit = scrapy.Field()
    gradeType = scrapy.Field()
    department = scrapy.Field()
    prerequisite = scrapy.Field()
    preclusion = scrapy.Field()
    availability = scrapy.Field()
    description = scrapy.Field()


def filterWord(rule):
    return lambda x: None if x == rule else x


def cleanPrerequisite(x):
    return re.sub(r'(?<=\S)\(', ' (', x)


class ModuleLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = Join('')

    title_in = MapCompose(unicode.title, unicode.strip)

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
