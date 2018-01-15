# -*- coding: utf-8 -*-
import scrapy
import logging

from scrapy_splash import SplashRequest
from scrapy import Selector
from scrapyPython3.items import YzyQuestionItem


class YzyspiderSpider(scrapy.Spider):
    name = 'yzySpider'
    # allowed_domains = ['https://www.yzyy365.com']
    start_urls = ['https://www.yzyy365.com/']

    def parse(self, response):
        for page_num in range(1, 51):
            next_url = 'https://www.yzyy365.com/s/%d.html?k=' % page_num
            yield SplashRequest(next_url, self.two_parse, args={'wait': 0.3})

    def two_parse(self, response):
        sel = Selector(response)
        div = sel.xpath('//div[@class="questionsList"]')
        for a in div.xpath('.//a[@class="listItem"]'):
            img_url_list = a.xpath('.//div[@class="Itembotbot"]/img/@src').extract()
            if img_url_list:
                img_url = ';'.join(img_url_list)
                answer_url = ''.join(['https://www.yzyy365.com', a.xpath('.//@href').extract_first()])
                que_type = a.xpath('.//div[@class="title fl"]/text()').extract_first().replace(' ', '').replace('\n', '').replace('\t', '').encode('utf-8')
                que_info = a.xpath('.//div[@class="Itembotmtop"]/p/text()').extract_first().replace(' ', '').replace('\n', '').replace('\t', '').encode('utf-8')
                yield SplashRequest(answer_url, self.answer_parse, meta={'que_type': que_type, 'img_url': img_url, 'que_info': que_info})

    def answer_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        item = YzyQuestionItem()
        question_id = response.url.split('/')[-1].split('.')[0]
        div = sel.xpath('//div[@class="group fl"]')
        p = '--'.join([x.replace(' ', '').replace('\n', '').replace('\t', '') for x in div.xpath('.//p/text()').extract()])
        item['question_id'] = question_id
        item['answer_id'] = 1
        item['answer_info'] = p
        item['question_info'] = meta['que_info']
        item['image_url'] = meta['img_url']
        item['question_type'] = meta['que_type']
        yield item
