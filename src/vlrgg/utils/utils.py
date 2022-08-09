from bs4 import BeautifulSoup
import requests
from expression import Ok, Result, Error
from expression.extra.result import pipeline

def scrape_url(strategy, url):
    url_pipe = pipeline(
                get_html,
                strategy)
    return url_pipe(url)


def get_html(url):
    events_resp = requests.get(url, timeout=10)
    if events_resp:
        return Ok(BeautifulSoup(events_resp.text, 'lxml'))
    else:
        return Error('Please check the URL of the webpage')
