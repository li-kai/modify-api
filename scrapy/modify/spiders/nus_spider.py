import scrapy
import json
from modify.items import (
    NusModule, NusLoader, LessonLoader, Lesson)
from settings import YEAR, SEM

class NusDetailsSpider(scrapy.Spider):
    name = "nus_details"
    allowed_domains = ["api.nusmods.com"]
    start_urls = [
        "http://api.nusmods.com/%(year_one)s-%(year_two)s/%(sem)s/modules.json"
        % {'year_one': YEAR, 'year_two': YEAR + 1, "sem": SEM}
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'modify.pipelines.NusDetailsPipeline': 400
        }
    }

    def addIfPresent(self, field, loader, module, key):
        if key in module:
            loader.add_value(field, module[key])

    def parseDetails(self, mod, loader):
        # each mod is a module
        loader.add_value('year', YEAR)
        loader.add_value('sem', SEM)
        loader.add_value('code', mod['ModuleCode'])
        loader.add_value('title', mod['ModuleTitle'])
        loader.add_value('credit', mod['ModuleCredit'])
        loader.add_value('department', mod['Department'])

        if 'ModuleDescription' in mod:
            loader.add_value('description', mod['ModuleDescription'])
        else:
            loader.add_value('description', u'')
        self.addIfPresent('prerequisite', loader, mod, 'Prerequisite')
        self.addIfPresent('preclusion', loader, mod, 'Preclusion')
        self.addIfPresent('exam_time', loader, mod, 'ExamDate')
        self.addIfPresent('exam_venue', loader, mod, 'ExamVenue')
        self.addIfPresent('exam_duration', loader, mod, 'ExamDuration')
        if 'corequisite' in mod:
            loader.add_value('remarks', u'Corequisite: ' + mod['corequisite'])
        if 'Workload' in mod:
            loader.add_value('remarks', u'Workload: ' + mod['Workload'])
        if 'ExamOpenBook' in mod and mod['ExamOpenBook']:
            loader.add_value('remarks', u'Exam is open book.')

        return loader.load_item()

    def parseTimetable(self, timetable, loader):
        # each les is a lesson
        for les in timetable:
            lesson_loader = LessonLoader(Lesson())
            lesson_loader.add_value('class_no', les['ClassNo'])
            lesson_loader.add_value('day_text', les['DayText'])
            lesson_loader.add_value('lesson_type', les['LessonType'])
            lesson_loader.add_value('week_text', les['WeekText'])
            lesson_loader.add_value('start_time', les['StartTime'])
            lesson_loader.add_value('end_time', les['EndTime'])
            lesson_loader.add_value('venue', les['Venue'])
            loader.add_value('timetable', lesson_loader.load_item())

    def parse(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        for mod in jsonresponse:
            # each mod is a module
            loader = NusLoader(NusModule(), mod)
            self.parseDetails(mod, loader)
            if 'Timetable' in mod:
                self.parseTimetable(mod['Timetable'], loader)
            yield loader.load_item()
