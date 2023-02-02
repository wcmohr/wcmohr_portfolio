# epoch is the most current version of the function and will be called
# in the main notebook.
import numpy as np  # numpy will be used for vectorized calculations.
import sys
sys.path.append('..')
from pyglicko2.glicko2 import Player

class eloPlayer:
    # initialize the update rate
    _k = 16 
    def getRating(self):
        return self.__rating
    def setRating(self, rating):
        self.__rating = rating
    def __init__(self, rating = 1500):
        self.__rating = rating
    def update_player(self, rating_list, outcome_list):
        rating_list = np.array(rating_list).astype(float) # avoid exponentiation of int 
        # by negative value error.
        n = len(rating_list)
        # calculate expected wins
        expected_wins = np.divide(1,
                                  (1 + np.power(10,
                                                rating_list-self.__rating)/400))
        self.__rating = self.__rating + _k*(outcome_list - expected_wins)

def epoch(matches, players_dict):
    '''Take in a dataframe with matches, a list of players, a dictionary of players with the elements
    of player list as keys and an instance of the glicko2 class Player() as the value.
    This function wll return the updated players_list and players_dict.
    
    Future iterations of this function should do away with the p_ , and only should need the 
    players_dict with the keys as integers indicating the player id.
    '''
    players_list = list(players_dict.keys())
    players = [p for p in np.append(matches['winner_id'].unique(),\
                                                matches['loser_id'].unique())]
    # instantiate player class for players not yet instantiated
    players_to_instantiate = list(set(players) - set(players_list))
    
    new_players = {player: Player() for player in players_to_instantiate}
    # print(type(new_players))

    # update list of instantiated players
    players_list = list(set(players).union(set(players_list)))
    # update dictionary of instantiated players
    players_dict.update(new_players)
    # print(type(players_dict))
    # determine who competed and who didn't
    players_dnc = list(set(players_list) - set(players))
    players_compete = list(set(players_list)-set(players_dnc))
    # print(f'{players_compete=}')
    # update attributes for players who didn't compete
    for player in players_dnc:
        players_dict[player].did_not_compete()
    # fill dictionary with (wins,losses), a tuple of list of opponents in wins and losses for each match
    results = {}
    for player in players_compete:
        wins = [winner for winner in matches[matches['winner_id']==player]['loser_id']]
        losses = [loser for loser in matches[matches['loser_id']== player]['winner_id']]
        # get opponents' rating and rd
        # print(f'{wins=}')
        losses_rating = [players_dict[loss].getRating() for loss in losses ]
        losses_rd = [players_dict[loss].getRd() for loss in losses ]
        wins_rating = [players_dict[win].getRating() for win in wins ]
        wins_rd = [players_dict[win].getRd() for win in wins ]
        outcomes = np.append(np.ones(len(wins)),np.zeros(len(losses)))
        opponent_rating = wins_rating + losses_rating
        # print(f'{opponent_rating=}')
        opponent_rd = wins_rd + losses_rd
        results[player] = (opponent_rating, opponent_rd, outcomes)
        
    # update players
    for player in list(results.keys()):
        (rating_list, RD_list, outcome_list) = results[player]
        # print(f'{rating_list=}, {RD_list=}, {outcome_list=}')
        players_dict[player].update_player(rating_list, RD_list, outcome_list)

    return players_dict
    # opponent_indices = matches[matches['loser_id'].str==player '']


def epoch_3(matches, players_dict):
    '''Take in a dataframe with matches, a list of players, a dictionary of players with the elements
    of player list as keys and an instance of the glicko2 class Player() as the value.
    This function wll return the updated players_list and players_dict.
    
    Future iterations of this function should do away with the p_ , and only should need the 
    players_dict with the keys as integers indicating the player id.
    '''
    players_list = list(players_dict.keys())
    players = [p for p in np.append(matches['winner_id'].unique(),\
                                                matches['loser_id'].unique())]
    # instantiate player class for players not yet instantiated
    players_to_instantiate = list(set(players) - set(players_list))
    
    new_players = {player: Player() for player in players_to_instantiate}
    # print(type(new_players))

    # update list of instantiated players
    players_list = list(set(players).union(set(players_list)))
    # update dictionary of instantiated players
    players_dict.update(new_players)
    # print(type(players_dict))
    # determine who competed and who didn't
    players_dnc = list(set(players_list) - set(players))
    players_compete = list(set(players_list)-set(players_dnc))
    # print(f'{players_compete=}')
    # update attributes for players who didn't compete
    for player in players_dnc:
        players_dict[player].did_not_compete()
    # fill dictionary with (wins,losses), a tuple of list of opponents in wins and losses for each match
    results = {}
    for player in players_compete:
        wins = [winner for winner in matches[matches['winner_id']==player]['loser_id']]
        losses = [loser for loser in matches[matches['loser_id']== player]['winner_id']]
        # get opponents' rating and rd
        # print(f'{wins=}')
        losses_rating = [players_dict[loss].getRating() for loss in losses ]
        losses_rd = [players_dict[loss].getRd() for loss in losses ]
        wins_rating = [players_dict[win].getRating() for win in wins ]
        wins_rd = [players_dict[win].getRd() for win in wins ]
        outcomes = np.append(np.ones(len(wins)),np.zeros(len(losses)))
        opponent_rating = wins_rating + losses_rating
        # print(f'{opponent_rating=}')
        opponent_rd = wins_rd + losses_rd
        results[player] = (opponent_rating, opponent_rd, outcomes)
        
    # update players
    for player in list(results.keys()):
        (rating_list, RD_list, outcome_list) = results[player]
        # print(f'{rating_list=}, {RD_list=}, {outcome_list=}')
        players_dict[player].update_player(rating_list, RD_list, outcome_list)

    return players_dict
    # opponent_indices = matches[matches['loser_id'].str==player '']
    
