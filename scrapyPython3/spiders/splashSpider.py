# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest


class SplashspiderSpider(scrapy.Spider):
    name = 'splashSpider'
    # allowed_domains = ['www.baidu.com']
    start_urls = ['http://www.baidu.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        pass
