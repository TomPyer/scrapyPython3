# -*- coding: utf-8 -*-
import scrapy
import logging
import time
import os
import pytesseract
from scrapy import Selector, FormRequest
from scrapy_splash import SplashRequest
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
    cookie = {'_zap': '9a4d80e1-5623-4f25-9328-ad51422817a3',
              'd_c0': "AIACtUo4BAyPTsOB9195Nz_NiJjQPW6-IK8=|1499221622",
              'q_c1': 'e3165f4370f545c7981f463497855d2d|1513301109000|1499221616000',
              '__guid': '74140564.2335865430820433400.1513559013725.4736',
              'aliyungf_tc': 'AQAAACiNvGo9kQkAFIEgeQCzSdNxIIHW',
              '_xsrf': 'e272bf01-5497-4c37-a94f-c7517304bf9a',
              'l_cap_id': "MTk3ODY5MzEyMDk4NGUyNWE1MTA3MmIzNjcwY2IxNDA=|1513757662|d074b37dafc14e5e2729b13b90189d8c0ca39920",
              'r_cap_id': "OWU0NjAxMGYxODYwNGY5YWE5ZDg0ODRmZjdlMjZkOGM=|1513757662|28ca9ddc990808ce4674f469bda23718a1b89233",
              'cap_id': "Njk0MTUyNDdjN2M5NDI2MTgxZDIzZGQzYmRhNjU5Mzc=|1513757662|a45c3921a73a9c44c79d53b5726fbba138a315b5",
              'monitor_count': '12',
              '__utma': '51854390.120040990.1513577380.1513590187.1513755489.4',
              '__utmb': '51854390.0.10.1513755489',
              '__utmc': '51854390',
              '__utmz': '51854390.1513755489.4.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
              '__utmv': '51854390.000--|2=registration_date=20160929=1^3=entry_date=20171220=1'}

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        yield SplashRequest(captcha_url, callback=self.captcha_parse, headers=self.header, cookies=self.cookie)

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
                            cookies=self.cookie,
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
            yield FormRequest(url='https://www.zhihu.com/login/phone_num',
                                    method='POST',
                                    headers=self.header,
                                    formdata={'phone_num': '15521043979',
                                              'password': 'lalala123',
                                              '_xsrf': xsrf_value,
                                              'captcha_type': 'cn'},
                                    callback=self.logined,
                                    cookies=self.cookie,
                                    meta={'cookiejar': response.meta['cookiejar']})
        else:
            print('get xsrf_value error !!!!!!!!!')

    def logined(self, response):
        sel = Selector(response)
        print(response.body)