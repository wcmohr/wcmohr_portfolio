# epoch is the most current version of the function and will be called
# in the main notebook.
import numpy as np  # numpy will be used for vectorized calculations.
import pandas as pd
import sys
sys.path.append('..')
from pyglicko2.glicko2 import Player
from datetime import datetime, timedelta

class PlayerElo:
    """Holds, sets, and updates elo ratings."""
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
        _k = self._k
        n = len(rating_list)
        # calculate expected wins
        expected_wins = np.sum(np.divide(1,(1 + np.power(10,(rating_list-self.__rating)/400))))
        actual_wins = np.sum(np.array(outcome_list))
        self.__rating = self.__rating + _k*(actual_wins - expected_wins)

def epochElo(matches, players_dict, cutoff_date):
    '''Take in a dataframe with matches, a list of players, a dictionary of players with the elements
    of player list as keys and an instance of the class PlayerElo() as the value.
    This function wll return the updated players_list and players_dict.
    '''
    players_list = list(players_dict.keys())
    players = [p for p in np.append(matches['winner_id'].unique(),\
                                                matches['loser_id'].unique())]
    # instantiate player class for players not yet instantiated
    players_to_instantiate = list(set(players) - set(players_list))
    
    new_players = {player: PlayerElo() for player in players_to_instantiate}
    # print(type(new_players))

    # update list of instantiated players
    players_list = list(set(players).union(set(players_list)))
    # update dictionary of instantiated players
    players_dict.update(new_players)
    # print(type(players_dict))
    # determine who competed and who didn't
    players_dnc = list(set(players_list) - set(players))
    players_compete = list(set(players_list)-set(players_dnc))
    
    # fill dictionary with player:(wins,losses), a tuple of list of opponents in wins and losses for each match
    results = {}
  
    for player in players_compete:
        wins = [winner for winner in matches[matches['winner_id']==player]['loser_id']]
        losses = [loser for loser in matches[matches['loser_id']== player]['winner_id']]
        losses_rating = [players_dict[loss].getRating() for loss in losses]
        wins_rating = [players_dict[win].getRating() for win in wins]
        outcomes = np.append(np.ones(len(wins)),np.zeros(len(losses)))
        opponent_rating = wins_rating + losses_rating
        results[player] = (opponent_rating, outcomes)
    ratings_timestamp = {}
    # update players
    for player in list(results.keys()):
        (rating_list, outcome_list) = results[player]
          # math range error, float division by zero workaround creates a timestamp without updating the player.
        try:
            players_dict[player].update_player(rating_list,outcome_list)
            ratings_timestamp[(player,cutoff_date)] = players_dict[player].getRating()
        except OverflowError:
            ratings_timestamp[(player,cutoff_date)] = players_dict[player].getRating()
        except ZeroDivisionError:
            ratings_timestamp[(player,cutoff_date)] = players_dict[player].getRating()
    return players_dict,ratings_timestamp

def epochsElo(match_history, interval_length = 365):
    '''Calculate the ending rating for each player with the lengh of each epoch being
    a funtion of the interval_length
    
    Next iterations: generate a rating history indicating the rating of each player each time that
    the rating updates.
    '''
    # check if the match_history is empty, as if it is the function call will not complete.
    if match_history.empty:
        return "Try again with a non-empty match history!"
    max_date = max(match_history['tourney_date']) # maximum date in the records
    min_date = min(match_history['tourney_date']) # minimum date in the records
    date_range = range(0,(max_date-min_date).days + 1,interval_length) # days from date of first
    # match in increments of the interval (default 365).  This is the length of each epoch. 
    epoch_cutoffs = [min_date + timedelta(days = x) for x in date_range] # The times that
    # divide the matches into each epoch.
    epoch_ranges = zip(epoch_cutoffs[0:-1],epoch_cutoffs[1:]) # each epoch will include matches
    # greater than or equal to the first element, less than the second element for the zip
    # generator's respective item.
    players_dict = {} # instantiate the dictionary that will hold a PlayerElo() class for each player.
    ratings_history = {}
    # iteratively re-update for each epoch
    for period in epoch_ranges:
        # rating_period is the df of matches that fall within an epoch
        rating_period = match_history[(match_history['tourney_date']>=period[0])&(match_history['tourney_date']<period[1])]
        # make sure the rating period isn't empty and then update the players.
        if not rating_period.empty:
            players_dict,ratings_timestamp = epochElo(rating_period,players_dict,period[1])
            ratings_history.update(ratings_timestamp)
    # get the final rating period updates (for matches in the final 365 to 729 days).
    rating_period = match_history[match_history['tourney_date']>=epoch_cutoffs[-1]]
    players_dict, ratings_timestamp = epochElo(rating_period,players_dict,max_date)
    ratings_history.update(ratings_timestamp)
    return players_dict,ratings_history

