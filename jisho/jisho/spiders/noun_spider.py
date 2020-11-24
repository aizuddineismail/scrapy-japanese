import scrapy
from ..items import NounItem
import re

class NounSpider(scrapy.Spider):
    name = "noun"
    allowed_domains = ['jisho.org']
    start_urls = [
        'https://jisho.org/search/%23jlpt-n5%20%23noun',
        'https://jisho.org/search/%23jlpt-n4%20%23noun',
        'https://jisho.org/search/%23jlpt-n3%20%23noun',
        'https://jisho.org/search/%23jlpt-n2%20%23noun',
        'https://jisho.org/search/%23jlpt-n1%20%23noun',
    ]
    custom_settings = {
        'FEED_URI': "./data/noun.json"
    }

    def parse(self, response):
        level_regex = re.compile('.*jlpt-(\S\S).*')
        noun_regex = re.compile('.*Noun.*')

        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            m = level_regex.match(response.request.url)
            noun = NounItem()
            noun['level'] = m.group(1).upper()
            noun['level_learned'] = card.xpath('.//span[@class="concept_light-tag label"]/text()').get().replace("JLPT", "").strip()
            noun['kanji'] = ''.join([x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall()])
            noun['kanji_list'] = [x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall() if x.strip() != '']
            
            furigana = card.xpath('.//span[@class="furigana"]/span')
            noun['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]
            noun['english_meanings'] = [x.strip() for x in card.xpath('.//span[@class="meaning-meaning"]/text()').getall() if x != '、']
            noun['hiragana'] = [noun['furigana'][x] if noun['furigana'][x] is not '' else noun['kanji'][x] for x in range(len(noun['furigana']))]

            # Getting the related noun
            switch = False
            noun['noun'] = []
            for wrap in card.xpath('.//div[@class="meanings-wrapper"]/div'):
                if (wrap.xpath('./@class').get() == 'meaning-tags'):
                    if (noun_regex.match(wrap.xpath('./text()').get()) is not None):
                        switch = True
                    else:
                        switch = False
                elif (switch):
                    noun['noun'].append(wrap.xpath('.//span[@class="meaning-meaning"]/text()').get())

            yield noun

        next_page = response.xpath('.//a[@class="more"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)