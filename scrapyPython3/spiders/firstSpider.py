# -*- coding: utf-8 -*-
import scrapy


class FirstspiderSpider(scrapy.Spider):
    name = 'firstSpider'
    allowed_domains = ['www.baidu.com']
    start_urls = ['http://www.baidu.com/']

    def parse(self, response):
        pass
