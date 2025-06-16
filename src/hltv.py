from util.scraper import *
from endpoints.matches import *

class HLTV:
    """
    This is what the user will instantiate and make all their calls through

    Outside of the input arguments to instantiate the class, the user should not know what happens inside this class
    """
    scraper: HLTVScraper
    
    def __init__(self, max_calls_per_second: int):
        self.scraper = HLTVScraper(max_calls_per_second)

    def get_upcoming_matches(self, skip_pending_team_matches: bool):
        return get_upcoming_matches(self.scraper, skip_pending_team_matches)
