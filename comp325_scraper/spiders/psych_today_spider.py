import scrapy


class PsychTodaySpider(scrapy.Spider):
    name = "psychtoday"

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        return [scrapy.Request(url="https://www.psychologytoday.com/us/therapists/nc/chapel-hill", callback=self.parse, headers=headers)]

    def parse(self, response):
        for name in response.xpath('//a[@class="result-name"]/@href').getall():
            self.log(name)
