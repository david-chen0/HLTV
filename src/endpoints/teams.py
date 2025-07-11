from util.scraper import *
from datetime import datetime

# def get_team(scraper: HLTVScraper, team_name: str, time: datetime) -> dict:
#     """
#     Returns info for the given team name at the specified point in time. Returned dict will have the following fields:

    
#     """
#     return

# todos:
# make the logic common and then make a separate function for all time, which is just the same url but with startDate=all and no endDate
# add a parameter to change the number of results, currently set to 20
def get_top_teams(scraper: HLTVScraper, start_date: datetime, end_date: datetime) -> dict:
    """
    Returns the top 20 teams in the given period
    """
    # ex link: https://www.hltv.org/stats/teams?startDate=2025-04-09&endDate=2025-07-09&rankingFilter=Top20
