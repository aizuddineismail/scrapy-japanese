import scrapy
from ..items import VocabularyItem

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
        'FEED_URI': "/data/vocabulary.json"
    }

    def parse(self, response):
        print(VocabularyItem())
        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            furigana = card.xpath('.//span[@class="furigana"]/span')
            
            vocabulary = VocabularyItem()
            vocabulary['kanji'] = [x for x in card.xpath('.//span[@class="text"]/node()').get().strip()]
            vocabulary['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]

            # print(card)