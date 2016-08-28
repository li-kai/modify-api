import scrapy
from scrapy.http import FormRequest


class NtuExamsSpider(scrapy.Spider):
    name = "ntu_exams"
    allowed_domains = [
        "https://wis.ntu.edu.sg/"
    ]
    year = 2016
    sem = 1
    start_urls = [
        "https://wis.ntu.edu.sg/webexe/owa/exam_timetable_und.main"
    ]
    '''
    custom_settings = {
        'ITEM_PIPELINES': {
            'modify.pipelines.NtuDetailsPipeline': 400
        }
    }
    '''

    def parse(self, response):
        formdata = {'p_plan_no': '31',
                    'bOption': 'Next'}
        return [FormRequest(
            response,
            formdata=formdata,
            callback=self.parse1)]

    def parse1(self, response):
        from scrapy.shell import inspect_response
        inspect_response(response, self)
