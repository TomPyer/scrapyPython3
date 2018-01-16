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
    last_id = 292933
    last_page = 1

    def parse(self, response):
        while self.last_id > 10000:
            url = 'http://ngjv4.laodao.so/ASHX/bbs_card.ashx?action=jzlist&version=pc&CropID=-1&lastid=%d&pgsize=20&pgindex=%d&pckey=' % (self.last_id, self.last_page)
            self.last_page += 1
            self.last_id -= 20
            yield SplashRequest(url, self.body_parse, args={"wait": 0.3}, meta={'page': self.last_page, 'last_id': self.last_id})

    def body_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        # with open('test.txt', 'wb') as f:
        #     f.write(sel.xpath('//body/pre/text()').extract_first().encode('utf-8'))
        with open('laodao.txt', 'a') as f:
            f.write(''.join([str(meta['page']), '-------------', str(meta['last_id']), '\n']))
        body = json.loads(sel.xpath('//body/pre/text()').extract_first().encode('utf-8'))
        crop_list = ['黄瓜', '番茄', '瓜菜', '根菜', '叶菜', '水稻', '土豆', '棉麻', '花生', '粮油', '葡萄', '苹果',
                     '柑橘', '香蕉', '水果', ' ', '植保', '施肥', '栽培', '意见反馈', ' ', '草莓', '火龙果', '辣椒']
        crop_dic = {}
        for index, value in enumerate(crop_list):
            crop_dic[str(index + 1)] = value
        if body['code'] in ['200', 200]:
            for data in body['datas']:
                if data['CropID']:
                    crop = crop_dic[str(data['CropID'])]
                else:
                    crop = ''
                answer_url = 'http://www.laodao.so/forum/info/%d' % data['lastid']
                img_url = data['photos'].split(',') if data['photos'] else ''
                if img_url:
                    img_lis = [''.join(['http://sngj.laodao.so/', x]) for x in img_url]
                    yield SplashRequest(answer_url, self.answer_parse, meta={'crop': crop, 'id': str(data['ID']),
                                                                             'question_info': data['contents'],
                                                                             'img_url': img_lis})
                else:
                    with open('fail_question.txt', 'a') as f:
                        f.write(str(data['ID']) + '\n')
        else:
            logging.error('this code is not 200 ! url:  ', response.url)

    def answer_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        item = YzyQuestionItem()
        answer = '--'.join([x.replace(' ', '').replace('\n', '').replace('\t', '') for x in sel.xpath('//div[@class="pl-content"]/text()').extract()])
        item['question_id'] = meta['id']
        item['question_info'] = meta['question_info']
        item['answer_id'] = 1
        item['answer_info'] = answer
        item['question_type'] = meta['crop']
        item['websit'] = 'laodao'
        item['image_url'] = meta['img_url']
        yield item

