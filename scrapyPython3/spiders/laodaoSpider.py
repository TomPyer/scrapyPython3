# -*- coding: utf-8 -*-
import scrapy
import json
import logging

from scrapy import Selector
from scrapy_splash import SplashRequest
from scrapyPython3.items import YzyQuestionItem

class LaodaospiderSpider(scrapy.Spider):
    name = 'laodaoSpider'
    # allowed_domains = ['www.laodao.com']
    start_urls = ['http://www.laodao.so/']
    last_id = 292771
    last_page = 1

    def parse(self, response):
        while self.last_id > 292700:
            url = 'http://ngjv4.laodao.so/ASHX/bbs_card.ashx?action=jzlist&version=pc&CropID=-1&lastid=%d&pgsize=20&pgindex=%d&pckey=' % (self.last_id, self.last_page)
            self.last_page += 1
            self.last_id -= 20
            with open('laodao.txt', 'a') as f:
                f.write(''.join([str(self.last_page), '-------------', str(self.last_id), '\n']))
            yield SplashRequest(url, self.body_parse, args={"wait": 0.3})

    def body_parse(self, response):
        sel = Selector(response)
        # with open('test.txt', 'wb') as f:
        #     f.write(sel.xpath('//body/pre/text()').extract_first().encode('utf-8'))
        body = json.loads(sel.xpath('//body/pre/text()').extract_first().encode('utf-8'))
        crop_dic = {}
        if body['code'] in ['200', 200]:
            data = body['datas']
            if data['CropID']:
                crop = crop_dic[data['CropID']]
            else:
                crop = ''
            answer_url = 'http://www.laodao.so/forum/info/%d' % data['last_id']
            yield SplashRequest(answer_url, self.answer_parse, meta={'crop': crop, 'id': data['last_id'],
                                                                     'question_info': data['contents'], })
        else:
            logging.error('this code is not 200 ! url:  ', response.url)

    def answer_parse(self, response):
        sel = Selector(response)
        item = YzyQuestionItem()
        div = sel.xpath('//div[@class="pl-content"]/text()').extract()