def epochG(matches, players_dict,cutoff_date):
    '''Take in a dataframe with matches, a list of players, a dictionary of players with the elements
    of player list as keys and an instance of the glicko2 class Player() as the value.
    This function wll return the updated players_list and players_dict.'''
    
    players_list = list(players_dict.keys())
    players = [p for p in np.append(matches['winner_id'].unique(),\
                                                matches['loser_id'].unique())]
    # instantiate player class for players not yet instantiated
    players_to_instantiate = list(set(players) - set(players_list))
    
    new_players = {player: Player() for player in players_to_instantiate}
    # print(type(new_players))
    players_list = list(set(players).union(set(players_list)))

    # update list of instantiated players
    # update dictionary of instantiated players
    players_dict.update(new_players)
    # determine who competed and who didn't
    players_dnc = list(set(players_list) - set(players))
    players_compete = players
    # print(f'{players_compete=}')
    # update rating deviation for players who didn't compete
    for player in players_dnc:
        players_dict[player].did_not_compete()
    # fill dictionary with (wins,losses), a tuple of list of opponents in wins and losses for each match
    results = {}
    # update players who did compete
    for player in players_compete:
        # get id of players they beat
        wins = [winner for winner in matches[matches['winner_id']==player]['loser_id']]
        # get id of players they lost to
        losses = [loser for loser in matches[matches['loser_id']== player]['winner_id']]
        # get opponents' rating and rd
        losses_rating = [players_dict[loss].getRating() for loss in losses]
        losses_rd = [players_dict[loss].getRd() for loss in losses]
        wins_rating = [players_dict[win].getRating() for win in wins]
        wins_rd = [players_dict[win].getRd() for win in wins]
        outcomes = np.append(np.ones(len(wins)),np.zeros(len(losses)))
        opponent_rating = wins_rating + losses_rating
        opponent_rd = wins_rd + losses_rd
        results[player] = (opponent_rating, opponent_rd, outcomes)
    
    ratings_timestamp = {}
    # update players, catch zerodivision, overflow errors in which case create timestamp with previous rating
    try:
        for player in list(results.keys()):
            (rating_list, RD_list, outcome_list) = results[player]
            players_dict[player].update_player(rating_list, RD_list, outcome_list)
            ratings_timestamp[(player,cutoff_date)] = (players_dict[player].getRating(), players_dict[player].getRd()) 
    except ZeroDivisionError: 
        ratings_timestamp[(player,cutoff_date)] = (players_dict[player].getRating(), players_dict[player].getRd())
        print('ZeroDivisionError')
        print(player)
        print(players_dict[player])
    except OverflowError: 
        ratings_timestamp[(player,cutoff_date)] = (players_dict[player].getRating(), players_dict[player].getRd()) 
        print('OverflowError')
        print(player)
        print(players_dict[player])
        
    return players_dict,ratings_timestamp

def epochsG(match_history, players_dict, interval_length = 365):
    '''Calculate the ending rating for each player with the lengh of each epoch being
    a funtion of the interval_length
    
    Next iterations: generate a rating history indicating the rating of each player each time that
    the rating updates.
    '''
    # check if the match_history is empty, as if it is the function call will not complete.
    if match_history.empty:
        return "Try again with a non-empty match history!"
    max_date = max(match_history['tourney_date']) # maximum date in the records
    min_date = min(match_history['tourney_date']) # minimum date in the records
    date_range = range(0,(max_date-min_date).days + 1,interval_length) # days from date of first
    # match in increments of the interval (default 365).  This is the length of each epoch. 
    epoch_cutoffs = [min_date + timedelta(days = x) for x in date_range] # The times that
    # divide the matches into each epoch.
    epoch_ranges = zip(epoch_cutoffs[0:-1],epoch_cutoffs[1:]) # each epoch will include matches
    # greater than or equal to the first element, less than the second element for the zip
    # generator's respective item.
    # print([r for r in epoch_ranges])
    ratings_history = {}

    # iteratively re-update for each epoch
    for period in epoch_ranges:
        # rating_ period is the df of matches that fall within a given epoch
        rating_period = match_history[(match_history['tourney_date']>=period[0])&
                                      (match_history['tourney_date']<period[1])]
        # If the rating period is empty, then adjust the rating deviation of the players.
        if not rating_period.empty:
            players_dict,ratings_timestamp = epochG(rating_period,players_dict,period[1])
            ratings_history.update(ratings_timestamp)
        else:
            for player in players_dict:
                players_dict[player].did_not_compete()
    # get the final rating period updates (for matches in the final 365 to 729 days).
    rating_period = match_history[match_history['tourney_date']>=epoch_cutoffs[-1]]
    players_dict,ratings_timestamp = epochG(rating_period,players_dict,max_date)
    ratings_history.update(ratings_timestamp)
    return players_dict, ratings_history


