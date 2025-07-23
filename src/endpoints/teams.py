from classes.team import Team
from enums.maps import Maps
from enums.match_types import MatchType
from util.global_cache import *
from util.scraper import *
from util.url_util import *
from datetime import datetime, timedelta
import re

# THERE IS ALSO A DIFFERENT PAGE FOR GETTING TEAMS AT A SPECIFIC POINT IN TIME
# IT HAS A DIFFERENT STRUCTURE FROM THE GENERAL PAGE ABOUT A TEAM, MAY NEED TO SETUP A DIFFERENT SCRAPE FOR THAT TOO
# STRUCTURE FOR THIS: https://www.hltv.org/stats/teams/9565/vitality?startDate=2025-04-13&endDate=2025-07-13
# BASICALLY https://www.hltv.org/stats/teams/9565/vitality AND THEN THE SAME LOGIC FOR ADDING THIS ON IN list_top_teams


def get_team(scraper: HLTVScraper, id: int, team_name: str = None) -> Team:
    """
    Returns info for the given team ID.
    This just returns current general information about the team, not specific to an interval of time.
    
    Returned Team class will have the following fields:
    """
    cached_team = global_cache.get(CacheType.TEAMS, id)
    if cached_team:
        return cached_team

    # The team name doesn't matter, it's just for logging purposes. Only the ID matters
    url = f"{scraper.default_url}/team/{id}/{team_name if team_name else "random"}"

    buttons = [scraper.cookie_text]
    soup = scraper.get_website(url, buttons)

    team_profile = soup.find("div", class_="teamProfile")

    # Getting all the players
    bodyshot_team_div = team_profile.find("div", class_="bodyshot-team g-grid")
    player_anchors = bodyshot_team_div.find_all("a", class_="col-custom")
    players = {}
    for player_anchor in player_anchors:
        player_name = player_anchor['title']
        player_id = int(re.search(r"/player/(\d+)/", player_anchor['href']).group(1))
        players[player_name] = player_id

    # Profile Top Box
    profile_top_box_div = team_profile.find("div", class_="standard-box profileTopBox clearfix")
    
    profile_team_container_div = profile_top_box_div.find("div", class_="profile-team-container text-ellipsis")
    profile_team_info_div = profile_team_container_div.find("div", class_="profile-team-info")
    region = profile_team_info_div.find("div", class_="team-country text-ellipsis").get_text(strip=True)
    name = profile_team_info_div.find("h1", class_="profile-team-name text-ellipsis").get_text(strip=True)

    profile_team_stats_container_div = profile_top_box_div.find("div", class_="profile-team-stats-container")
    valve_rank = -1
    world_rank = -1
    for stat_div in profile_team_stats_container_div.find("div", class_="profile-team-stat-50-50").find_all("div", class_="profile-team-stat"):
        rank_text = int(stat_div.select_one('.right a').get_text(strip=True)[1:]) # Converts '#1' to 1(int)
        label = stat_div.find('b').get_text(strip=True)
        if label == 'Valve ranking':
            valve_rank = rank_text
        elif label == 'World ranking':
            world_rank = rank_text
    coach_anchor = profile_team_stats_container_div.find("a", class_="a-reset right")
    coach_id = int(coach_anchor["href"].split("/")[2])
    coach_name = coach_anchor.find("span").get_text(strip=True).strip("'")
    coach = {coach_name: coach_id}

    team = Team(
        id=id,
        name=name,
        region=region,
        valve_rank=valve_rank,
        world_rank=world_rank,
        players=players,
        coach=coach
    )

    # Adding the team info to the cache before returning
    global_cache.set(CacheType.TEAMS, id, team)

    return team


