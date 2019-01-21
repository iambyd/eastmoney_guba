# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneySpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stockname = scrapy.Field()
    home_page = scrapy.Field()
    forward = scrapy.Field()
    comment = scrapy.Field()
    article_url = scrapy.Field()
    author = scrapy.Field()
    fb_date = scrapy.Field()
    fb_time = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
