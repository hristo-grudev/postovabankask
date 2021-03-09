import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import PostovabankaskItem
from itemloaders.processors import TakeFirst


class PostovabankaskSpider(scrapy.Spider):
	name = 'postovabankask'
	start_urls = ['https://www.postovabanka.sk/novinky/']

	def parse(self, response):
		years_links = response.xpath('//ul[@class="news-header-year"]/li/a/@href').getall()
		yield from response.follow_all(years_links, self.parse_year)

	def parse_year(self, response):
		post_links = response.xpath('//div[@class="news-post-content"]/a[1]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//span[text()="Ďalšie články"]//parent::a/@href').getall()
		yield from response.follow_all(next_page, self.parse_year)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="box_genericperex pad_tb25 "]//text()[normalize-space() and not(ancestor::h1)]|//div[@class="news article-content"]//text()[normalize-space() and not(ancestor::ul)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//ul[@class="article-content-writtenby"]/li[1]/text()').get()

		item = ItemLoader(item=PostovabankaskItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
