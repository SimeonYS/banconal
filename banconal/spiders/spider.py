import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbanconalItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.banconal.com.pa/index.php?option=com_content&view=category&layout=blog&id=10&Itemid=166&limitstart={}'

class BbanconalSpider(scrapy.Spider):
	name = 'banconal'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		yield response.follow(response.url, self.parse_post, dont_filter=True)

		if len(response.xpath('//article')) == 5:
			self.page += 5
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		articles = response.xpath('//article')
		length = len(articles)

		for index in range(length):
			item = ItemLoader(item=BbanconalItem(), response=response)
			item.default_output_processor = TakeFirst()

			date = "Not stated"
			title = response.xpath(f'(//article)[{index + 1}]/h3/text()').get().strip()
			content = response.xpath(f'(//article)[{index + 1}]//em//text()').getall() + response.xpath(f'(//article)[{index + 1}]/p//text()').getall()
			content = [p.strip() for p in content if p.strip()]
			content = re.sub(pattern, "", ' '.join(content))
			item.add_value('title', title)
			item.add_value('link', response.url)
			item.add_value('content', content)
			item.add_value('date', date)

			yield item.load_item()
