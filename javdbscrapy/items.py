# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JavdbscrapyItem(scrapy.Item):

    code = scrapy.Field()
    issue_date = scrapy.Field()
    time_length = scrapy.Field()
    rate_detail = scrapy.Field()
    actress = scrapy.Field()
    intro_images = scrapy.Field()
    cover = scrapy.Field()
    intro_video = scrapy.Field()
    magent_links = scrapy.Field()
    insert_date = scrapy.Field()
    page_url = scrapy.Field()
    page_content = scrapy.Field()
    batch_num = scrapy.Field()
    tag_list = scrapy.Field()


