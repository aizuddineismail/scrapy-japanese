import scrapy
from ..items import CounterItem
import re

class CounterSpider(scrapy.Spider):
    name = "counter"
    allowed_domains = ['jisho.org']
    start_urls = [
        'https://jisho.org/search/%23jlpt-n5%20%23counter',
        'https://jisho.org/search/%23jlpt-n4%20%23counter',
        'https://jisho.org/search/%23jlpt-n3%20%23counter',
        'https://jisho.org/search/%23jlpt-n2%20%23counter',
        'https://jisho.org/search/%23jlpt-n1%20%23counter',
    ]
    custom_settings = {
        'FEED_URI': "./data/counter.json"
    }

    def parse(self, response):
        level_regex = re.compile('.*jlpt-(\S\S).*')
        counter_regex = re.compile('.*Counter.*')

        for card in response.xpath('//div[@class="concept_light clearfix"]'):
            m = level_regex.match(response.request.url)
            counter = CounterItem()
            counter['level'] = m.group(1).upper()
            counter['level_learned'] = card.xpath('.//span[@class="concept_light-tag label"]/text()').get().replace("JLPT", "").strip()
            counter['kanji'] = ''.join([x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall()])
            counter['kanji_list'] = [x.strip() for x in card.xpath('.//span[@class="text"]//text()').getall() if x.strip() != '']
            
            furigana = card.xpath('.//span[@class="furigana"]/span')
            counter['furigana'] = [x.xpath('.//node()').get() if x.xpath('.//node()').get() is not None else '' for x in furigana]
            counter['english_meanings'] = [x.strip() for x in card.xpath('.//span[@class="meaning-meaning"]/text()').getall() if x != '、']
            counter['hiragana'] = [counter['furigana'][x] if counter['furigana'][x] is not '' else counter['kanji'][x] for x in range(len(counter['furigana']))]

            # Getting the related counter
            switch = False
            counter['counter'] = []
            for wrap in card.xpath('.//div[@class="meanings-wrapper"]/div'):
                if (wrap.xpath('./@class').get() == 'meaning-tags'):
                    if (counter_regex.match(wrap.xpath('./text()').get()) is not None):
                        switch = True
                    else:
                        switch = False
                elif (switch):
                    counter['counter'].append(wrap.xpath('.//span[@class="meaning-meaning"]/text()').get())

            yield counter

        next_page = response.xpath('.//a[@class="more"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)