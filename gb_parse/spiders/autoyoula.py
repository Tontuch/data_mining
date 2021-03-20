import scrapy


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/rossiya/']

    _data_advert = {

    }

    _css_selectors = {
        'brands':".TransportMainFilters_brandsList__2tIkv "
                 ".ColumnItemList_container__5gTrc a."
                 "blackLink",
        'paginations': 'a.Paginator_button__u1e7D',
        'car': '.SerpSnippet_titleWrapper__38bZM a.SerpSnippet_name__3F7Yu'
    }
    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get('href')
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._css_selectors['brands'], self.brand_parse)



    def brand_parse(self, response, **kwargs):
        yield from self._get_follow(response, self._css_selectors['paginations'], self.brand_parse)

        yield from self._get_follow(response, self._css_selectors['car'], self.car_parse)

        print(1)

    def car_parse(self, response):
        print(1)