def epoch_2(matches, players_list, players_dict):
    '''Take in a dataframe with matches, a list of players, a dictionary of players with the elements
    of player list as keys and an instance of the glicko2 class Player() as the value.
    This function wll return the updated players_list and players_dict.
    
    Future iterations of this function should do away with the p_ , and only should need the 
    players_dict with the keys as integers indicating the player id.
    '''
    
    players = [p for p in np.append(matches['winner_id'].unique(),\
                                                matches['loser_id'].unique())]
    # instantiate player class for players not yet instantiated
    players_to_instantiate = list(set(players) - set(players_list))
    new_players = {player: Player() for player in players_to_instantiate}
    # print(type(new_players))

    # update list of instantiated players
    players_list = list(set(players).union(set(players_list)))
    # update dictionary of instantiated players
    players_dict.update(new_players)
    # print(type(players_dict))
    # determine who competed and who didn't
    players_dnc = list(set(players_list) - set(players))
    players_compete = list(set(players_list)-set(players_dnc))
    # print(f'{players_compete=}')
    # update attributes for players who didn't compete
    for player in players_dnc:
        players_dict[player].did_not_compete()
    # fill dictionary with (wins,losses), a tuple of list of opponents in wins and losses for each match
    results = {}
    for player in players_compete:
        wins = [winner for winner in matches[matches['winner_id']==player]['loser_id']]
        losses = [loser for loser in matches[matches['loser_id']== player]['winner_id']]
        # get opponents' rating and rd
        # print(f'{wins=}')
        losses_rating = [players_dict[loss].getRating() for loss in losses ]
        losses_rd = [players_dict[loss].getRd() for loss in losses ]
        wins_rating = [players_dict[win].getRating() for win in wins ]
        wins_rd = [players_dict[win].getRd() for win in wins ]
        outcomes = np.append(np.ones(len(wins)),np.zeros(len(losses)))
        opponent_rating = wins_rating + losses_rating
        # print(f'{opponent_rating=}')
        opponent_rd = wins_rd + losses_rd
        results[player] = (opponent_rating, opponent_rd, outcomes)
        
    # update players
    for player in list(results.keys()):
        (rating_list, RD_list, outcome_list) = results[player]
        # print(f'{rating_list=}, {RD_list=}, {outcome_list=}')
        players_dict[player].update_player(rating_list, RD_list, outcome_list)

    return (players_list,players_dict)
    # opponent_indices = matches[matches['loser_id'].str==player '']
    
def cutDf(df,start,end,column):
    
    return df[(df[column]>=df[column][df[column].index[start]])&
              (df[column]<=df[column][df[column].index[end]])]

def epochs(match_history,interval_length = 365):
    '''Calculate the ending rating for each player with the lengh of each epoch being
    a funtion of the interval_length'''
    
    max_date = max(match_history['tourney_date']) # maximum date in the records
    min_date = min(match_history['tourney_date']) # minimum date in the records
    date_range = range(0,(max_date-min_date).days + 1,interval_length) # days from date of first
    # match in increments of the interval (default 365).  This is the length of each epoch. 
    players_list = []
    players_dict = {}
    
    epoch_cutoffs = [min_date + timedelta(days = x) for x in date_range]
    print(epoch_cutoffs)
    epoch_ranges = zip(epoch_cutoffs[0:-2],epoch_cutoffs[1:-1])
    
    
    # iteratively re-update for each epoch
    for period in epoch_ranges:
        rating_period = match_history[(match_history['tourney_date']>=period[0])&(match_history['tourney_date']<period[1])]
        if not rating_period.empty:
            (players_list,players_dict) = epoch(rating_period,players_list,players_dict)
        else:
            for player in players_list:
                players_dict[player].did_not_compete()
    # get the final, extended rating period updates.
    rating_period = match_history[match_history['tourney_date']>=epoch_cutoffs[-1]]
    (players_list,players_dict) = epoch(rating_period,players_list,players_dict)
    return (players_list,players_dict)