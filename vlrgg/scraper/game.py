from bs4 import BeautifulSoup
import pandas as pd
import requests
from expression import Ok, Result, Error, pipe, compose
from expression.core import result
from expression.extra.result import pipeline
from functools import partial

from vlrgg.utils import utils, functional_soup as fs
from vlrgg.scraper import match


def game_data(root_url, game_id):
    row_data = {}
    overview_soup = pipeline(
                        partial(utils.scrape_url, utils.html_text)
                        partial(fs.find_element, 'div', 
                                {'class': 'vm-stats-game',
                                 'data-game-id': game_id}))
    # Team total rounds
    team1_div = partial(fs.find_element, 'div', {'class': 'team'})
    team2_div = partial(fs.find_element, 'div', {'class': 'team mod-right'})
                                 
