

import scrapy
from shipNepal.items import ShipnepalItem
from urllib.parse import urlparse, parse_qs
from scrapy.loader import ItemLoader


class ShipnepalSpider(scrapy.Spider):
    name = 'shipnepal'
    allowed_domains = ['www.shipnepal.cn']
    start_urls = ['https://www.shipnepal.cn/en']
    page_number = 2

    def parse(self, response):

        yield scrapy.FormRequest("https://www.shipnepal.cn/login/enindexlogin", formdata={
            'no': "kachuwa@anzteams.com",
            "pwd": "Spidermann2"
        }, callback=self.start_scraping)

    def start_scraping(self, response):
        yield scrapy.Request("https://www.shipnepal.cn/i/myorder/enindex", callback=self.verifylogin)

        # yield scrapy.Request("https://www.shipnepal.cn/i/myorder/enindex?state=0&bt=&et=&pno=&id=41", callback=self.verifylogin)

    def get_product_url(self, str):

        position = str.find('http')

        url = str[position:]
        return url

    def get_product_id(self, str):

        url = self.get_product_url(str)

        parsed_url = urlparse(url)

        domain = parsed_url.netloc

        if domain.find("1688") > 0:

            if(domain.find('offerId') > 0):

                url_obj = parse_qs(parsed_url.query)
                id = url_obj['offerId'][0]
                return id
            else:
                path_with_html = parsed_url.path[7:]
                dot_index = path_with_html.find(".")
                final_url = path_with_html[:dot_index]
                return final_url

        url_obj = parse_qs(parsed_url.query)
        id = url_obj['id'][0]
        return id

    def verifylogin(self, response):
        final_data = []
        base_elements = response.xpath(
            "//table/tbody/tr/td/span[contains(@class,'lan-span')]")

        for element in base_elements:

            order_ids = element.xpath(
                ".//preceding::tr/th/div/div[@class='pull-left']/span/a/span/text()").extract()

            dates = element.xpath(
                ".//preceding::tr/th/div/div[@class='pull-left']/span/span[1]/text()").extract()

            order_id = order_ids[len(order_ids)-1]
            date = dates[len(dates)-1]

            order_status = element.xpath(
                ".//ancestor::tr/td[5]/span/text()").extract_first()

            price = element.xpath(
                ".//ancestor::tr/td[3]/span[1]/text()").extract_first()

            qty = element.xpath(
                ".//ancestor::tr/td[3]/span[2]/text()").extract_first()

            total = element.xpath(
                ".//ancestor::tr/td[4]/span/text()").extract_first()

            package_detail = element.xpath(
                ".//ancestor::tr/td[6]/span/a/@href").extract_first()

            product_url = self.get_product_url(element.xpath(
                ".//ancestor::tr/td[2]/a/@href").extract_first())

            product_id = self.get_product_id(element.xpath(
                ".//ancestor::tr/td[2]/a/@href").extract_first())

            product = {
                "order_status": order_status,
                "price": price,
                "qty": qty,
                "total": total,
                "package_detail": package_detail,
                "product_url": product_url,
                "product_id": product_id
            }

            data = {
                "order_id": order_id,
                "date": date,
                "products": [
                    product
                ]
            }

            if(len(final_data)):

                found_value = [
                    dictionary for dictionary in final_data if dictionary["order_id"] == order_id]
                if(len(found_value)):
                    found_value[0]["products"].append(product)
                else:
                    final_data.append(data)
            else:
                final_data.append(data)

        for data in final_data:
            items = ShipnepalItem()
            for product in data['products']:

                if product['package_detail'] is not None:
                    yield response.follow(url=product['package_detail'], callback=self.package_detail, meta={"data": data, "product": product})
                    # yield response.follow(url="/i/exlist/ensee/719", callback=self.package_detail, meta={"data": data, "product": product})

                else:
                

                    items['order_id'] = data["order_id"]
                    items['date'] = data["date"]
                    items['order_status'] = product["order_status"]
                    items['price'] = product["price"]
                    items['total'] = product["total"]
                    items['qty'] = product["qty"]
                    items['product_url'] = product['product_url']
                    items['product_id'] = product['product_id']
                    yield items

        next_page = "https://www.shipnepal.cn/i/myorder/enindex?state=0&bt=&et=&pno=&id=" + \
            str(ShipnepalSpider.page_number)
        current_attr = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "current", " " ))]/text()').extract_first()

        if current_attr is not None:
            ShipnepalSpider.page_number += 1
            yield response.follow(next_page, callback=self.verifylogin)

    def package_detail(self, response):

        items = ShipnepalItem()
        data = response.request.meta["data"]

        product = response.request.meta["product"]

        tracking_number = response.xpath(
            '//table/tbody/tr[2]/td[4]/a/text()').extract_first()

        weight = response.xpath(
            'normalize-space(//table/tbody/tr[6]/td[2]/text())').extract_first()

        grand_total = response.xpath(
            '//table/tbody/tr[5]/td[4]/text()').extract_first()

        check_pic_exits = response.xpath(
            '//table/tbody/tr/td[contains(@class, "tr td1") and normalize-space(text()) = "Entry Picture："]/text()').extract_first()

        way_bill_number = response.xpath(
            '//table/tbody/tr/td[contains(@class, "tr td1") and normalize-space(text()) = "Waybill Number:"]/text()').extract_first()

        pic = ''
        way_bill_num = ''
        if(check_pic_exits is not None):
            if "Entry Picture" in check_pic_exits:
                pic_url = response.xpath(
                    '//table/tbody/tr[8]/td[2]/a/img/@src').extract_first()
                pic = "https://www.shipnepal.cn" + pic_url
        if(way_bill_number):

            way_bill_num = response.xpath(
                '//table/tbody/tr/td[contains(@class, "tr td1") and normalize-space(text()) = "Waybill Number:"]/following-sibling::td/a/text()').extract_first()

        items['order_id'] = data["order_id"]
        items['date'] = data["date"]
        items['order_status'] = product["order_status"]
        items['price'] = product["price"]
        items['total'] = product["total"]
        items['qty'] = product["qty"]
        items['product_url'] = product['product_url']
        items['product_id'] = product['product_id']
        items['tracking_number'] = tracking_number
        items['weight'] = weight
        items['grand_total'] = grand_total
        items['pic'] = pic
        items['way_bill_number'] = way_bill_num

        yield items
