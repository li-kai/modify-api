# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


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
