# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JishoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class VocabularyItem(scrapy.Item):
    level = scrapy.Field()
    level_learned = scrapy.Field()
    hiragana = scrapy.Field()
    kanji = scrapy.Field()
    kanji_list = scrapy.Field()
    furigana = scrapy.Field()
    english_meanings = scrapy.Field()