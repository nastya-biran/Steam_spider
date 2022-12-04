import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import re
from spider_steam.items import SpiderSteamItem

queries = ['Инди', 'Майнкрафт', 'Шутер']



class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    pages = [1, 2]

    def start_requests(self):
        for query in queries:
            for page in self.pages:
                url = 'https://store.steampowered.com/search/' + urlencode(
                    {'term': query, 'page': str(page)})
                yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        product_urls =  set()
        for res in response.xpath('//a[@data-gpnav="item"]/@href').extract():
            if 'app' in res:
                product_urls.add(res)

        for product_url in product_urls:
            yield scrapy.Request(url=product_url, callback=self.parse_product_page)

    def parse_product_page(self, response):
        item = SpiderSteamItem()
        name = response.xpath('//div[@class="apphub_AppName" and @id="appHubAppName"]/text()').extract()
        category = response.xpath('//div[@class="blockbg"]//a/text()').extract()
        category = category[1:]
        rating_str = response.xpath('//div[@class="user_reviews_summary_row" and @itemprop="aggregateRating"]/@data-tooltip-html').extract()
        if rating_str is not None and len(rating_str) > 0 and re.search(r'\d',rating_str[0]) is not None:
            rating = re.search(r'\d+%', rating_str[0])[0]
            rating_str[0] = rating_str[0].replace(rating, '')
            reviews_count = re.search(r'[,\d]+[^%]', rating_str[0])[0]
        else:
            rating = ''
            reviews_count = ''
        release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()
        developer = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        tags = [x.strip() for x in response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()]
        price = response.xpath('//div[@class="game_purchase_action"]//div[@class="game_purchase_price price"]/text()').extract()
        if price is not None and len(price) > 0:
            price = price[0].strip()
        platforms = {*[x.strip() for x in response.xpath('//@data-os').extract()]}
        item["name"] = ''.join(name).strip()
        item["category"] = '/'.join(category).strip()
        item["reviews_count"] = ''.join(reviews_count).strip()
        item["rating"] = ''.join(rating).strip()
        item["release_date"] = ''.join(release_date).strip()
        item["developer"] = ''.join(developer).strip()
        item["tags"] = tags
        item["price"] = price
        item["platforms"] = ', '.join(platforms)
        yield item
