import scrapy
from ..items import AdjectiveItem
import re

class AdjectiveSpider(scrapy.Spider):
    name = "adjective"
    allowed_domains = ['jisho.org']
    start_urls = [
        'https://jisho.org/search/%23jlpt-n5%20%23adjective',
        'https://jisho.org/search/%23jlpt-n4%20%23adjective',
        'https://jisho.org/search/%23jlpt-n3%20%23adjective',
        'https://jisho.org/search/%23jlpt-n2%20%23adjective',
        'https://jisho.org/search/%23jlpt-n1%20%23adjective',
    ]
    custom_settings = {
        'FEED_URI': "./data/adjective.json"
    }

    def parse(self, response):
        level_regex = re.compile('.*jlpt-(\S\S).*')
        adjective_regex = re.compile('.*adjective.*')

        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            m = level_regex.match(response.request.url)
            adjective = AdjectiveItem()
            adjective['level'] = m.group(1).upper()
            adjective['level_learned'] = card.xpath('.//span[@class="concept_light-tag label"]/text()').get().replace("JLPT", "").strip()
            adjective['kanji'] = ''.join([x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall()])
            adjective['kanji_list'] = [x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall() if x.strip() != '']
            
            furigana = card.xpath('.//span[@class="furigana"]/span')
            adjective['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]
            adjective['english_meanings'] = [x.strip() for x in card.xpath('.//span[@class="meaning-meaning"]/text()').getall() if x != '、']
            adjective['hiragana'] = [adjective['furigana'][x] if adjective['furigana'][x] is not '' else adjective['kanji'][x] for x in range(len(adjective['furigana']))]

            # Getting the related adjective
            switch = False
            adjective['adjective'] = []
            for wrap in card.xpath('.//div[@class="meanings-wrapper"]/div'):
                if (wrap.xpath('./@class').get() == 'meaning-tags'):
                    if (adjective_regex.match(wrap.xpath('./text()').get()) is not None):
                        switch = True
                    else:
                        switch = False
                elif (switch):
                    adjective['adjective'].append(wrap.xpath('.//span[@class="meaning-meaning"]/text()').get())

            yield adjective

        next_page = response.xpath('.//a[@class="more"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)