import datetime
import redis

import scrapy
from javdbscrapy.items import JavdbscrapyItem
from urllib.parse import urlparse, parse_qs
import json

redis_client = redis.Redis(host='localhost', port=6379, db=5, decode_responses=True)
brand_list = ['ssis', 'vr', 'stars', 'midv', 'ipzz', 'juq', 'fsdss', 'ara', 'mium', 'gana', 'siro', 'maam', 'scute',
              'luxu', 'pred']


def save_to_redis(brand, issue_date):
    if redis_client.get(f'stop:{brand}') is None:
        redis_client.setex(f'stop:{brand}', 4 * 60 * 60, 1)
    else:
        redis_val = redis_client.get(f'stop:{brand}')
        redis_client.setex(f'stop:{brand}', 4 * 60 * 60, int(redis_val) + 1)
    times_ = redis_client.get(f'stop:{brand}')
    print(f'brand:{brand} 爬取到日期{issue_date}==> {times_} 次')


class JavdbspiderSpider(scrapy.Spider):
    name = "javdbspider"
    allowed_domains = ["javdb.com"]


    start_urls = [f'https://javdb.com/video_codes/{x}?page=1' for x in brand_list]

    def parse(self, response):
        page_urls = response.css('a.box')
        next_page_page_url = response.xpath('//a[@class="pagination-next"]/@href').get()
        for url in page_urls:
            url = url.css('a.box ::attr(href)').get()
            url = f'https://javdb.com{url}'
            redis_res = redis_client.get(url)
            if redis_res is not None:
                print(f'{url} ====> 已爬取，跳过')
                continue
            yield scrapy.Request(url=url, callback=self.parse_movies_page, meta={'brand_url': url})

        if next_page_page_url is not None and len(next_page_page_url) > 0:
            next_page_url = f'https://javdb.com{next_page_page_url}'
            next_page_brand = get_brand(next_page_url)
            val = redis_client.get(f'stop:{next_page_brand}')
            if val is None and int(val) <= 5:
                yield scrapy.Request(url=next_page_url, callback=self.parse)
            else:
                print(f'brand:{next_page_brand} 已停止，最后url{next_page_url}')

    def parse_movies_page(self, response):
        brand_url = response.meta['brand_url']

        cover_img = response.xpath('//img[@class="video-cover"]/@src').get()
        intro_video = response.xpath('//video[@id="preview-video"]/source/@src').get()
        intro_images = response.xpath(
            '//div[@class="tile-images preview-images"]//a[@class="tile-item"]/@href').getall()
        code = response.xpath('//strong[text()="ID:"]/following-sibling::span//text()').getall()
        code = ''.join(code)
        issue_date = response.xpath(
            '//strong[text()="Released Date:"]/following-sibling::span[@class="value"]/text()').get()
        time_length = response.xpath(
            '//strong[text()="Duration:"]/following-sibling::span[@class="value"]/text()').get()
        rate_detail = response.xpath(
            '//strong[text()="Rating:"]/following-sibling::span[@class="value"]/text()').get()
        actress = response.xpath('//strong[text()="Actor(s):"]/following-sibling::span[@class="value"]/strong['
                                 '@class="symbol female"]/preceding-sibling::a[1]/text()').getall()

        magent_links_div = response.xpath('//div[contains(@class,"item columns is-desktop")]')

        magent_links = []
        for link_div in magent_links_div:
            link_name = link_div.xpath('//div[contains(@class,"item columns is-desktop")]')[0].xpath(
                './/span[@class="name"]/text()').get()
            link_time = link_div.xpath('//div[contains(@class,"item columns is-desktop")]')[0].xpath(
                './/span[@class="time"]/text()').get()
            if link_time is not None:
                link_time = str(link_time).strip()
            link_meta = link_div.xpath('//div[contains(@class,"item columns is-desktop")]')[0].xpath(
                './/span[@class="meta"]/text()').get().strip()
            if link_meta is not None:
                link_meta = str(link_meta).split(',')[0].strip()
            link_url = link_div.xpath('//div[contains(@class,"item columns is-desktop")]')[0].xpath('.//a/@href').get()
            if link_url is not None:
                link_url = str(link_url).strip()

            magent_links.append({
                'link_name': link_name,
                'link_time': link_time,
                'link_size': link_meta,
                'link_url': link_url
            })

        javdb_item = JavdbscrapyItem()

        javdb_item['cover'] = cover_img
        javdb_item['intro_video'] = intro_video
        javdb_item['intro_images'] = intro_images
        javdb_item['code'] = code
        javdb_item['issue_date'] = issue_date
        javdb_item['time_length'] = time_length
        javdb_item['rate_detail'] = rate_detail
        javdb_item['actress'] = actress
        javdb_item['magent_links'] = magent_links
        javdb_item['insert_date'] = datetime.datetime.now()
        javdb_item['page_url'] = response.url
        javdb_item['page_content'] = response.text

        formatted_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        redis_client.set(response.url, json.dumps({'crawl_time': formatted_string, 'code': code}))

        if code is not None and len(code) > 0:
            if issue_date is not None and len(issue_date) > 0:
                print(f'{code}--{issue_date} ======> 不收录')
                if is_date_greater_than_date(issue_date):
                    yield javdb_item
                else:
                    brand = get_brand(brand_url)
                    save_to_redis(brand, issue_date)


def is_date_greater_than_date(issue_date):
    # 将日期字符串转换为date类型
    date1 = datetime.datetime.strptime(issue_date, '%Y-%m-%d').date()
    the_date = datetime.datetime.strptime('2018-01-01', '%Y-%m-%d').date()

    # 判断date1是否大于date2
    return date1 > the_date


def get_brand(uuu: str):
    parsed_url = urlparse(uuu)
    query_parameters = parse_qs(parsed_url.query)
    if 'q' in query_parameters:
        brand = query_parameters['q'][0].lower()
    else:
        brand = uuu.split('/')[-1].split('?')[0].lower()
    return brand
