# -*- coding: utf-8 -*-
import scrapy
import logging
import time
import os
import pytesseract
from scrapy import Selector
from scrapy_splash import SplashRequest, SplashFormRequest
from PIL import Image
from wget import download


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    start_urls = ['https://www.zhihu.com/']

    header = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        "Upgrade-Insecure-Requests": "1",
        'Host': 'www.zhihu.com',
        'DNT': '1'
    }

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        yield SplashRequest(captcha_url, callback=self.captcha_parse, headers=self.header)

    def captcha_parse(self, response):
        download(response.url, out='D:\work\scrapyPython3\captcha.jpg')
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请打开%s文件,手动输入验证码' % os.path.abspath('captcha.jpg'))
        captcha = input(u'请输入图片中的验证码...')
        yield SplashRequest(url='https://www.zhihu.com/#signin', callback=self.parse, headers=self.header,
                            meta={'captcha': captcha, 'cookiejar': 1})

    def parse(self, response):
        if os.path.exists('D:\work\scrapyPython3\captcha.jpg'):
            os.remove('D:\work\scrapyPython3\captcha.jpg')
        sel = Selector(response)
        with open('zhihu.html', 'wb') as f:
            f.write(response.body)
        xsrf_value = sel.xpath('//div[@class="view view-signin"]/form/input[@name="_xsrf"]/@value') \
            .extract_first(default='')
        captcha = response.meta['captcha']
        print(xsrf_value)
        print(captcha)
        if xsrf_value:
            yield SplashFormRequest(url='https://www.zhihu.com/login/phone_num',
                                    method='POST',
                                    headers=self.header,
                                    formdata={'phone_num': '15521043979',
                                              'captcha_type': 'en',
                                              'password': '********',
                                              '_xsrf': xsrf_value,
                                              'captcha': captcha,
                                              'rememberme': 'y'},
                                    callback=self.logined,
                                    meta={'cookiejar': response.meta['cookiejar']})
        else:
            print('get xsrf_value error !!!!!!!!!')

    def logined(self, response):
        sel = Selector(response)
        print(response.body)