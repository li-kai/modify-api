import scrapy
from tutorial.items import Details, NtuDetailsLoader


class NtuDetailsSpider(scrapy.Spider):
    name = "ntu_details"
    allowed_domains = ["wish.wis.ntu.edu.sg"]
    year = 2016
    sem = 1
    start_urls = [
        "https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main_display1?"
        "acad=%(year)s&semester=%(sem)s&acadsem=%(year)s;1&r_subj_code="
        "&boption=Search"
        % {'year': year, "sem": sem}
    ]
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.NtuDetailsPipeline': 400
        }
    }

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
            loader = NtuDetailsLoader(Details(), mod)
            # first row contains code, title
            # credit and department
            firstRow = mod[0].xpath('.//font/text()').extract()
            loader.add_value('year', self.year)
            loader.add_value('sem', self.sem)
            loader.add_value('code', firstRow[0])
            loader.add_value('title', firstRow[1])
            loader.add_value('credit', firstRow[2])
            loader.add_value('department', firstRow[3])

            # second row onwards contains prerequisites,
            # remarks, preclusion and availability
            # which can take up several rows
            for i in xrange(1, len(mod)):
                row = mod[i].xpath('.//font')
                for data in row:
                    requirement = data.xpath('text()').extract()
                    # empty string, skip
                    if not requirement:
                        continue
                    data = data.extract()
                    if ('color="#FF00FF"' in data):
                        loader.add_value('prerequisite', requirement)
                    elif ('color="RED"' in data):
                        loader.add_value('remarks', requirement)
                    elif ('color="BROWN"' in data):
                        loader.add_value('preclusion', requirement)
                    elif ('color="GREEN"' in data):
                        loader.add_value('availability', requirement)
                    elif i == len(mod) - 1:
                        loader.add_value('description', requirement)
                    '''else:
                        self.logger.warning('Found unexpected %s', data)
                    '''
            yield loader.load_item()
