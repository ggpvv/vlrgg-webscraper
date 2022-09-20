from bs4 import BeautifulSoup
import pandas as pd
import requests
from expression import Ok, Result, Error, pipe, compose
from expression.collections import seq
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
    			fs.inner_text
    			)
    team2_score = pipeline(
    			team2_div,
    			score_div,
    			fs.inner_text
    			)
   
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
    
    def is_winner(team_div):
    	score_div = team_div.bind(partial(
    		        fs.find_element, 'div', {'class': 'mod-win'}))
    	match score_div:
    		case Ok():
    			return True
    		case _:
    			return False
    				
    row_data['Winner'] = (row_data['Team1'] 
    				if is_winner(overview_soup.bind(team1_div))
                                else row_data['Team2']
                         )
    # Team total rounds
    row_data['Team1TotalRounds'] = overview_soup.bind(team1_score)
    row_data['Team2TotalRounds'] = overview_soup.bind(team2_score)
    # Half scores and sides
    team1_half_rounds_fn = pipeline(
    			  team1_div,
    			  partial(fs.find_elements, 'span', {})
    			  )
    team2_half_rounds_fn = pipeline(
    			  team2_div,
    			  partial(fs.find_elements, 'span', {})
    			  )
    
    def side(attribute):
        result = 'attack' if attribute == 'mod-t' else 'defense'
        return result
    
    first_half_side = compose(
    			seq.head,
    			partial(fs.attribute, 'class'),
    			result.map(lambda x: x[0])
    			)    			
    row_data['Team1_SideFirstHalf'] = overview_soup.bind(
    					pipeline(
    					    team1_half_rounds_fn,
    					    first_half_side
    					    )
    					).map(side)
    row_data['Team2_SideFirstHalf'] = overview_soup.bind(
    					pipeline(
    					    team2_half_rounds_fn,
    					    first_half_side
    					    )
    					).map(side)
    return row_data                            
