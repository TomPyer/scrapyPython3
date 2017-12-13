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

