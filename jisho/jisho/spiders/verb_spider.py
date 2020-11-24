import scrapy
from ..items import VerbItem
import re

class VerbSpider(scrapy.Spider):
    name = "verb"
    allowed_domains = ['jisho.org']
    start_urls = [
        'https://jisho.org/search/%23jlpt-n5%20%23verb',
        'https://jisho.org/search/%23jlpt-n4%20%23verb',
        'https://jisho.org/search/%23jlpt-n3%20%23verb',
        'https://jisho.org/search/%23jlpt-n2%20%23verb',
        'https://jisho.org/search/%23jlpt-n1%20%23verb',
    ]
    custom_settings = {
        'FEED_URI': "./data/verb.json"
    }

    def parse(self, response):
        level_regex = re.compile('.*jlpt-(\S\S).*')
        verb_regex = re.compile('.*verb.*')
        suru_regex = re.compile('.*Suru verb.*')

        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            m = level_regex.match(response.request.url)
            verb = VerbItem()
            verb['level'] = m.group(1).upper()
            verb['level_learned'] = card.xpath('.//span[@class="concept_light-tag label"]/text()').get().replace("JLPT", "").strip()
            verb['kanji'] = ''.join([x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall()])
            verb['kanji_list'] = [x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall() if x.strip() != '']
            
            furigana = card.xpath('.//span[@class="furigana"]/span')
            verb['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]
            verb['english_meanings'] = [x.strip() for x in card.xpath('.//span[@class="meaning-meaning"]/text()').getall() if x != '、']
            verb['hiragana'] = [verb['furigana'][x] if verb['furigana'][x] is not '' else verb['kanji'][x] for x in range(len(verb['furigana']))]

            # Getting the related verb
            switch = False
            verb['verb'] = []
            for wrap in card.xpath('.//div[@class="meanings-wrapper"]/div'):
                if (wrap.xpath('./@class').get() == 'meaning-tags'):
                    if (verb_regex.match(wrap.xpath('./text()').get()) is not None):
                        switch = True
                        if (suru_regex.match(wrap.xpath('./text()').get())):
                            verb['isSuru'] = True
                    else:
                        switch = False
                elif (switch):
                    verb['verb'].append(wrap.xpath('.//span[@class="meaning-meaning"]/text()').get())

            if('isSuru' not in verb):
                verb['isSuru'] = False
            yield verb

        next_page = response.xpath('.//a[@class="more"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)