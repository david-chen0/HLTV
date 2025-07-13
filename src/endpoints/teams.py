from enums.maps import Maps
from enums.match_types import MatchType
from util.scraper import *
from datetime import datetime, timedelta

# def get_team(scraper: HLTVScraper, team_name: str, time: datetime) -> dict:
#     """
#     Returns info for the given team name at the specified point in time. Returned dict will have the following fields:

    
#     """
#     return


def list_top_teams(
        scraper: HLTVScraper,
        start_date: datetime,
        end_date: datetime,
        match_type: MatchType = None,
        maps: Maps = None,
        num_results: int = None
    ) -> list:
    """
    Retrieves the top teams from HLTV in the specified [start_date, end_date] timeframe.
    The match_type argument specifies the type of match to filter for
    The maps argument specifies the maps to filter for games on
    The num_results argument specifies the number of top teams to fetch for
     
    The returned value is a list of dicts, ordered by team rank, each with the following fields:

    rank: The rank of the team
    name: The name of the team
    region: The country/region the team is based in(ex: Russia, Europe, Brazil, Other, etc)
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

    # Ex link with all arguments: https://www.hltv.org/stats/teams?startDate=2025-04-09&endDate=2025-07-09&matchType=Majors&maps=de_dust2&rankingFilter=Top20
    url = f"{scraper.default_url}/stats/teams?startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}"
    if match_type: # When match_type is null, we make the query for all match types, which is done by not specifying any arguments in the url
        url += f"&matchType={match_type.value}"
    if maps: # When maps is null, we make the query for all maps, which is done by not specifying any arguments in the url
        url += f"&maps={maps.value}"
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

        teams.append({
            "rank": idx + 1,
            "name": cells[0].find('a').get_text(strip=True),
            "region": cells[0].find('img')['title'],
            "num_maps_played": cells[1].get_text(strip=True),
            "kd_diff": cells[2].get_text(strip=True),
            "kd_ratio": cells[3].get_text(strip=True),
            "rating": cells[3].get_text(strip=True)
        })

    print(teams)

    return teams
