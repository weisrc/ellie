import db
from models import embed, langid  # , getkw
from lxml import html
import httpx
import asyncio
import profiles
from urllib.parse import urlparse
import shortuuid
import struct
from collections import Counter
import re


def most_frequent(arr):
    occurence_count = Counter(arr)
    print(occurence_count.most_common(1))
    return occurence_count.most_common(1)[0][0]


TIMEOUT = 5


async def fetch_json(proxies, *args, **kwargs):
    async with httpx.AsyncClient(proxies=proxies, timeout=TIMEOUT) as client:
        response = await client.get(*args, **kwargs)
        return response.json()


async def fetch(proxies, *args, **kwargs):
    async with httpx.AsyncClient(proxies=proxies, timeout=TIMEOUT) as client:
        response = await client.get(*args, **kwargs)
        return response.text


async def fetch_serp(proxies, url, query, user_agent):
    return await fetch(proxies, url, params={"q": query}, headers={
        'User-Agent': user_agent})


async def fetch_serp_urls(proxies, source, query, user_agent):
    url, xpath = source
    page = await fetch_serp(proxies, url, query, user_agent)
    # with open("serp.html", "w") as f:
    #     f.write(
    #         f"proxy: {proxies.get('http')}, source: {source[0]}, user-agent: {user_agent}, page: {str(page)}")
    tree = html.fromstring(page)
    return tree.xpath(xpath)


def parse_title(tree):
    title = tree.xpath("//title[1]/text()")
    if title:
        return title[0][:255]
    headers = tree.xpath("//h1|h2|h3")
    return headers[0].text_content[:255] if headers else ""


def remove_html_tags(text):
    """Remove html tags from a string"""

    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)


def parse_description(tree):
    description = tree.xpath("//meta[@name='description'][1]/@content")
    if description:
        return description[0][:255]
    paragraphs = tree.xpath("//p[1]")
    if paragraphs and len(paragraphs[0].strip()) > 10:
        return remove_html_tags(paragraphs[0].text_content())[:255]
    return remove_html_tags(tree.text_content())[:255]


def parse_keywords(tree):
    keywords = tree.xpath("//meta[@name='keywords'][1]/@content")
    if keywords:
        return keywords[0][:255]
    content = remove_html_tags(tree.text_content())
    return ",".join(getkw(content))[:255]


def parse_urls(tree):
    return list(filter(lambda url: url.startswith("https://") or url.startswith("http://"), tree.xpath("//a[@href]/@href")))


def parse_lang(tree, title, description):
    lang = tree.get("lang")
    if lang:
        return lang[:2]
    elif description:
        return langid(description)
    elif title:
        return langid(title)
    else:
        return "??"


async def crawl_site(proxies, url):
    page = await fetch(proxies, url)
    tree = html.fromstring(page)
    title = parse_title(tree)
    description = parse_description(tree)
    # urls = parse_urls(tree)
    lang = parse_lang(tree, title, description)
    return title, description, lang  # , urls


async def fetch_domain_stats(proxies, domain):
    return await fetch_json(proxies, "https://web.informer.com/w/popup", params={"domain": domain, "format": "json"})


def try_int(string):
    try:
        return int(string)
    except:
        return None


async def want_domain_by_name(proxies, name):
    row = db.get_domain_by_name(name)
    if not row:
        stats = await fetch_domain_stats(proxies, name)
        if not stats.get("domainName"):
            return False
        id = shortuuid.uuid(name=name)
        trust = try_int(stats.get("mywotTrust"))
        privacy = try_int(stats.get("mywotPrivacy"))
        child_safety = try_int(stats.get("mywotChildSafety"))
        popularity = try_int(stats.get("sitePopularity"))
        alexa_rank = try_int(stats.get("siteAlexaRank"))
        rating_good = try_int(stats.get("siteadvisorRankGood"))
        rating_bad = try_int(stats.get("siteadvisorRankBad"))
        row = (id, name, trust, privacy, child_safety,
               popularity, alexa_rank, rating_good, rating_bad)
        db.insert_domain(*row)

    res = dict(zip(
        "id name trust privacy child_safety popularity alexa_rank rating_good rating_bad".split(), row))
    print(res)
    return res


def parse_url(url):
    parsed = urlparse(url)
    return parsed.scheme, parsed.netloc, parsed.path, parsed.query


async def index_site(proxies, url):
    try:
        domain = urlparse(url).netloc
        # url = f"{scheme}://{name}{path}{'?'+query if query else ''}"
        if db.exist_site_by_url(url):
            return False
        title, description, lang = await crawl_site(proxies, url)
        domain_id = (await want_domain_by_name(proxies, domain)).get("id")
        id = shortuuid.uuid(name=url)
        vector = embed(f"{title} {description}".lower())[0]
        bytes_vector = struct.pack("512f", *vector)
        db.insert_site(id, domain_id, bytes_vector,
                       url, title, description, lang)
        return lang
    except Exception as e:
        print(e)
        return False


async def search_and_index(query):
    proxies = {"http": next(profiles.PROXIES)}
    source = next(profiles.SOURCES)
    user_agent = next(profiles.USER_AGENTS)
    urls = await fetch_serp_urls(proxies, source, query, user_agent)
    langs = await asyncio.gather(*[index_site(proxies, url) for url in urls])
    db.commit()
    filtered = list(filter(lambda x: x, langs))
    print(filtered)
    return most_frequent(filtered) if len(filtered) else False
