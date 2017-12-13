# scrapyPython3
### 这是对于上一个项目的更细化教程(或者说是笔记..) 
#### 一、基本工作
第一次提交的内容是由
```python
scrapy startproject projcetName
```
完成的,可以在任意目录下执行该命令,前提是你安装好了python及scrapy包.
```python
pip install scrapy      # pip安装scrapy库
```
使用startproject创建scrapy项目标准目录结构,由spiders文件夹,items,middlewares,pipelines,settings组成.
spiders:
存放当前项目下的所有爬虫文件
items:
存放爬虫工程中所用到的Item类定义
middlewares:
中间件,可以再settings中启用自定义的中间件,可以定义部分在spiders工作中涉及到的操作
pipelines:
用来处理spider中返回的item信息,完成数据库存储,文件图片下载等操作
settings:
项目配置文件

基础介绍完了,现在,创建自己的第一个爬虫 :)
```python
scrapy genspider firstSpider www.baidu.com 
```
参数分别为爬虫名称,允许和起始链接
不出意外的话,在spiders文件夹内会新增一个名为firstSpider的py文件,内容由标准的scrapy模板生成,可以自行查找模板修改方法.

firstSpider.py介绍
name: 爬虫名称,在启动爬虫时需要用上
allowed_domains: 允许追踪的域名,当爬虫运行中yield某个不属于该域名下的url会被抛弃
start_urls: 一个列表,用来定义启动爬虫时开始的url

parse: 对于response的处理方法

先不管这些,先把scrapyd搭起来!
安装依赖包
```python
pip install scrapyd
pip install scrapyd-client
```
启动scrapyd服务
```python
scrapyd    # 在项目的根目录执行,会运行scrapyd服务,监听6800端口
```
文档[Scrapyd](http://scrapyd.readthedocs.io/en/stable/)
将scrapyPython3项目发布到scrapyd中
```python
scrapyd-deploy target -p project 
```
事先取消scrapy.cfg文件中[deploy]下url的注释,并修改为[deploy:xxx]
执行成功会打印信息:
```python
Deploying to project "scrapyPython3" in http://localhost:6800/addversion.json
Server response (200):
{"node_name": "tree", "status": "ok", "project": "scrapyPython3", "version": "1513146589", "spiders": 1}

```
显示大概是这样就算是完成发布成功了.

#### 二、第一个爬虫
先拿一些基础的网页来展示功能效果
比如[凤凰娱乐新闻](http://ent.ifeng.com/)
也省的再创建一个爬虫了,直接对firstSpider进行修改使用

注释掉allowed_domains字段,部分情况下才需要使用
修改start_urls字段,改为待爬取的链接

定义parse()函数处理response进行信息抓取
```python
    def parse(self, response):
        sel = Selector(response)        # 将response传给Selector生成Selector实例
        next_url = sel.xpath('//ul[@class="clearfix"]/li[3]/a/@href').extract()     # 娱乐版块下的电影版块链接
        yield Request(next_url, self.next_parse)
```
Selector是scrapy的选择器对象,根据条件选取我们所需要文本信息等
Request接受url, callback, meta等参数,将Request实例对象放入scrapy抓取队列中

后续两个方法功能类似,为了展示如何更深层次的抓取需要的信息.

一般来讲,是使用curl命令访问127.0.0.1:6800/xxx 并制定参数来操作scrapyd服务
部分,部分情况下,windows下使用curl命令似乎不尽如人意,而且每次需要输入那么一长串的命令信息

所以,duang! duang! duang! 
自己写的curlApi文件就应运而生！
启动爬虫
```python
python curmain.py -s scrapyPython3 firstSpider     # -s 为启动命令, 参数为项目名称和爬虫名称
```
关闭爬虫
```python
python curmain.py -c scrapyPython3 SpiderID     # -c 关闭爬虫命令, 参数为项目名称和爬虫ID
```
其他相关操作可以使用 -h 进行查看文本输出.

执行启动命令后,会在项目的根目录下产生logs文件夹,根据项目,爬虫,job_id区分各个爬虫的日志文件
并在curlApi目录下产生job_id.txt文件,方便查找job_id终止爬虫或查找对应日志文件.

根据logs下产生的日志文件对spider进行调试修改

推荐是在127.0.0.1:6800中查看当前项目状态(运行爬虫数,运行时间,日志文件)

第二次运行
```python
title = div.xpath('.//h2/text()').extract()[0]
IndexError: list index out of range
```
很常见的一个问题,部分情况下xpath并不一定能取值成功(即标签不存在或内容不存在的情况下)
如果取值失败  .extract() 方法返回的是一个空列表,使用[0]取值则会触发IndexError错误.