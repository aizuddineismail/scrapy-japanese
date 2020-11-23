import scrapy
from ..items import VocabularyItem
import re

class VocabularySpider(scrapy.Spider):
    name = "vocabulary"
    allowed_domains = ['jisho.org']
    start_urls = [
        'https://jisho.org/search/%23jlpt-n5%20%23words',
        'https://jisho.org/search/%23jlpt-n4%20%23words',
        'https://jisho.org/search/%23jlpt-n3%20%23words',
        'https://jisho.org/search/%23jlpt-n2%20%23words',
        'https://jisho.org/search/%23jlpt-n1%20%23words',
    ]
    custom_settings = {
        'FEED_URI': "./data/vocabulary.json"
    }

    def parse(self, response):
        level_regex = re.compile('.*jlpt-(\S\S).*')
        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            m = level_regex.match(response.request.url)
            vocabulary = VocabularyItem()
            vocabulary['level'] = m.group(1).upper()
            vocabulary['level_learned'] = card.xpath('.//span[@class="concept_light-tag label"]/text()').get().replace("JLPT", "").strip()
            vocabulary['kanji'] = ''.join([x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall()])
            vocabulary['kanji_list'] = [x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall() if x.strip() != '']
            
            furigana = card.xpath('.//span[@class="furigana"]/span')
            vocabulary['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]
            vocabulary['english_meanings'] = [x.strip() for x in card.xpath('.//span[@class="meaning-meaning"]/text()').getall() if x != '、']
            vocabulary['hiragana'] = [vocabulary['furigana'][x] if vocabulary['furigana'][x] is not '' else vocabulary['kanji'][x] for x in range(len(vocabulary['furigana']))]
            
            yield vocabulary

        next_page = response.xpath('.//a[@class="more"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)