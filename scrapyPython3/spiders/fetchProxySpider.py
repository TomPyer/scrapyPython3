# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
from scrapy_splash import SplashRequest
from scrapy import Selector


class FetchproxyspiderSpider(scrapy.Spider):
    name = 'fetchProxySpider'
    # allowed_domains = ['www.baidu.com']
    start_urls = ['http://www.baidu.com/']
    proxys = []

    def start_requests(self):
        url_div = {'kxdaili': [], 'mimvp': [], 'xici': [], 'nians': [], 'httpd': [], 'liu': [], 'kuai': []}
        for page in range(1, 10):
            url_div['kxdaili'].append("http://www.kxdaili.com/dailiip/1/%d.html#ip" % page)
            url_div['xici'].append("http://www.xicidaili.com/nn/%d" % page)
            url_div['nians'].append("http://www.nianshao.me/?page=%d" % page)
        for ind in range(1, 34):
            url_div['liu'].append("http://www.66ip.cn/areaindex_%d/1.html" % ind)
        url_div['kuai'].append("http://www.kuaidaili.com/free/inha/1/")
        url_div['mimvp'].append("https://proxy.mimvp.com/free.php?proxy=in_hp&sort=&page=1")
        url_div['httpd'].append("http://www.httpdaili.com/#c-4")

        for k, v in url_div.items():
            for url in v:
                yield SplashRequest(url, self.parse, args={'wait': 0.5}, meta={'fr': k})

    def parse(self, response):
        # 此方法仅提供部分代理网站抓取提示和简单保存流程
        sel = Selector(response)
        meta = response.meta
        try:
            if meta['fr'] == 'dxdaili':
                table_obj = sel.xpath('//table[@class="ui table segment"]')
                # print(len(table_obj.xpath('.//tr')))
                for tr in table_obj.xpath('.//tbody/tr'):
                    td = tr.xpath('.//td/text()').extract()
                    if int(td[4].split(' ')[0]) < 3:
                        ip, port = td[0], td[1]
                        self.proxys.append("%s:%s" % (ip, port))
            elif meta['fr'] == 'mimvp':
                port_dic = {"NmTidmtvapW12cDkwMDAO0O": '9000', "NmTidmtvapW12cDg4ODgO0O": '8888', "NmTidmtvapW12cDgw": '80',
                            "NmTidmtvapW12cDUzMjgx": '53281', "NmTidmtvapW12cDgxMTgO0O": '8118', "NmTidmtvapW12cDgwODgO0O": '8018',
                            "MmDihmtvapW12cDQ0MwO0OO0O": '443', "MmzidmtvapW12cDU0MzE4": '54318', "MmziRmtvapW12cDgy": '82',
                            "MmziRmtvapW12cDgwODIO0O": '8082'}
                div_obj = sel.xpath('//div[@class="free-list"]')
                table_obj = div_obj.xpath('.//table[@class="free-table table table-bordered table-striped"]')
                for tr in table_obj.xpath('.//tbody/tr'):
                    td = tr.xpath('.//td')
                    ip = td[1].xpath('.//text()').extract_first()
                    p_img = td[2].xpath('.//img/@src').extract_first()
                    port = port_dic[p_img.split('=')[-1]] if p_img.split('=')[-1] in port_dic.keys() else '80'
                    self.proxys.append("%s:%s" % (ip, port))
            elif meta['fr'] == 'xici':
                pass
            elif meta['fr'] == 'nians':
                pass
            elif meta['fr'] == 'httpd':
                pass
            elif meta['fr'] == 'liu':
                pass
            elif meta['fr'] == 'kuai':
                pass
        except:
            logging.error(traceback.print_exc())
        finally:
            with open('D:/tangxuelin/stutest/scrapyPython3/scrapyPython3/proxyes.dat', 'wb') as f:
                for pro in self.proxys:
                    f.write(pro)