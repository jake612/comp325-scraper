import scrapy


class PsychTodaySpider(scrapy.Spider):
    name = "psychtoday"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def generate_request_urls(self, base_url):
        requests = []
        if self.pages is None:
            self.pages = 1
        else:
            self.pages = int(self.pages)

        for page in range(self.pages):
            target_url = base_url + str(page * 20 + 1)
            requests.append(scrapy.Request(url=target_url, callback=self.parse, headers=self.headers))

        return requests

    def start_requests(self):
        base_url = "https://www.psychologytoday.com/us/therapists/{}/{}?sid=5e73cc0863d4a&rec_next=".format(self.state, self.city)
        return self.generate_request_urls(base_url)

    def parse(self, response):
        # iterates over a list of all the links to therapist page
        therapist_pages = response.xpath('//a[@class="result-name"]')

        yield from response.follow_all(therapist_pages, headers=self.headers, callback=self.parse_therapist)

    def parse_therapist(self, response):
        def extract_data(query):
            result = response.xpath(query).get()
            if result is None:
                return "N/A"
            else:
                return result.strip()

        def extract_street_details(path, query):
            result = path.xpath(query).get()
            if result is None:
                return "N/A"
            else:
                return result.strip()

        def get_in_list(query, splitter):
            list = response.xpath(query).getall()
            if len(list) == 0:
                return "N/A"
            else:
                return_string = ""
                for item in list:
                    return_string += item.strip() + splitter
                return return_string[:-(len(splitter))]

        def get_cost(query):
            list_items = response.xpath(query).getall()
            for item in list_items:
                item = item.strip()
                if len(item) > 0 and item[0] == '$':
                    return item

            return "N/A"


        address_details = response.xpath('//div[@class="address-data"]/span')

        yield {
            'name': extract_data('//h1[@itemprop="name"]/text()'),
            'street': extract_street_details(address_details, '//span[@itemprop="streetAddress"]/text()'),
            'locality': extract_street_details(address_details, '//span[@itemprop="addressLocality"]/text()'),
            'region': extract_street_details(address_details, '//span[@itemprop="addressRegion"]/text()')[:-1],
            'postalcode': extract_street_details(address_details, '//span[@itemprop="postalcode"]/text()'),
            'number': extract_data('//a[@class="phone-number"]/text()'),
            'insurance': get_in_list('//div[@class="spec-list attributes-insurance"]/div[@class="col-split-xs-1 col-split-md-2"]/ul[@class="attribute-list copy-small"]/li/text()', ", "),
            'specialties': get_in_list('//ul[@class="attribute-list specialties-list"]/li/text()', ', '),
            'treatment-approach': get_in_list('//div[@class="spec-list attributes-treatment-orientation"]/div[@class="col-split-xs-1 col-split-md-1"]/ul[@class="attribute-list copy-small"]/li/button/span/text()', ', '),
            'cost': get_cost('//div[@class="profile-finances details-section top-border"]/ul/li/text()')
        }

