from itertools import cycle
import requests
from lxml import html


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = html.fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"no")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


PROXIES = cycle([
    # localhost
    # "http://localhost:8899"
    # United States - Auburn
    "http://208.80.28.208:8080",
    # France
    # "http://159.8.114.37:8123"  # port 80 and 25
    "http://62.210.69.176:5566",
    "http://159.8.114.34:8123",
    # Canada
    "http://198.50.163.192:3129",
    "http://142.93.147.210:3128"
])

USER_AGENTS = cycle([
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
])

SOURCES = cycle([
    # google
    ("https://google.com/search",
     "//div[@class='yuRUbf']/a/@href"),
    # bing
    ("https://bing.com/search",
     "//*[@class='b_algo']/h2/a/@href"),
    # ecosia
    # ("https://ecosia.org/search",
    #  "//a[@class='result-url js-result-url']/@href"),
    # duckduckgo
    ("https://lite.duckduckgo.com/lite",
     "//a[@class='result-link']/@href"),
    # startpage
    ("https://startpage.com/do/search",
     "//a[@class='w-gl__result-title result-link']/@href")
])
