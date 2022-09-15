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
    match_soup = utils.html_text(root_url)
    overview_soup = match_soup.bind(
    		partial(fs.find_element, 'div', {'class': 'vm-stats-game',
                                 		 'data-game-id': game_id}))
    # Team divs
    team1_div = partial(fs.find_element, 'div', {'class': 'team'})
    team2_div = partial(fs.find_element, 'div', {'class': 'team mod-right'})
    score_div = partial(fs.find_element, 'div', {'class': 'score'})
    team1_score = pipeline(
    			team1_div,
    			score_div,
    			fs.inner_text)
    team2_score = pipeline(
    			team2_div,
    			score_div,
    			fs.inner_text)
   
    # GameID and MatchID
    row_data['GameID'] = Ok(game_id)
    row_data['MatchID'] = match_soup.bind(match.match_id)
    # Map
    map_name = pipeline(
    		partial(fs.find_element, 'div', {'class': 'map'}),
    		partial(fs.find_element, 'span', {}),
    		fs.stripped_strings)
    row_data['Map'] = overview_soup.bind(map_name).map(
    				lambda x: x[0])
    # Team IDs
    row_data['Team1ID'] = match_soup.bind(partial(match.team_id, 1))
    row_data['Team2ID'] = match_soup.bind(partial(match.team_id, 2))
    # Team names and winner
    row_data['Team1'] = match_soup.bind(partial(match.team_name, 1))
    row_data['Team2'] = match_soup.bind(partial(match.team_name, 2))
    row_data['Winner'] = 
    # Team total rounds
    row_data['Team1TotalRounds'] = overview_soup.bind(team1_score)
    row_data['Team2TotalRounds'] = overview_soup.bind(team2_score)
    
    return row_data                            