# Glicko-2 probability calculation inspired by [chess_in_sgv](https://www.reddit.com/r/chess/comments/i0pnv1/glicko2_win_probability/) but scrapped in favor of the direct adaptation from E in step 3 of [glicko 2 example](https://www.glicko.net/glicko/glicko2.pdf) by Mark Glickman.

def winProbG(r1, rd1, r2, rd2):
    """Calculate the probability that player 1 defeats 
    player 2 based on Glicko2 rating and rating deviations"""
    r1 = (r1 - 1500)/173.7178
    r2 = (r2 - 1500)/173.7178
    rd1 = rd1/173.7178
    rd2 = rd2/173.7178
    rds = (rd1**2 + rd2**2)**.5
    g_phi = 1 / (1 + 3 * (rds**2) / math.pi**2)
    # x = (rd1**2 + rd2**2)
    # A = 1 / (1 + 3 * (x**2) / math.pi**2) * (r1-r2)
    E1 = 1/(1+math.e ** (-g_phi*(r1-r2)))
    return E1

def assembleDf(ratingHistory):
    '''Generate a DataFrame from the ratingHistory dictionary.
    The cuttoff dates for each rating period is the rows and 
    the player ids are the columns with the values being the
    ratings.'''
    
    keys = [key for key in ratingHistory.keys()] # convert to iterable
    # vals = np.array([ratingHistory[key] for key in keys]) # get corresponding vals
    cols_players = [key[0] for key in keys] # 
    rows_times = [key[1] for key in keys]
    df = pd.DataFrame( columns = list(set(cols_players)))
    for key in ratingHistory.keys():
        r,c = key[1],key[0]
        df.loc[r,c] = ratingHistory[key]
    return df

def get_recent_rating_wp(ratingsHistory_df,tourney_date,winner_id,loser_id):
    """Takes in a DataFrame of ratings history, tournament date, winner id and loser id
    and returns the winner's and loser's Elo rating as well as the win probability."""
    
    if not type(tourney_date) == pd._libs.tslibs.timestamps.Timestamp:
        tourney_date = pd.to_datetime(tourney_date)
    timestamp = max(ratingsHistory_df.index[ratingsHistory_df.index<=tourney_date])
    winner_rating, loser_rating = ratingsHistory_df.loc[timestamp,[winner_id,loser_id]]
    wp = 1/(1 + 10**((loser_rating-winner_rating)/400))
    return winner_rating, loser_rating, wp

def get_recent_rating_rd_wp(tourney_date, winner_id, loser_id, **kwargs):
    """Return the most recent ratings and rating deviations for the competitors as
        well as the a priori win probability for the eventual winner according to 
        the Glicko-2 rating system. **kwargs : ratingsHistory_df,rdHistory_df"""
    ratingsHistory_df = kwargs['ratingsHistory_df']
    rdHistory_df = kwargs['rdHistory_df']
    try:
        if not type(tourney_date) == pd._libs.tslibs.timestamps.Timestamp:
            tourney_date = pd.to_datetime(tourney_date)
        # for robustness, assuming that rd and ratings may have different timestamps
        timestamp_rh = max(ratingsHistory_df.index[ratingsHistory_df.index<=tourney_date])
        timestamp_rd = max(rdHistory_df.index[rdHistory_df.index<=tourney_date])
        winner_rating, loser_rating = ratingsHistory_df.loc[timestamp_rh,[winner_id,loser_id]]
        winner_rd, loser_rd = rdHistory_df.loc[timestamp_rd,[winner_id,loser_id]]
        wp = winProbG(winner_rating, winner_rd, loser_rating, loser_rd)
        return winner_rating, winner_rd, loser_rating, loser_rd, wp
    except KeyError:
        return np.nan, np.nan, np.nan, np.nan,np.nan