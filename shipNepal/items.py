# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShipnepalItem(scrapy.Item):
    # define the fields for your item here like:
    order_id = scrapy.Field()
    date = scrapy.Field()
    order_status = scrapy.Field()
    price = scrapy.Field()
    total = scrapy.Field()
    qty = scrapy.Field()
    tracking_number = scrapy.Field()
    weight = scrapy.Field()
    grand_total = scrapy.Field()
    pic = scrapy.Field()
    product_url = scrapy.Field()
    product_id =scrapy.Field()
    way_bill_number = scrapy.Field()
