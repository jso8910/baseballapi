from typing import Any, Union
from getcumulativestats import getProbabilityOfString, getLeverageOfString
import statsapi
import datetime
import pytz

# TODO: use `.get(param)` to prevent errors and just return None

class Game:
    """A class! DO NOT INSTANTIATE OUTSIDE OF THE FUNCTIONS IN THIS FILE BECAUSE IT DOESN'T HAVE VERIFICATION OF PARAMETERS 
    """    
    def __init__(self, game_id, timecode=None):        
        self.game_id = game_id
        self.timecode = timecode
        self.game_obj = statsapi.get('game', {'gamePk': game_id, 'timecode': timecode})
        self.url = self.game_obj['link']

    def refresh(self):
        """Refresh the game_obj with more recent data
        """        
        self.game_obj = statsapi.get('game', {'gamePk': self.game_id, 'timecode': self.timecode})

    def __get_runners(self) -> dict[bool]:
        """Tells the runners on base

        Returns:
            Dict[bool]: {'first': bool, 'second': bool, 'third': bool}
        """        
        runners = self.game_obj['liveData']['linescore']['offense']
        bases = {'first': False, 'second': False, 'third': False}
        for base in bases:
            if base in runners:
                bases[base] = True
        
        return bases

    def __get_score(self) -> dict[int]:
        """Gets the score for each team

        Returns:
            Dict[int]: {'home': int, 'away': int}
        """        
        homeTeam = self.game_obj['liveData']['linescore']['teams']['home']
        awayTeam = self.game_obj['liveData']['linescore']['teams']['away']

        return {'home': homeTeam['runs'], 'away': awayTeam['runs']}

    def __get_current_inning(self) -> int:
        """Gets the current inning number

        Returns:
            int
        """        
        return self.game_obj['liveData']['linescore']['currentInning']
    
    def __get_current_inning_half(self) -> str:
        """Gets the current half of the inning

        Returns:
            str: 'top' or 'bottom'
        """        
        return self.game_obj['liveData']['linescore']['inningHalf'].lower()
    
    def __get_inning_ordinal(self) -> str:
        """The ordinal (eg 1st, 2nd, 3rd) of the current inning

        Returns:
            str: Read the summary :)
        """        
        return self.game_obj['liveData']['linescore']['currentInningOrdinal']
    
    def __get_scheduled_innings(self) -> int:
        """Number of innings that are scheduled to occur —

        Returns:
            int: Normally 7 or 9
        """        
        return self.game_obj['liveData']['linescore']['scheduledInnings']

    def __get_inning_objs(self) -> list[dict[Any]]:
        """The objects of the innings

        Returns:
            List[Dict[Any]]: A list of all the inning dicts
        """        
        return self.game_obj['liveData']['linescore']['innings']

    def __get_innings_runs(self) -> dict[list[Union[str, None]]]:
        """A dict with the runs per team per inning. If a value is None, that means that inning hasn't been played yet

        Returns:
            Dict[List[Any]]: {'home': [0, 0, 0, 0, 0, None, None], 'away': [0, 2, 0, 0, 0, 8, None]}
        """        
        scheduled_innings = self.__get_scheduled_innings()

        innings_runs = {'home': [None] * scheduled_innings, 'away': [None] * scheduled_innings}
        innings = self.game_obj['liveData']['linescore']['innings']

        if len(innings) == 0:
            return innings_runs
        
        for i in range(len(innings)):
            if 'runs' not in innings[i]['home'] and i < len(innings_runs['home']):
                innings_runs['home'][i] = None
            elif 'runs' not in innings[i]['home'] and i > len(innings_runs['home']):
                innings_runs['home'].append(None)
            elif i < len(innings_runs['home']):
                innings_runs['home'][i] = innings[i]['home']['runs']
            else:
                innings_runs['home'].append(innings[i]['home']['runs'])

            if 'runs' not in innings[i]['away'] and i < len(innings_runs['away']):
                innings_runs['away'][i] = None
            elif 'runs' not in innings[i]['away'] and i > len(innings_runs['away']):
                innings_runs['away'].append(None)
            elif i < len(innings_runs['away']):
                innings_runs['away'][i] = innings[i]['away']['runs']
            else:
                innings_runs['away'].append(innings[i]['away']['runs'])
        
        return innings_runs
    
    def __get_balls_strikes_outs(self) -> dict[int]:
        """Returns balls, strikes, and outs for the game

        Returns:
            Dict[Int]: {'balls': int, 'strikes': int, 'outs': int}
        """ 
        return {'balls': self.game_obj['liveData']['linescore']['balls'], 
                'strikes': self.game_obj['liveData']['linescore']['strikes'], 
                'outs': self.game_obj['liveData']['linescore']['outs']}
    
    def __get_boxscore_info(self) -> list[dict[Any]]:
        """Returns info for the boxscore

        Returns:
            List[Dict[Any]]: Has a list of dicts with `label` and `value`
        """        
        return self.game_obj['liveData']['boxscore']['info']
    
    def __get_pitching_notes(self) -> list[str]:
        """Pitching notes

        Returns:
            List[str]: A list of pitching notes
        """        
        return self.game_obj['liveData']['boxscore']['pitchingNotes']

    def __get_officials(self) -> list[dict[Any]]:
        """Gets officials (umps)

        Returns:
            List[dict[Any]]: A list of umpire dicts
        """        
        return self.game_obj['liveData']['boxscore']['officials']
            
    def __get_teams(self) -> dict[dict[Any]]:
        """Information about the teams

        Returns:
            Dict[Dict[any]]: {'home': Dict, 'away': Dict}
        """        
        return {'home': self.game_obj['liveData']['boxscore']['teams']['home']['team'], 'away': self.game_obj['liveData']['boxscore']['teams']['away']['team']}
    
    def __get_all_plays(self) -> list[dict[Any]]:
        """All the plays in the game

        Returns:
            List[Dict[Any]]: A list of play dicts
        """        
        return self.game_obj['liveData']['plays']['allPlays']
    
    def __get_current_play(self) -> dict[Any]:
        """The play that just happened

        Returns:
            Dict[Any]: Self explanatory
        """        
        return self.game_obj['liveData']['plays']['currentPlay']
    
    def __get_inning_plays(self) -> list[dict[Any]]:
        """The plays this inning

        Returns:
            List[Dict]: A list of play dicts from this inning
        """        
        return self.game_obj['liveData']['plays']['playsByInning']
    
    def __get_scoring_plays(self) -> list[dict[Any]]:
        """Scoring plays this game

        Returns:
            List[Dict]: A list of play dicts that ended in someone scoring
        """        
        return self.game_obj['liveData']['plays']['scoringPlays']
    
    def __get_weather(self) -> dict[Any]:
        """The weather!

        Returns:
            Dict[Any]: A dict with the weather (`condition`, `temp`, `wind`)
        """        
        return self.game_obj['gameData']['weather']
    
    def __get_venue(self) -> dict[Any]:
        """The venue the game is in

        Returns:
            Dict[Any]: Stuff like an id, url to get more information, name, and more
        """        
        return self.game_obj['gameData']['venue']
    
    def __get_players(self) -> dict[dict[Any]]:
        """All the players on the roster of the teams

        Returns:
            Dict[Dict[Any]]: key is id, value is player info
        """        
        return self.game_obj['gameData']['players']
    
    def __get_status(self) -> dict[Any]:
        """The status of the game

        Returns:
            Dict[Any]: Information about the status of the game
        """        
        return self.game_obj['gameData']['status']
    
    def __get_gamething(self) -> dict[Any]:
        """I don't know why this is seperate from gameInfo, but it is. Some stuff about the game

        Returns:
            Dict[Any]: Game info dict
        """        
        return self.game_obj['gameData']['game']
    
    def __get_gameinfo(self) -> dict[Any]:
        """gameInfo such as attendance and duration

        Returns:
            Dict[Any]: A dict
        """        
        return self.game_obj['gameData']['gameInfo']
    
    def __get_flags(self) -> dict[bool]:
        """Is it a no hitter? Is it a perfect game?

        Returns:
            Dict[bool]: Summary says it all
        """        
        return self.game_obj['gameData']['gameInfo']
    
    def __get_alerts(self):
        """Some alerts about the game — don't know what goes here, probably posteponement???

        Returns:
            List[Dict?]: Who knows
        """        
        return self.game_obj['gameData']['alerts']
    
    def __get_probable_pitchers(self) -> dict[dict[Any]]:
        """Who's gonna pitch

        Returns:
            Dict[Dict[Any]]: Two keys (away and home) with the name, id, and url of the pitcher
        """        
        return self.game_obj['gameData']['probablePitchers']
    
    def __game_is_started(self) -> bool:
        """Has the game started (it will return true even if finished)

        Returns:
            bool: True or False
        """        
        # May be more
        return not self.game_obj['gameData']['status']['statusCode'] in ['S', 'P']
    
    def __game_is_finished(self) -> bool:
        """Has the game been finished?

        Returns:
            bool: True or False
        """        
        return self.game_obj['gameData']['status']['statusCode'] in ['F', 'O']
    
    def __get_linescore(self) -> dict[Any]:
        """The linescore dict

        Returns:
            dict[Any]: The linescore dict from game_obj
        """        
        return self.game_obj['liveData']['linescore']
    
    def create_good_json(self) -> dict[Any]:
        """A better json for anyone to use (I made this so I understand the structure)

        Returns:
            Dict[Any]: If you want more info just read the source — pretty self explanatory
        """        
        json = {
            'gameData': {
                'game': self.__get_gamething(),
                'gameInfo': self.__get_gameinfo(),
                'status': self.__get_status(),
                'weather': self.__get_weather(),
                'venue': self.__get_venue(),
                'flags': self.__get_flags(),
                'alerts': self.__get_alerts(),
                'probablePitchers': self.__get_probable_pitchers(),
                'players': self.__get_players(),
                'started': self.__game_is_started(),
                'finished': self.__game_is_finished()
            },
            'currentData': {
                'plays': {
                    'allPlays': self.__get_all_plays(),
                    'currentPlay': self.__get_current_play() if self.__game_is_started() else None,
                    'playsThisInning': self.__get_inning_plays(),
                    'playsByInning': self.__get_inning_plays(),
                    'scoringPlays': self.__get_scoring_plays()
                },
                'score': self.__get_score() if self.__game_is_started() else None,
                'info': self.__get_boxscore_info(),
                'scheduledInnings': self.__get_scheduled_innings(),
                'currentInning': self.__get_current_inning() if self.__game_is_started() else None,
                'inningHalf': self.__get_current_inning_half() if self.__game_is_started() else None,
                'inningOrdinal': self.__get_inning_ordinal() if self.__game_is_started() else None,
                'inningsObjs': self.__get_inning_objs(),
                'runsPerInning': self.__get_innings_runs(),
                'teams': self.__get_teams(),
                'officials': self.__get_officials(),
                'pitchingNotes': self.__get_pitching_notes(),
                'balls': self.__get_balls_strikes_outs()['balls'] if self.__game_is_started() else None,
                'strikes': self.__get_balls_strikes_outs()['strikes'] if self.__game_is_started() else None,
                'outs': self.__get_balls_strikes_outs()['outs'] if self.__game_is_started() else None,
                'runners': self.__get_runners() if self.__game_is_started() else None
            }
        }
        
        return json
    
    def score_json(self):
        """Uses the internal function __get_linescore and gives you the return value of it

        Returns:
            Dict: Yeah
        """        
        return self.__get_linescore()

    def get_probability(self):



        betterjson = self.create_good_json()

        if not self.__game_is_started():
            return {'message': 'Game has not started'}
        elif self.__game_is_finished():
            return {'message': 'Game is finished'}

        # Team represents which half of the inning
        team = 'H' if betterjson['currentData']['inningHalf'] == 'Top' else 'V'
        inning = betterjson['currentData']['currentInning']
        outs = betterjson['currentData']['outs']
        runners = 1
        bases = betterjson['currentData']['runners']
        balls = betterjson['currentData']['balls']
        strikes = betterjson['currentData']['strikes']

        if bases['first']:
            runners += 1
        
        if bases['second']:
            runners += 2
        
        if bases['third']:
            runners += 4
        
        homeScore = int(betterjson['currentData']['score']['home'])
        awayScore = int(betterjson['currentData']['score']['away'])

        if team == 'H':
            scorediff = homeScore - awayScore
        else:
            scorediff = awayScore - homeScore
        
        if outs == 3:
            outs = 2
        
        if strikes == 3:
            strikes = 2
        
        if balls == 4:
            balls = 3
        
        stateString = f'"{team}",{inning},{outs},{runners},{scorediff}'
        ballsStrikes = f'{balls},{strikes}'

        startYear = 1957
        endYear = 2020

        
        (wins, total) = getProbabilityOfString(stateString + "," + ballsStrikes, int(startYear), int(endYear))
        leverage = getLeverageOfString(stateString)
        return {"wins": wins, "total": total, "leverage": leverage} 


def get_day_ids(date: datetime.datetime) -> list:
    return [obj['game_id'] for obj in statsapi.schedule(date=date.strftime('%m/%d/%Y'))]

def today_ids() -> list:
    eastern = pytz.timezone('US/Eastern')
    date = datetime.datetime.now(eastern)

    # If it is earlier than 8 then no games will have started so yesterdays game
    if date.hour < 8:
        date -= datetime.timedelta(days=1)

    return get_day_ids(date)

from concurrent.futures import ProcessPoolExecutor as PoolExecutor

def today_objs() -> list[Game]:
    eastern = pytz.timezone('US/Eastern')
    date = datetime.datetime.now(eastern)
    # If it is earlier than 8 then no games will have started so yesterdays game
    if date.hour < 8:
        date -= datetime.timedelta(days=1)

    ids_for_day = get_day_ids(date) 

    with PoolExecutor(max_workers=16) as executor:
        return list(executor.map(game, ids_for_day))
 
def day_objs(date: str) -> list[Game]: # Format: MM/DD/YYYY
    ids_for_day = get_day_ids(date) 
    with PoolExecutor(max_workers=16) as executor:
        return list(executor.map(game, ids_for_day))

def game(game_id, timecode=None):
    game = Game(game_id, timecode)
    return game