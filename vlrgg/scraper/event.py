from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys
from expression import Ok, Result, Error, pipe, compose
from expression.core import result
from expression.extra.result import pipeline
from functools import partial

from vlrgg.utils import utils, functional_soup as fs
from vlrgg.scraper import match

def event_matches(event):
    url_str = 'https://vlr.gg/event/matches/' + str(event) + '/?series_id=all&group=completed'
    urls = partial(utils.scrape_url, match_urls)
    scrape_match = partial(utils.scrape_url, match.match_data)
    return pipe(
                url_str,
                urls,
                result.map(lambda x: x.map(scrape_match)),
                result.map(lambda x: x.map(lambda x: utils.sequence_iter(Ok(x)))),
                utils.sequence_iter
           )


def event_games(event):
    pass

def match_urls(soup):
    def match_url(a_tag):
        return fs.attribute('href', a_tag).map(lambda x: 'https://vlr.gg' + x)
    match_items = fs.find_elements('a', {'class': 'match-item'}, soup)
    return utils.sequence_iter(
        match_items.map(lambda x: x.map(match_url))
        )
