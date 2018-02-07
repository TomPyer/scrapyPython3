# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import logging
import copy
import pymysql
import logging
from twisted.enterprise import adbapi



class Scrapypython3Pipeline(object):
    def process_item(self, item, spider):
        return item


class firstSpiderImagePipeline(ImagesPipeline):
    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': 'https://www.douban.com/photos/photo/2370443040/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    def get_media_requests(self, item, info):
        # ImagePipeline根据image_urls中指定的url进行爬取，可以通过get_media_requests为每个url生成一个Request
        for image_url in item['image_urls']:
            self.default_headers['referer'] = image_url
            yield Request(image_url, headers=self.default_headers)

    def item_completed(self, results, item, info):
        # 图片下载完毕后，处理结果会以二元组的方式返回给item_completed()函数
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item


class MySQLChyxxPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        copyItem = copy.deepcopy(item)
        d = self.dbpool.runInteraction(self._do_currency_func, copyItem, spider)
        d.addErrback(self._handle_error, item, spider)
        return d

    def _do_currency_func(self, conn, item, spider):
        import traceback
        if spider.name == 'zhihuSpider':
            if 'to_user' in item.keys():
                # 评论流程
                sql = '''insert into zhihu_comment(question_id, answer_id, content, author, zan_num, to_user, is_question)
                         values(%s, %s, %s, %s, %s, %s, %s, %s)
                '''
                args = [item['question_id'], item['answer_id'], item['content'], item['author'], item['zan_num'],
                        item['to_user'], item['is_question']]
                conn.execute(sql, args)
            elif 'answer_id' in item.keys():
                # 回答流程
                sql = '''insert into zhihu_answer(question_id, answer_id, answer_cre_date, answer_content, answer_author,
                              answer_comment_num, answer_zan_num)
                         values(%s, %s, %s, %s, %s, %s, %s)
                '''
                args = [item['question_id'], item['answer_id'], item['answer_cre_date'], item['answer_content'],
                        item['answer_author'], item['answer_comment_num'], item['answer_zan_num']]
                conn.execute(sql, args)
            else:
                # 问题流程
                sql = '''insert into zhihu_question(question_id, question_author, question_title, question_description,
                        question_image, question_comment, question_comment, question_comment_num, question_care_num,
                        question_view_num, answer_count, from_theme, from_theme_url)
                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                args = [item['question_id'], item['question_author'], item['question_title'], item['question_description'],
                        item['question_image'], item['question_comment'], item['question_comment'],
                        item['question_comment_num'], item['question_care_num'], item['question_view_num'],
                        item['answer_count'], item['from_theme'], item['from_theme_url']]
                conn.execute(sql, args)
        elif spider.name in ['yzySpider', 'laodaoSpider']:
            all_id_sql = '''select id from bch_question'''
            conn.execute(all_id_sql)
            all_id_list = conn.fetchall()
            if item['question_id'] not in all_id_list:
                sql = '''insert into bch_question(question_id, answer_id, question_info, answer_info, image_url, question_type, websit)
                         values(%s, %s, %s, %s, %s, %s, %s)
                '''
                args = (item['question_id'], item['answer_id'], item['question_info'], item['answer_info'], item['image_url'], item['question_type'], item['websit'])
                conn.execute(sql, args)
            else:
                logging.warning('this id is exist ! %s' % item['question_id'])
        elif spider.name == 'gdstats':
            if 'value_' in item.keys():
                # 常规表流程
                try:
                    sql = '''insert into gd_zyjjzb(year_, area, section_, target, value_, grow_b)
                             values(%s, %s, %s, %s, %s, %s)'''
                    conn.execute(sql, (item['year_'], item['area'], item['section_'], item['target'], item['value_'],
                                       item['grow_b']))
                except Exception as e:
                    logging.error(traceback.print_exc())
            else:
                # 特殊表流程
                pass

    def _handle_error(self, failue, item, spider):
        logging.error(failue)
