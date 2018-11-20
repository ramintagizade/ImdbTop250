# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    rating = scrapy.Field()
    duration = scrapy.Field()
    genre = scrapy.Field()
    issue_date = scrapy.Field()
    issue_country = scrapy.Field()
    directors = scrapy.Field()
    stars = scrapy.Field()
    metascore = scrapy.Field()
    popularity = scrapy.Field()
    



