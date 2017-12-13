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