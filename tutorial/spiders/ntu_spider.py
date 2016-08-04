import scrapy
import re
from tutorial.items import Module, ModuleLoader


class NtuSpider(scrapy.Spider):
    name = "ntu"
    allowed_domains = ["wish.wis.ntu.edu.sg"]
    start_urls = [
        "https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main_display1?" +
        "acad=2016&semester=1&acadsem=2016;1&r_subj_code=" +
        "ACC" + "&boption=Search"
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.ModulesPipeline': 400
        }
    }

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
            loader = ModuleLoader(Module(), mod)
            # first row contains code, title
            # credit and department
            firstRow = mod[0].xpath('.//font/text()').extract()
            loader.add_value('code', firstRow[0])
            loader.add_value('title', firstRow[1])
            loader.add_value('credit', firstRow[2])
            loader.add_value('department', firstRow[3])

            # second row onwards contains prerequisites,
            # gradeType, preclusion and availability
            # which can take up several rows
            for i in xrange(1, len(mod)):
                row = mod[i].xpath('.//font')
                for data in row:
                    requirement = data.xpath('text()').extract()
                    # empty string, skip
                    if not requirement:
                        continue
                    data = data.extract()
                    if ('#FF00FF' in data):
                        loader.add_value('prerequisite', requirement)
                    elif ('RED' in data):
                        loader.add_value('gradeType', requirement)
                    elif ('BROWN' in data):
                        loader.add_value('preclusion', requirement)
                    elif ('GREEN' in data):
                        loader.add_value('availability', requirement)
                    elif i == len(mod) - 1:
                        loader.add_value('description', requirement)
                    else:
                        self.logger.warning('Found unexpected %s', data)
            yield loader.load_item()
