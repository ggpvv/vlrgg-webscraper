from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys
from expression import Ok, Result, Error
from expression.extra.result import pipeline
from functools import partial

from utils import utils, functional_soup as fs

def event_games(event):
    html = partial(utils.scrape_url, get_match_urls)
    url_str = 'https://vlr.gg/event/matches/' + str(event) + '/?series_id=all&group=completed'
    urls_result = html(url_str)
    return urls_result
    # the function is correctly returning the html soup object of the matches page
    # urls will contain the list of the urls of all the matches for that event
    # scrape each url, getting whatever information is needed
    # build this into a dictionary containing the table data
    #match urls_result:
    #    case Success(value=val) as succ:
    #        return val.map(lambda x: x.upper())
    #    case Error() as failure:
    #        return failure


def get_match_urls(soup):
    def get_match_url(a_tag):
        return fs.attribute('href', a_tag).map(lambda x: 'https://vlr.gg' + x)
    match_items = fs.find_elements('a', {'class': 'match-item'}, soup)
    return utils.sequence_iter(
        match_items.map(lambda x: x.map(get_match_url)))
