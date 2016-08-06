import scrapy
from tutorial.items import (NtuTimetables, NtuTimetablesLoader,
                            NtuLesson, NtuLessonLoader)


class NtuTimetablesSpider(scrapy.Spider):
    name = "ntu_timetables"
    allowed_domains = ["wish.wis.ntu.edu.sg"]
    start_urls = [
        "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1?" +
        "staff_access=false&acadsem=2016;1" +
        "&r_subj_code=ACC" +
        "&boption=Search&r_search_type=F"
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.NtuTimetablesPipeline': 400
        }
    }

    def getText(self, selector):
        text = selector.xpath('./text()').extract()
        if len(text) == 0:
            return u''
        return text[0]

    def getSmallprint(self, text):
        listOfTypes = set()
        if ('*' in text):
            listOfTypes.add('Unrestricted Elective')
        if ('^' in text):
            listOfTypes.add('Self-Paced Course')
        if ('#' in text):
            listOfTypes.add('General Education Prescribed Elective')
        listOfTypes = list(listOfTypes)
        # join them up with some formatting
        result = u'Course is available as '
        if len(listOfTypes) > 1:
            result += ', '.join(listOfTypes[:-1])
            result += ' and ' + listOfTypes[-1]
        elif len(listOfTypes) == 1:
            result += listOfTypes[0]
        else:
            return
        return result

    def getUid(self, listOfSelectors):
        listOfText = []
        for selector in listOfSelectors:
            listOfText.append(self.getText(selector))
        return ''.join([listOfText[1]] + listOfText[3:])

    def parseHeader(self, header, loader):
        # first row contains code, title
        # credit and department
        # just need code and title to extract the smallprint
        firstRow = header[0].xpath('.//font/text()').extract()
        loader.add_value('code', firstRow[0])
        loader.add_value('remark', self.getSmallprint(firstRow[1]))

        # second row onwards either contains prerequisites
        # or module level remarks
        # since we parse prerequisites in NtuDetails, we shall ignore those
        for i in xrange(1, len(header)):
            row = header[i].xpath('//font/text()').extract()
            if 'Remark:' in row:
                loader.add_value('remark', row[1:])

    def parseLesson(self, row, timetable):
        lessonLoader = NtuLessonLoader(NtuLesson(), timetable)
        row[1] = self.getText(row[1])
        row[2] = self.getText(row[2])
        if len(row[2]) == 1:
            row[2] = row[1][0] + row[2]
        lessonLoader.add_value('lessonType', row[1])
        lessonLoader.add_value('classNo', row[2])
        lessonLoader.add_value('dayText', self.getText(row[3]))
        timing = self.getText(row[4]).split('-')
        lessonLoader.add_value('startTime', timing[0])
        lessonLoader.add_value('endTime', timing[1])
        lessonLoader.add_value('venue', self.getText(row[5]))
        lessonLoader.add_value('weekText', self.getText(row[6]))
        return lessonLoader.load_item()

    def parse(self, response):
        hugeListUnprocessed = response.xpath('body/center/table')

        # split into giant lists
        modulesListUnprocessed = []
        # potentially every pair is a module
        i = 0
        while i < len(hugeListUnprocessed):
            moduleHeader = hugeListUnprocessed[i]
            if (i + 1 < len(hugeListUnprocessed) and
                    'border' in hugeListUnprocessed[i + 1].extract()):
                moduleTimetable = hugeListUnprocessed[i + 1]

                modulesListUnprocessed.append([
                    moduleHeader.xpath('.//tr'),
                    moduleTimetable.xpath('.//tr')
                ])
                i += 2
            # rare case, no timetable
            else:
                modulesListUnprocessed.append([moduleHeader.xpath('.//tr')])
                i += 1

        for mod in modulesListUnprocessed:
            # each mod is a module
            loader = NtuTimetablesLoader(NtuTimetables(), mod)

            self.parseHeader(mod[0], loader)

            # timetable contains lessons, which will be added to a set
            # with classNo, dayText, lessonType, start&endTime being the
            # transitive properties
            timetable = mod[1]
            lessonUidSet = set()
            # first row are headers
            for i in xrange(1, len(timetable)):
                row = timetable[i].xpath('.//td/b')
                # construct an uid, leaving out the group & index
                uid = self.getUid(row)
                if uid not in lessonUidSet:
                    lessonUidSet.add(uid)
                    loader.add_value(
                        'timetable', self.parseLesson(row, timetable))

            yield loader.load_item()
