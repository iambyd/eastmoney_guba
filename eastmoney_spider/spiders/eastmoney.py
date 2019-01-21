# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from eastmoney_spider.items import EastmoneySpiderItem
import re
import math
import json


class EastmoneySpider(scrapy.Spider):
    name = 'eastmoney'
    allowed_domains = ['eastmoney.com']
    start_urls = [
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=1',
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=2',
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=3',
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=4',
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=5',
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=6'
    ]

    def parse(self, response):
        """1.爬取所有个股吧的首页"""
        ngbglist = Selector(response).xpath(
            '//div[@class="ngbglistdiv"]/ul/li'
        ).extract()
        for ngbg in ngbglist:
            item1 = EastmoneySpiderItem()
            item1['stockname'] = re.sub(r'<.*?>', '', ngbg)
            item1['home_page'] = "http://guba.eastmoney.com/" + Selector(text=ngbg).xpath(
                '//a/@href').extract_first()
            yield scrapy.Request(
                url=item1['home_page'],
                meta={'item1': item1},
                callback=self.parse_page_num,
                dont_filter=True
            )

    def parse_page_num(self, response):
        """2.获取每个股吧所有的页面list"""
        item1 = response.meta['item1']
        try:
            data_pager = Selector(response).xpath(
                '// div[@id="articlelistnew"]/div[@class="pager"]/span/@data-pager'
            ).extract_first()
            # 获取帖子总数
            article_sum = int(data_pager.split('|')[1])
            # 获取每页帖子数量
            per_num = int(data_pager.split('|')[2])
            # 获取帖子页数
            data_page = math.ceil(article_sum / per_num)
        except:
            # 若仅有一页，那么data-pager将直接没有，直接取值为1
            data_page = 1
        # 将每页贴子网页传送到下一个方法中
        for p in range(data_page):
            page_url = response.url.split('.html')[0] +\
                '_' + str(p + 1) + '.html'
            yield scrapy.Request(
                url=page_url,
                meta={'item1': item1},
                callback=self.get_article_url,
                dont_filter=True
            )

    def get_article_url(self, response):
        """3.获取每页帖子的url信息"""
        item1 = response.meta['item1']
        articlelistnew = Selector(response).xpath(
            '//div[@id="articlelistnew"]/div'
        ).extract()
        # 除去首个元素为标题及尾部两行无效内容，对剩下的内容进行解析
        for article in articlelistnew:
            # 每条评论数据的div的class属性中含有articleh字眼，进行无效数据过滤
            if "articleh" in article:
                item2 = EastmoneySpiderItem()
                item2['stockname'] = item1['stockname']
                item2['home_page'] = item1['home_page']
                # 获取阅读数
                item2['forward'] = Selector(text=article).xpath(
                    '//span[@class="l1"]/text()').extract_first()
                # 获取评论数
                item2['comment'] = Selector(text=article).xpath(
                    '//span[@class="l2"]/text()').extract_first()
                # 摘取每个帖子的url地址
                item2['article_url'] = "http://guba.eastmoney.com" +\
                    Selector(text=article).xpath('//a/@href').extract_first()
                yield scrapy.Request(
                    url=item2['article_url'],
                    meta={'item2': item2},
                    callback=self.get_article_detail,
                    dont_filter=False
                )

    def get_article_detail(self, response):
        """4.对每个帖子进行数据抓取"""
        item2 = response.meta['item2']
        # 拼接得到最终期望得到的数据
        item_end = EastmoneySpiderItem()
        item_end['stockname'] = item2['stockname']
        item_end['home_page'] = item2['home_page']
        item_end['forward'] = item2['forward']
        item_end['comment'] = item2['comment']
        item_end['article_url'] = item2['article_url']
        # 抓取作者信息
        item_end['author'] = json.loads(Selector(response).xpath(
            '//div[@id="zwcontent"]/div[@id="zwcontt"]/div[@class="data"]/@data-json').extract_first()
        )
        # 获取帖子发表时间
        zwfbtime = Selector(response).xpath(
            '//div[@id="zwconttb"]/div[@class="zwfbtime"]/text()'
        ).extract_first().split(' ')[1:3]
        item_end['fb_date'] = zwfbtime[0]
        item_end['fb_time'] = zwfbtime[1]
        # 获取帖子内容
        # 标题
        item_end['title'] = Selector(response).xpath(
            '//div[@id="post_content"]/div[@id="zwconttbt"]/text()'
        ).extract_first().strip()
        # 正文
        item_end['content'] = re.sub(
            r'<.*?>', '',
            Selector(response).xpath(
                '//div[@id="post_content"]/div[@id="zwconbody"]/div'
            ).extract_first()
        ).strip().replace('\u3000', '').replace('&gt;', '')
        # print(item)
        yield item_end
