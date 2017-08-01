import re, csv, requests, lxml.html, logging
from collections import namedtuple
from pprint import pprint as pp
from urllib.parse import urlparse, urljoin, urldefrag

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)

# TODO: track sources to each url
# TODO: get title of url
# TODO: check if URL 404s
Link = namedtuple("Link", field_names=["text", "url"])

def is_relative(url):
    return not bool(urlparse(url).netloc)

def find_all_links(url):

    logging.debug("Finding links in url: %s" % url)

    links = []

    response = requests.get(url)
    doc = lxml.html.fromstring(response.content)
    for atag in doc.cssselect("a"):

        text = re.sub(r'\s+', ' ', atag.text_content()).strip()
        new_url = atag.get('href')

        if not new_url or "mailto" in new_url: continue

        new_url, fragment = urldefrag(new_url)

        if is_relative(new_url):
            new_url = urljoin(url, new_url)
            link = Link(text, new_url)
            links.append(link)

    return links

def crawl_page(url, depth, urls_already_crawled=set()):

    if depth == 0:
        return []
    else:
        links = find_all_links(url)
        # TODO: this doesn't work right
        urls_already_crawled.add(url)
        for link in links:
            if link.url in urls_already_crawled: continue
            links += crawl_page(link.url, depth-1, urls_already_crawled)
        return links

start_url = "http://www.pollingreport.com/"
max_depth = 2

logging.info(f"Crawling start page {start_url} with max depth of {max_depth}")

links = crawl_page(start_url, depth=max_depth)

logging.info("Writing links to CSV...")

with open("pollingreport_links.csv", "w") as f:
    writer = csv.writer(f)
    for link in links:
        row = [link.text, link.url]
        logging.debug(row)
        writer.writerow(row)
