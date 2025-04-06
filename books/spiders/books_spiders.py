from pathlib import Path

import scrapy
from requests import Response

from books.items import BookItem


class BooksSpidersSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/catalogue/page-1.html']

    def parse(self, response: Response, **kwargs):
        books = response.css('article.product_pod h3 a::attr(href)').getall()
        for book_url in books:
            book_url = response.urljoin(book_url)
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css(".product_pod").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book(self, response):
        item = BookItem()

        item['title'] = response.css('div.product_main h1::text').get()
        item['price'] = response.css('p.price_color::text').get()
        item['amount_in_stock'] = response.css(".star-rating Four").get()
        item['rating'] = response.css('p.star-rating').attrib['class'].replace('star-rating', '').strip()
        item['category'] = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        description = response.css('div#product_description ~ p::text').get()
        item['description'] = description.strip() if description else ''
        item['upc'] = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()

        yield item
