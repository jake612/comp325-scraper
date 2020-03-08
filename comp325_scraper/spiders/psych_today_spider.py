import scrapy


class PsychTodaySpider(scrapy.Spider):
    name = "psychtoday"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        return [scrapy.Request(url="https://www.psychologytoday.com/us/therapists/nc/chapel-hill", callback=self.parse, headers=self.headers)]

    def parse(self, response):
        # iterates over a list of all the links to therapist page
        therapist_pages = response.xpath('//a[@class="result-name"]')

        yield from response.follow_all(therapist_pages, headers=self.headers, callback=self.parse_therapist)

    def parse_therapist(self, response):
        yield {'name': response.xpath('//h1[@itemprop="name"]/text()').get().strip()}

