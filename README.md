# scrapyPython3
## 这是对于上一个项目的更细化教程(或者说是笔记..) 
### 一、基本工作
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

### 二、第一个爬虫
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

嗯...好像还是有问题,好吧,现在这样来,跟我做
```python
scrapy shell http://ent.ifeng.com/listpage/6/1/list.shtml
```
以命令行形式加载指定url内容,当然,是由scrapy解析后的
进入命令行后,基本上跟一个ipython窗口一样,但是他加载了scrapy相关模块可供使用,然后就可以在里面为所欲为了
可以先随手输入一个
```python
print(response.body)        
```
看看是否有值没有,看到一堆东西唰唰唰基本上就稳了,没有的话看看是否访问失败,错误代码是啥,那是另外分析的事情了
然后就基本上可以把firstSpider里的代码一句一句复制进去看看输出情况了.

经过一番检查,错误在.xpath筛选时,只选择/h2/text()无法读取到/h2/a/text()内容
以及content读取时,应该使用//开头,才能确保从根目录开始查找.

到现在这个commit,是可以成功运行并将电影分类下的新闻标题和内容获取下来.

### 三、扩大需求(图片下载)
嗯..光是拿个标题和文章内容似乎也不够有表现力...试试把剧照给弄下来
兵马未动粮草先行
先把settings.py配置好,需要做的有:
1、开启'scrapy.pipelines.images.ImagesPipeline':5,<br>
2、配置images相关属性<br>
这两个是最基础的，后面有需要再额外添加

然后把item定义好
items.py
```python
class FirstSpiderItem(scrapy.Item):
    images = scrapy.Field()
    images_urls = scrapy.Field()
    images_paths = scrapy.Field()
    pass
```
再把爬虫文件中添加一句获取图片Url的xpath表达式以及赋值给item并yield
```python
image_url = sel.xpath('//div[@id="main_content"]/p[@class="detailPic"]/img/@src').extract()
item = FirstSpiderItem()
    if image_url:
        item['image_urls'] = image_url
        yield item
```
一个最基础的图片下载功能就完成了.
漏了一段
```python
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
```
在pipelines.py文件中添加该自定义图片下载pipeline

### 四、爬取动态页面(scrapy_splash)

现在很多网站都采用js动态加载的模式来加载页面数据,具体原因可能是比较流行吧<br>

面对js动态加载的数据,spider在初次访问时并无法获取到所需要的内容,这时候就需要一个中间模块来代为执行js函数加载所需要的内容<br>

这里我用到的是scrapy_splash,原因嘛,简单,易用(基础功能使用并不复杂)<br>

Splash是一个Javascript渲染服务。它是一个实现了HTTP API的轻量级浏览器,<br>

Splash是用Python实现的,同时使用Twisted和QT.Twisted（QT）用来让服务具有异步处理能力,以发挥webkit的并发能力.<br>

首先,我们需要拥有docker(<br>
    Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的容器中,然后发布到任何流行的 Linux 机器上,也可以实现虚拟化的.容器是完全使用沙箱机制,相互之间不会有任何接口.)<br>
    
