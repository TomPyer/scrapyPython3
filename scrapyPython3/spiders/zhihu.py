# -*- coding: utf-8 -*-
import scrapy
import logging
import time
import os
from scrapy import Selector
from scrapy_splash import SplashRequest, SplashFormRequest
from PIL import Image
from wget import download


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    start_urls = ['https://www.zhihu.com/']

    # headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #             'Accept-Encoding': 'gzip, deflate, sdch, br',
    #             'Accept-Language': 'zh-CN,zh;q=0.8',
    #             'Cache-Control': 'max-age=0',
    #             'Connection': 'keep-alive',
    #             'Host': 'www.zhihu.com',
    #             'Referer': 'https://www.zhihu.com/',
    #             'Upgrade-Insecure-Requests': '1',
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
    #                           '(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        logging.error(captcha_url)
        yield SplashRequest(captcha_url, callback=self.captcha_parse, meta={'cookiejar': 1})

    def captcha_parse(self, response):
        download(response.url)
        try:
            im = Image.open('captcha.gif')
            im.show()
            im.close()
        except:
            print(u'请打开%s文件,手动输入验证码' % os.path.abspath('captcha.gif'))
        captcha = input(u'请输入图片中的验证码...')
        yield SplashRequest(url='https://www.zhihu.com/#signin', callback=self.parse, meta={'captcha': captcha})

    def parse(self, response):
        sel = Selector(response)
        xsrf_value = sel.xpath('//div[@class="view view-signin"]/form/input[@name="_xsrf"]/@value') \
            .extract_first(default='')
        # self.headers['X-Xsrftoken'] = xsrf_value
        if xsrf_value:
            data = {}
            data['phone'] = '15521043979'
            data['pasd'] = 'wobuzhidao123'
            data['captcha'] = 'en'
            login_url = 'https://www.zhihu.com/login/phone_num'
            logging.info(xsrf_value)
            yield SplashFormRequest(login_url, meta=data, dont_filter=True, callback=self.logined,
                                    formdata={'phone_num': data['phone'], 'captcha_type': 'en',
                                              'password': data['pasd'], '_xsrf': xsrf_value})
        else:
            logging.error('xsrf_value get error!')

    def logined(self, response):
        sel = Selector(response)
        print(response.body)