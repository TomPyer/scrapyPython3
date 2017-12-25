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

from scrapyPython3.items import ZhihuAnswerItem, ZhihuCommentItem, ZhihuQuestionItem


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
        if xsrf_value:
            yield FormRequest(url='https://www.zhihu.com/login/phone_num',
                                    method='POST',
                                    headers=self.header,
                                    formdata={'phone_num': '15521043979',
                                              'password': 'lalala1',
                                              '_xsrf': xsrf_value,
                                              'captcha_type': 'en',
                                              'captcha': captcha},
                                    callback=self.logined,
                                    cookies=self.cookie,
                                    meta={'cookiejar': response.meta['cookiejar']})
        else:
            print('get xsrf_value error !!!!!!!!!')

    def logined(self, response):
        print(response.body)
        meta = response.meta
        yield SplashRequest('https://www.zhihu.com/', callback=self.first_page, cookies=self.cookie, meta=meta)

    def first_page(self, response):
        sel = Selector(response)
        meta = response.meta
        card_div = sel.xpath('//div[@class="Card TopstoryItem"]')
        for card in card_div:
            # 遍历首页的基础页面,获取问题链接
            question_div = card.xpath('.//div[@class="Feed"]')
            question_url = ''.join([self.start_urls[0], question_div.xpath('.//div[@class="ContentItem AnswerItem"]/h2/div/a/@href').extract_frist()])
            meta['question_id'] = question_url.split('/')[-1]
            meta['from_theme'] = sel.xpath('//a[@class="TopicLink"]/div/div/text()').extract()
            meta['from_theme_url'] = sel.xpath('//a[@class="TopicLink"]/@href').extract()
            yield SplashRequest(question_url, callback=self.question_parse, cookies=self.cookie, meta=meta)

    def question_parse(self, response):
        # 处理和提取所需要的问题内容, xpath格式都是从页面上获取的
        sel = Selector(response)
        meta = response.meta
        question_item = ZhihuQuestionItem()
        self.answer_info(sel, meta['question_id'])  # 优先提取答案内容
        header_div = sel.xpath('//div[@class="QuestionHeader-main"]')
        question_item['question_title'] = header_div.xpath('.//h1/text()').extract_first()
        question_item['question_id'] = meta['question_id']
        question_item['question_description'] = header_div.xpath('.//span[@class="RichText"]/text()').extract_first()
        question_item['question_image'] = header_div.xpath('.//span[@class="RichText"]/figure/img/@src').extract()
        question_item['question_comment'] = sel.xpath('//div[@class="QuestionHeader-Comment"]/span/text()').extract_first()
        follow_div = sel.xpath('//div[@class="QuestionFollowStatus"]')
        question_item['question_care_num'] = follow_div.xpath('.//button/div[@class="NumberBoard-value"]/text()').extract_first()
        question_item['question_view_num'] = follow_div.xpath('.//div[@class="NumberBoard-item"]/div[@class="NumberBoard-value"]/text()').extract_first()
        question_item['answer_count'] = sel.xpath('//div[@class="List-header"]/h4/span/text()').extract_first().split('"')[1]
        question_item['from_theme'] = meta['from_theme']
        question_item['from_theme_url'] = meta['from_theme_url']
        yield question_item

    def answer_info(self, sel, question_id):
        for answer in sel.xpath('//div[@class="ContentItem AnswerItem"]'):
            # 遍历答案card, 评论内容也隐藏在其中
            answer_item = ZhihuAnswerItem()
            answer_item['question_id'] = question_id
            answer_item['answer_id'] = answer.xpath(".//@name").extract_first()
            answer_item['answer_cre_date'] = answer.xpath('.//meta[@itemprop="dateCreated"]/@content').extract_first()
            answer_item['answer_content'] = '\r'.join(answer.xpath('.//span[@class="RichText CopyrightRichText-richText"]/text()').extract())
            answer_item['answer_author'] = answer.xpath('.//meta[@itemprop="name"]/@content').extract_first()
            answer_item['answer_comment_num'] = answer.xpath('.//meta[@itemprop="commentCount"]/@content').extract_first()
            answer_item['answer_zan_num'] = answer.xpath('.//meta[@itemprop="upvoteCount"]/@content').extract_first()
            yield answer_item
            for comment in answer.xpath('//div[@class="CommentItem"]'):
                # 提取需要的评论信息
                comment_item = ZhihuCommentItem()
                comment_item['question_id'] = question_id
                comment_item['answer_id'] = answer.xpath('.//@name').extract_first()
                comment_item['is_question'] = 1
                content = comment.xpath('.//div[@class="RichText CommentItem-content"]/text()').extract_first()
                comment_item['content'] = content if content else comment.xpath('.//div[@class="RichText CommentItem-content"]/p/text()').extract_first()
                comment_item['author'] = comment.xpath('.//a[@class="UserLink-link"]/text()').extract_first()
                comment_item['zan_num'] = comment.xpath('.//div[@class="CommentItem-footer"]/button/text()').extract_first()
                if comment.xpath('.//span[@class="CommentItem-reply"]'):
                    comment_item['to_user'] = comment.xpath('.//a[@class="UserLink-link"]/text()').extract()[1]
                else:
                    comment_item['to_user'] = ''
                yield comment_item