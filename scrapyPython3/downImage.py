#! coding:utf-8
import os
import pymysql
import queue
import traceback

from threading import Thread
from urllib import request


def file_path_cre(path, nam):
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, nam)


def download_img(ur, ty, nam):
    resp = request.urlopen(ur)
    img = resp.read()
    file_path = file_path_cre(os.path.join(r'D:\\image', ty), nam)
    with open(file_path, 'wb') as outfile:
        outfile.write(img)


def get_img_data():
    conn = None
    try:
        conn = pymysql.connect(host='192.168.30.161', port=3306, user='root', password='', db='gds_argidata20170324', charset='utf8')
        cursor = conn.cursor()
        sql = '''
            select question.question_id, question.question_info, question.image_url, question.crop_name, answer.answer_info
            from question
            left join answer
            on answer.question_id=question.question_id
            where question.question_id not like '%A%' and question.question_id not like '%C%' and is_true_data!=2
            limit 0, 1000
        '''
        cursor.execute(sql)
        laodao_data = cursor.fetchall()
        sql = '''
            select question.question_id, question.question_info, question.image_url, question.crop_name, answer.answer_info
            from question
            left join answer
            on answer.question_id=question.question_id
            where question.question_id like '%A%' or question.question_id like '%C%' and is_true_data!=2
            limit 0, 1000
        '''
        cursor.execute(sql)
        yzy_data = cursor.fetchall()
        return laodao_data, yzy_data
    except Exception as e:
        _ = e
        traceback.print_exc()
    finally:
        if conn:
            conn.close()


class downImageFunc(Thread):
    def __init__(self, name, tup, count):
        Thread.__init__(self)
        self.name = name
        self.tup = tup
        self.count = count

    def run(self):
        for da in self.tup:
            try:
                print('%s -- 已下载 %d 张图片....' % (self.name, self.count))
                self.count += 1
                info = ''.join([da[1], da[4]])
                info = info[0:195] if len(info) > 200 else info  # 精简回答内容并拼接字符串
                file_name = info.replace('\n', '').replace('\r', '').replace('\t', '').replace('---', '-').replace('你好', '') \
                    .replace(' ', '').replace('\xa0', '').replace('%', '').replace('·', '').replace('/', '').replace('°', '')\
                    .replace('？', '').replace('?', '.').replace('：', '').replace('；', '.').replace(':', '-')
                typ = da[3] if da[3] else '未分类'  # 查看是否有分类
                img_url = da[2]
                img_url_list = img_url.split(',')
                for index, url in enumerate(img_url_list):
                    name = file_name + '-' + str(index) + '.jpg'
                    download_img(url, typ, name)
                queue_tmp.put(da[0])
            except Exception as e:
                _ = e
                traceback.print_exc()
                continue
        return self.count


class mdyImageData(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        conn = None
        while 1:
            try:
                conn = pymysql.connect(host='***', port=3306, user='root', password='***',
                                       db='***', charset='utf8')
                cursor = conn.cursor()
                id = queue_tmp.get()
                sql = '''update question set is_true_data=2 where question_id='%s' ''' % str(id)
                cursor.execute(sql)
                conn.commit()
                print('修改数据表成功>>>>>>>>>>>>>>..')
            except Exception as e:
                _ = e
                traceback.print_exc()
            finally:
                if conn:
                    conn.close()


if __name__ == '__main__':
    l_data, y_data = get_img_data()
    num = 1
    queue_tmp = queue.Queue(10)
    print('start ---------------- \n')
    down_obj = downImageFunc('downloadImage', l_data, num)
    down_obj2 = downImageFunc('download2', y_data, num)
    mdy_obj = mdyImageData('mdyMysql')
    down_obj2.start()
    down_obj.start()
    mdy_obj.start()
    mdy_obj.join()
    print('end---------------------\n')