这里是我自己的docker安装过程以及一些遇到的小问题[docker-简书](http://www.jianshu.com/p/75d26f00ddb1)<br>

不出意外应该是很容易就安装好了的,最多受网速限制慢一些.<br>

然后需要就是需要安装scrapy_splash了<br>
```python
pip install scrapy_splash
```

docker准备好了之后呢,需要把scrapy_splash服务给运行起来<br>

```python
docker pull scrapinghub/splash          # 将scrapy_splash镜像pull到docker环境

docker run -p 8050:8050 scrapinghub/splash     # 将scrapy_splash服务运行在8050端口
```

到这里,一个运行了scrapy_splash服务的docker环境已经搭建完成<br>

然后在项目目录下的settings.py中添加<br>

```python

SPLASH_URL = 'http://192.168.99.100:8050'       # 这是我的dcoker的地址和scrapy_splash服务端口

DOWNLOADER_MIDDLEWARES = {
'scrapy_splash.SplashCookiesMiddleware': 723,           # 添加SplashMiddleware下载中间件
'scrapy_splash.SplashMiddleware': 725,
'scrapy.downloadermid
SPIDER_MIDDLEWARES = {dlewares.httpcompression.HttpCompressionMiddleware': 810,
}

'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,       # 启用SplashDeduplicateArgsMiddleware爬虫中间件
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'        # 设置scrapy_splash去重类

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'   # 启用scrapy_splash缓存

```

上面这些配置根据个人需要做修改或注释掉部分不需要的配置.<br>

到这里,准备和配置工作基本做完了,接下来只需要在写爬虫的时候稍微做些改动就可以了.<br>

比如:修改start_request()函数,使用SplashRequest来代替默认的Request<br>
```python

    from scrapy_splash import SplashRequest

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse)
```
这样就能让url都以SplashRequest对象的方式传递下去,交给splash服务进行js渲染工作.<br>

诶嘿嘿嘿嘿,现在可以直接在Selecotr对象的xpath或css方法中去获取页面上js加载出来的数据了 :),网站就跟在你面前裸奔一样<br>

tips: js渲染也仅仅是加载默认那部分,如果是需要滚动页面进行额外获取的话,需要仔细去查看滚动鼠标时网页在偷偷的执行了什么哦!

## 五、实战演练
今天的预告：完成一个动态爬虫,从页面到入库的整个过程.

有请今天的受害者[知乎](www.zhihu.com)<br>
首先使用了
```python
scrapy shell www.zhihu.com
```
简单测试,发现事情果然没有这么简单<br>
接着
```python
scrapy genspider zhihu www.zhihu.com    # 创建zhihu爬虫
```
然后研究一下知乎的登录页面的具体流程<br>

首先,我们肯定是使用帐号密码登录,'www.zhihu.com'访问默认是app扫码登录,需要加上'#signin',才能切换为帐号密码登录<br>

然后,使用错误的帐号密码查看post请求去向(正确的你就登录成功然后跳转链接了,浏览器F12跳转链接后会刷新Network信息)<br>

就能发现post请求url为('https://www.zhihu.com/login/phone_num')<br>

其中有参数['_xsrf', 'phone_num', 'password', 'captcha_type']<br>
```
'_xsrf':  请求页面中携带的一个验证码<br>
'phone_num', 'password' : 看字面意思就可以<br>
'captcha_type':  验证码类型,默认是cn<br>
```
好的,大概准备好了,可以尝试一波<br>

很好,第一次尝试失败了,看看是为什么<br>

返回内容是验证码错误, 可是在登录页面并没有发现填写验证码的地方啊,而且'_rsxf'参数值也成功获取到了并提交<br>

问题处在哪里呢?  动动脑子就能知道,知乎对于真实用户使用浏览器访问主页时,并不设置验证码输入框(至少一开始不会)<br>

当用户访问频率或部分操作已经达到了非常人水平,再次登录,就能看见知乎的验证码小框框了   :)  <br>

好的,经过不懈努力,让知乎已经把我判断为非人类操作了,找出了他请求验证码的url<br>
(https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en)<br>

其中, t代表当前时间参数,  time.time() * 1000 , 然后套上去就可以了<br>

流程就变成了:<br>

    1, 访问'www.zhihu.com/#signin', 并请求 'www.zhihu.com/captcha.gif', 带上指定参数获取到验证码<br>

    2, 将'captcha'码 和 '_xsrf'码 加上 帐号密码, 'captcha_type', 这几个参数, 访问'www.zhihu.com/login/phone_num'<br>

    3, 嗯...到这里,如果成功的话,应该会重定向到www.zhihu.com首页,并根据用户属性展示相关推荐文章<br>

好,琢磨完了！, 写代码吧！<br>

由于使用的scrapyd运行爬虫,input语句在代码中似乎不起作用,正在想别的办法..

嗯...才现密码写在里面了....刚做修改...

