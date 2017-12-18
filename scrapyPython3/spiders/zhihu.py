# -*- coding: utf-8 -*-
import scrapy
import logging

from scrapy import Selector
from scrapy_splash import SplashRequest, SplashFormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    start_urls = ['https://www.zhihu.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={'wait': 0.5})

    def parse(self, response):
        sel = Selector(response)
        xsrf_value = sel.xpath('//div[@class="view view-signin"]/form/input[@name="_xsrf"]/@value') \
            .extract_first(default='')
        if xsrf_value:
            data = {}
            data['phone'] = '15521043979'
            data['pasd'] = '********'
            data['captcha'] = 'en'
            login_url = 'https://www.zhihu.com/login/phone_num'
            logging.info(xsrf_value)
            yield SplashFormRequest(login_url, meta=data, dont_filter=True, callback=self.two_parse,
                                    formdata={'phone_num': data['phone'], 'captcha_type': data['captcha'],
                                              'password': data['pasd'], '_xsrf': xsrf_value})
        else:
            logging.error('xsrf_value get error!')

    def two_parse(self, response):
        print(response.body)