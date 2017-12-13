# coding: utf-8

import sys, getopt
import urllib.request
import urllib.parse

from datetime import datetime


class CommondParse(object):
    @staticmethod
    def startup():
        url = ''.join([website, 'schedule.json'])
        parse = {'project': v, 'spider': args[0]}
        re_data = open_post_url(url, parse)
        if re_data['status'] == 'ok':
            with open(r'D:\\work\\studyscrapy\\curApi\\job_id.txt', 'a') as f:
                f.write(args[0] + ':' + re_data['jobid'] + ' ' + str(datetime.now())+ '\n')
        print_info(re_data)

    @staticmethod
    def close():
        url = ''.join([website, 'cancel.json'])
        parse = {'project': v, 'job': args[0]}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def daemonstatus():
        """
        Add a version to a project, creating the project if it doesn’t exist.
        """
        url = ''.join([website, 'daemonstatus.json'])
        re_data = open_get_url(url)
        print_info(re_data)

    @staticmethod
    def listprojects():
        url = ''.join([website, 'listprojects.json'])
        re_data = open_get_url(url)
        print_info(re_data)

    @staticmethod
    def listversions():
        url = ''.join([website, 'listversions.json'])
        parse = {'project': v}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def listspiders():
        url = ''.join([website, 'listspiders.json'])
        parse = {'project': v}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def listjobs():
        url = ''.join([website, 'listjobs.json'])
        parse = {'project': v}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def addversion():
        url = ''.join([website, 'addversion.json'])
        parse = {'project': v, 'version': args[0], 'egg': args[1]}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def delversion():
        url = ''.join([website, 'delversion.json'])
        parse = {'project': v, 'version': args[0]}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def delproject():
        url = ''.join([website, 'delproject.json'])
        parse = {'project': v, 'version': args[0]}
        re_data = open_post_url(url, parse)
        print_info(re_data)

    @staticmethod
    def print_helper_message():
        print("----------------------Help message-----------------------")
        print("-s : start spider, need parse(project_name, spider_name)")
        print("-c : close spider, need parse(project_name, spider_job_id)")
        print("-d : daemonstatus, need parse(one)")
        print("-a : addversion,   need parse(project_name, version, egg)")
        print("-l : listprojects, need parse(one)")
        print("-v : listversions, need parse(project_name)")
        print("-p : listspiders,  need parse(project_name)")
        print("-j : listjobs,     need parse(project_name)")
        print("-dv: delversion,   need parse(project_name, version)")
        print("-dp: delproject,   need parse(project_name)")


def open_post_url(url, data):
    try:
        en_data = urllib.parse.urlencode(data).encode('UTF8')
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, en_data)
        return eval(response.read())
    except NameError as e:
        return {'msg': 'This jobid spider not run.'}


def open_get_url(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    return eval(response.read())


def print_info(data):
    print("----------------------Return info------------------------")
    for k, va in data.items():
        print(k, va)


if __name__ == '__main__':
    opts = []
    args = None
    website = 'http://127.0.0.1:6800/'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:help:s:c:d:a:l:v:p:j:dv:dp")
    except getopt.GetoptError as err:
        print(str(err))
    if len(opts) == 0:
        CommondParse.print_helper_message()
    for op, v in opts:
        if op == '-h' or '--help':
            CommondParse.print_helper_message()
        if op == '-s':
            CommondParse.startup()
        elif op == '-c':
            CommondParse.close()
        elif op == '-d':
            CommondParse.daemonstatus()
        elif op == '-a':
            CommondParse.addversion()
        elif op == '-l':
            CommondParse.listprojects()
        elif op == '-v':
            CommondParse.listversions()
        elif op == '-p':
            CommondParse.listspiders()
        elif op == '-j':
            CommondParse.listjobs()
        elif op == '-dv':
            CommondParse.delversion()
        elif op == '-dp':
            CommondParse.delproject()