终于登录成功了, 提供一个解决问题的大概思路:<br>

    首先, 回顾一下模拟登录的流程<br>

    1、我们先访问了('https://www.zhihu.com/captcha.gif?r=******&type=login&lang=en')获取验证码<br>

    2、然后携带验证码去访问('https://www.zhihu.com/#signin')登录页面<br>

    3、验证码和登录页面的'_xsrf'码这两个关键信息已经拿到了,再去进行post请求('https://www.zhihu.com/login/phone_num')<br>

    4、等待服务器返回成功与否, 看返回值中的 "r" 即可, 0为成功, 1为失败<br>

之前一直登陆不上是为什么呢, 因为我们在2步骤, 访问 ('https://www.zhihu.com/#signin') 时并没有存储下服务器返回的cookies信息<br>

这个非常关键, 服务器返回cookies信息代表着服务器对访问端的一个身份验证, 如果没有这一层cookie, post登录请求的时候不管验证码对不对, 服务器都当作一个非法请求, 直接返回验证码错误...<br>

在这里栽了那么一小会儿...<br>

有想到cookies信息, settings.py开启了cookie验证, 并且在访问时也有携带meta={'cookiejar': 1} <br>

但是还是一直无法成功登录, 可能我的header伪装不够... 一直被当成非法请求??<br>

那么干脆一不做二不休, 我使用浏览器手动访问 ('https://www.zhihu.com/#signin') <br>

然后F12查看Request Headers 中的Cookie, 然后复制下来, 整理好格式后写死在代码里！<br>

然后就成功了....<br>

严格来讲这应该还是一个不成功的模拟登陆, 毕竟如果手动把cookie写在代码里的话, 跟登录以后手动把cookie保存有什么区别...<br>

有待后续修改...<br>

不过在做大面积信息爬取的时候, 还是可以考虑手动保存多个帐号到cookie池, 轮换使用, 避免被BAN...<br>

