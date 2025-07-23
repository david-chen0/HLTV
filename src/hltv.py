from classes.match import Match
from classes.player import Player
from classes.team import Team
from endpoints.matches import *
from endpoints.players import *
from endpoints.teams import *
from enums.maps import Maps
from enums.match_types import MatchType
from util.scraper import *
from datetime import datetime

class HLTV:
    """
    This is what the user will instantiate and make all their calls through

    Outside of the input arguments to instantiate the class, the user should not know what happens inside this class
    """
    scraper: HLTVScraper
    
    def __init__(self, max_calls_per_second: int):
        self.scraper = HLTVScraper(max_calls_per_second)

    # Match APIs
    def get_upcoming_matches(self, skip_pending_team_matches: bool) -> list[Match]:
        return get_upcoming_matches(self.scraper, skip_pending_team_matches)
    
    # Player APIs
    def get_player(
            self,
            id: int,
            player_name: str = None
    ) -> Player:
        return get_player(self.scraper, id, player_name)
    
    # Team APIs
    def get_team(
        self,
        id: int,
        team_name: str = None
    ) -> Team:
        return get_team(self.scraper, id, team_name)

    def list_top_teams(
        self,
        start_date: datetime,
        end_date: datetime,
        match_type: MatchType = None,
        maps: list[Maps] = None,
        num_results: int = None
    ) -> list[Team]:
        return list_top_teams(
            self.scraper,
            start_date,
            end_date,
            match_type,
            maps,
            num_results
        )