def list_top_teams(
        scraper: HLTVScraper,
        start_date: datetime,
        end_date: datetime,
        match_type: MatchType = None,
        maps: list[Maps] = None,
        num_results: int = None
    ) -> list[Team]:
    """
    Retrieves the top teams from HLTV in the specified [start_date, end_date] timeframe.
    The match_type argument specifies the type of match to filter for
    The maps argument specifies the list of maps to filter for games on
    The num_results argument specifies the number of top teams to fetch for
     
    The returned value is a list of Team classes, ordered by team rank, each with the following fields:

    General fields(description in the class):
    id
    name
    region

    Time-specific fields:
    rank: The rank of the team
    num_maps_played: The number of maps played by the team in the specified timeframe
    kd_diff: The K-D diff by the team in the specified timeframe
    kd_ratio: The K-D ratio by the team in the specified timeframe
    rating: The HLTV 2.1 rating of the team in the specified timeframe
    """
    if start_date > end_date - timedelta(weeks=1):
        raise Exception(f"Input start date {start_date} must be at least one week before the end date {end_date}")
    possible_num_results = [5, 10, 20, 30, 50]
    if num_results and num_results not in possible_num_results:
        raise Exception(f"The number of top teams to get must be one of {possible_num_results}")

    url = f"{scraper.default_url}/stats/teams?"
    url += URLUtil.get_end_of_url(start_date, end_date, match_type, maps)
    if num_results: # When num_results is null, we give all results back to user, which is done by not specifying any arguments in the url
        url += f"&rankingFilter=Top{num_results}"

    buttons = [scraper.cookie_text]
    soup = scraper.get_website(url, buttons)

    # Finding the main table, header, and body
    table = soup.find("table", class_="stats-table player-ratings-table")
    header = table.find("thead")
    body = table.find("tbody")

    # Verify that the table's header is still in the expected format
    expected_headers = [
        "teamCol-teams-overview",
        "mapsCol-teams-overview",
        "kdDiffCol-teams-overview",
        "kdCol-teams-overview",
        "ratingCol-teams-overview"
    ]
    header_row = header.find_all("tr")[0]
    headers = header_row.find_all("th")
    for idx in range(len(headers)):
        header = headers[idx].get('class', [None])[0]
        expected_header = expected_headers[idx]
        if header != expected_header:
            raise Exception(f"Retrieved headers {header} is not what's expected in {expected_header}, scraping might not work for this new format")

    # Each of the team info is stored in a row, ordered by team rank
    interval_string = CacheManager.datetime_interval_to_string(start_date, end_date) # String representing the time interval we're scraping this data for
    teams = [] # The result
    rows = body.find_all("tr")
    for idx in range(len(rows)):
        row = rows[idx]
        cells = row.find_all("td")
        # Example cells:
        # <td class="teamCol-teams-overview">
        #   <img alt="Europe" class="flag" src="/img/static/flags/30x20/EU.gif" title="Europe"/>
        #   <a data-tooltip-id="uniqueTooltipId--768131681" href="/stats/teams/9565/vitality?startDate=2025-04-09&amp;endDate=2025-07-09&amp;rankingFilter=Top20">
        #     Vitality
        #   </a>
        # </td>
        # <td class="statsDetail">
        #   46
        # </td>
        # <td class="kdDiffCol won">
        #   +424
        # </td>
        # <td class="statsDetail">
        #   1.14
        # </td>
        # <td class="ratingCol ratingPositive">
        #   1.14
        # </td>

        # Stats we scraped
        id = int(re.search(r'/stats/teams/(\d+)/', cells[0].find('a').get('href')).group(1)) # Using RegEx to parse the href for the team's id
        new_team = Team(
            id=id,
            name=cells[0].find('a').get_text(strip=True),
            region=cells[0].find('img')['title'],
            time_specific_data={
                interval_string: {
                    "rank": idx + 1,
                    "num_maps_played": cells[1].get_text(strip=True),
                    "kd_diff": cells[2].get_text(strip=True),
                    "kd_ratio": cells[3].get_text(strip=True),
                    "rating": cells[3].get_text(strip=True)
                }
            }
        )

        # Adds the item into the cache or merges it into the existing cache item if one exists
        cached_team = global_cache.get(CacheType.TEAMS, id)
        if cached_team is not None:
            CacheManager.merge_dataclasses(cached_team, new_team)
            teams.append(cached_team)
        else:
            global_cache.set(CacheType.TEAMS, id, new_team)
            teams.append(new_team)

    return teams