tips:.....好忙啊......   :(<br>

好了,来正式开干....<br>

首先更新一个Items.py 文件

    class ZhihuQuestionItem(scrapy.Item):
        question_id = scrapy.Field()
        question_launch_date = scrapy.Field()
        question_author = scrapy.Field()
        question_title = scrapy.Field()
        question_description = scrapy.Field()
        question_image = scrapy.Field()
        question_comment_num = scrapy.Field()
        question_care_num = scrapy.Field()
        question_view_num = scrapy.Field()
        answer_count = scrapy.Field()
        pass
        
    class ZhihuAnswerItem(scrapy.Item):
        answer_id = scrapy.Field()
        answer_cre_date = scrapy.Field()
        answer_content = scrapy.Field()
        answer_author = scrapy.Field()
        answer_comment_num = scrapy.Field()
        answer_zan_num = scrapy.Field()
        pass


    class ZhihuCommentItem(scrapy.Item):
        question_id = scrapy.Field()
        answer_id = scrapy.Field()
        is_question = scrapy.Field()
        content = scrapy.Field()
        author = scrapy.Field()
        zan_num = scrapy.Field()
        to_user = scrapy.Field()
        pass


这是第一版本, 初步观察知乎问答详情所挑出来的有用的信息, 暂时不考虑过滤辣鸡内容, 毕竟从Question出发, 注意选择分类就可以<br>

简单讲一下,

    QuestionItem用来存储id,时间,标题,问题描述,作者,关注数,浏览数,回答数,评论数,以及可能存在的图片..
    AnsWerItem用来存储id,时间,内容,作者,评论数,赞次数..
    CommentItem用来存储各类提问,回答中的评论,根据id索引...

知乎内容提取和保存代码完成,详见更新...<br>

基本上都是xpath内容提取步骤, 因为只要到达所需要的页面后, 要做的也就剩下xpath了<br>

也不提倡在spider中做分析, 撑死做一个数据过滤, 明确分工才对<br>

后半段流程介绍:

    1、登录成功后, 携带cookie, header 访问 (www.zhihu.com) 首页
    2、提取首页的推荐问答信息(默认5条, 暂时不多取, 示例爬虫没必要)
    3、根据每个问答的url进入问答详情页面(一层for)
    4、问答详情页面的问题描述最先提取, 其次为回复层(二层遍历)
    5、在回复层(问答问答,这个叫做答案可能更好一些)中, 遍历评论层(三层遍历)
    6、提取信息完毕后yield item
    7、编写pipelines.py文件, 编写存储步骤, 所有关于数据库操作都在这里执行
    8、修改settings.py, 修改ITEM_PIPELINES配置, 加入自己编写的pipeline类, 添加数据库信息配置

### 六、代理
在爬虫工作过程中, 有很多种方法可以避免自己的ip被网站封禁策略拒之门外<br>

常见的有：
    
    1、添加header信息, 尽可能模仿真实用户访问(使用user agent池)
    2、合理的使用cookie信息
    3、设置爬虫频率, 以保证网站正常运行为前提进行爬取
    4、设置代理ip
    5、分布式爬虫

关于header信息的配置在zhihu爬虫上已经实际使用过, 但是并没有使用到user agent池, 因为知乎的登陆后访问,需要携带header和cookie信息,<br>

在访问新闻, 博客, 分类信息网站等无须登录, 爬取频率较高的网站时, 就需要配置User Agent池了, 也算是一种减小被网站捉到我们小爬虫的一种可行方法吧.<br>

cookie信息, 也是要具体问题具体分析, 大部分无须登录的网站来讲, 直接禁用cookie最为妥当.<br>

爬取频率...本着人道主义精神, 在保证人家网站正常运行不死机的情况下, 合理的调整爬取频率吧...<br>

分布式爬虫...后面另开一节专门讲, 其实scrapyd也算的上是一个python 分布式爬虫框架, 合理使用就可以达到意想不到的效果.<br>

这里我们主要是讲第四条, 代理IP<br>

讲在前面, 合理的收费才是保证提供良好服务的基础.<br>

so....有条件的就找个好的代理ip网站, 买个几万条, 或者买个会员, ip实时更新, 稳的一匹.(我就不打广告了, 反正我用的免费的)<br>

在scrapy中应用ip代理, 算不上太麻烦的事情.<br>

有简单的, 直接在settings.py中写如全局变量, ip pool, 添加一批可用的ip, 然后在spider文件中, 手动切换(仅提供这思路, 不建议这么做)<br>

我们这里用到的是, 自定义  中间件(Middleware)  并在settings.py中启用自定义的中间件.<br>

中间件, 详细信息可参考(http://scrapy-chs.readthedocs.io/zh_CN/0.24/topics/spider-middleware.html)[Scrapyd Middleware]<br>

主要是在其中添加代码来处理发送给 Spiders 的 response 及 spider 产生的 item 和 request.<br>

添加代理的操作, 就在 Middleware 中的 process_request 方法中.<br>

```python
    proxies = '***.***.**.***:*****'
    request.meta['proxy'] = proxies
```
不考虑其他操作的话, 在process_request方法中有这一句, 就完成了一个代理ip的设置.<br>

完成代理ip的切换后, 可以在 process_response 方法中检测使用该代理ip访问后的处理结果, 根据处理结果来进行进一步的操作.<br>

代理, 我们这里用到的是(https://github.com/kohn/HttpProxyMiddleware)[kohn] 朋友的代理文件, 我觉得写的很好,<br>

虽然很久没更新, 但是主题思路参考, 针对版本更新做一些小修改就可以直接使用上去.<br>

[fetch_free_proxy.py]文件虽然有写好现成的规则和网站, 但是仅当提供思路, 因为网站会有更新, 如果无法直接抓取到代理IP,<br>

则需要自己对该文件进行修改, 也可以将自己觉得比较好的代理网站抓取规则写在里面, 就可以很好的融入整个代理流程中.<br>

自己写了一个抓取代理IP的爬虫, 不是使用urllib.request抓取,<br>

目标是:  既然使用scrapyd框架运行, 就将实际工作爬虫和代理抓取爬虫同时运行, 使用scrapy-redis保存代理信息, 并在middlewares中获取并使用.<br>

