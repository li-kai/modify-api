import scrapy
import re
from tutorial.items import Module


class NtuSpider(scrapy.Spider):
    name = "ntu"
    allowed_domains = ["wish.wis.ntu.edu.sg"]
    start_urls = [
        "https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main_display1?" +
        "acad=2016&semester=1&acadsem=2016;1&r_subj_code=" +
        "ACC" + "&boption=Search"
    ]

    # remove the title
    # and join the strings
    def conditionalConcat(self, listOfStrings, rule):
        result = ''
        for item in listOfStrings:
            if (rule != item):
                result += item
        return result

    def clean(self, str):
        # turns 'man?s to man's and students? to students'
        str = re.sub(r'\?(?=[sS])|(?<=[sS])\?', '\'', str)
        # turns 'for example ? the' to 'for example - the'
        str = re.sub(r' \? ', ' - ', str)
        # turns multiple whitespace to a single space
        str = re.sub('\s +', ' ', str)
        # lastly replace tabs with space and
        # strip starting and ending whitespace
        return str.replace('\t', ' ').strip()

    def parse(self, response):
        hugeListUnprocessed = response.xpath(
            '//tr[position()>1 and position()<last()]'
        )

        # split into giant lists
        modulesListUnprocessed = [[]]
        for item in hugeListUnprocessed:
            if item.extract() == u'<tr>\n<td>\xa0</td>\n</tr>':
                modulesListUnprocessed.append([])
            else:
                modulesListUnprocessed[-1].append(item)

        for mod in modulesListUnprocessed:
            # each mod is a module
            item = Module()
            # first row contains code, title
            # credit and department
            firstRow = mod[0].xpath('.//font/text()').extract()
            item['code'] = firstRow[0]
            item['title'] = firstRow[1]
            item['credit'] = firstRow[2].strip()
            item['department'] = firstRow[3]

            # second row onwards contains prerequisites,
            # gradeType, preclusion and availability
            # which can take up several rows
            prerequisites = []
            gradeType = []
            preclusion = []
            availability = []
            description = []
            for i in xrange(1, len(mod)):
                row = mod[i].xpath('.//font')
                for data in row:
                    requirement = data.xpath('text()').extract()
                    # empty string, skip
                    if not requirement:
                        continue
                    data = data.extract()
                    if ('#FF00FF' in data):
                        prerequisites.extend(requirement)
                    elif ('RED' in data):
                        gradeType.extend(requirement)
                    elif ('BROWN' in data):
                        preclusion.extend(requirement)
                    elif ('GREEN' in data):
                        availability.extend(requirement)
                    elif i == len(mod) - 1:
                        for subdata in requirement:
                            description.append(self.clean(subdata))
                    else:
                        self.logger.warning('Found unexpected %s', data)

            prerequisites = self.conditionalConcat(
                prerequisites, 'Prerequisite:')
            gradeType = self.conditionalConcat(gradeType, 'Grade Type: ')
            preclusion = self.conditionalConcat(
                preclusion, 'Mutually exclusive with: ')
            description = self.conditionalConcat(description, '')

            # replace OR with lower cased ones
            prerequisites = prerequisites.replace(' OR', ' or ')
            # change(corequisite) to change (corequisite)
            prerequisites = re.sub(r'(?<=\S)\(', ' (', prerequisites)

            item['description'] = description.strip()
            item['prerequisite'] = prerequisites
            item['gradeType'] = gradeType
            item['preclusion'] = preclusion
            item['availability'] = availability

            yield item
