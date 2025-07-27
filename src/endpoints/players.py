from classes.player import Player
from enums.maps import Maps
from enums.match_types import MatchType
from util.global_cache import *
from util.scraper import *
from util.url_util import *
import re

def get_player(scraper: HLTVScraper, id: int, player_name: str = None) -> Player:
    """
    Returns info for the given player ID.
    This just returns current general information about the player, not specific to an interval of time.
    """
    # This method only fetches the bare minimum info about the players, so we can short circuit if we find the player in the cache
    cached_player = global_cache.get(CacheType.PLAYERS, id)
    if cached_player:
        return cached_player

    # The player name doesn't matter, it's just for logging purposes. Only the ID matters
    url = f"{scraper.default_url}/player/{id}/{player_name if player_name else "random"}"

    buttons = [scraper.cookie_text]
    soup = scraper.get_website(url, buttons)

    # High level divs
    player_profile_div = soup.find("div", class_="playerProfile")
    player_info_wrapper_div = player_profile_div.find("div", class_="playerInfoWrapper")

    # Player name info
    player_name_div = player_info_wrapper_div.find("div", class_="playerName")
    name = soup.find("h1", class_="playerNickname").get_text(strip=True)
    real_name_div = player_name_div.find("div", class_="playerRealname")
    real_name = real_name_div.get_text(strip=True)
    nationality = real_name_div.find('img')['title']

    # Player general info
    player_info_div = player_info_wrapper_div.find("div", class_="playerInfo")
    age = re.search(r'\d+', player_info_div.find('span', itemprop='text').get_text(strip=True)).group()

    # Player team info
    player_team_info_div = player_info_div.find('div', class_='playerInfoRow playerTeam')
    team_anchor = player_team_info_div.find("span", itemprop="text").find("a")
    team_id = re.search(r'/team/(\d+)/', team_anchor['href']).group(1)
    team_name = team_anchor.get_text(strip=True)

    # Player top20 info
    top20_placements = {}
    top20_div = player_info_wrapper_div.find("div", class_="playerInfoRow playerTop20 top-grid-box")
    if top20_div: # Only players with a top20 HLTV placement will have this
        year_spans = top20_div.find_all("span", class_="top-20-year")
        rank_anchors = top20_div.find_all("a")
        top20_placements = {}
        for anchor, year_span in zip(rank_anchors, year_spans):
            year_short = year_span.get_text(strip=True)  # e.g. "('19)"
            year = "20" + year_short.strip("(')")  # Convert ('19) -> "2019"
            placement = int(anchor.get_text(strip=True).lstrip('#'))
            top20_placements[year] = placement

    # Team Box
    team_box_div = player_profile_div.find("div", class_="tab-content hidden", id="teamsBox")
    time_with_team: int
    time_with_any_team: int
    for stat_block in team_box_div.find_all("div", class_="highlighted-stat"):
        description = stat_block.find("div", class_="description")
        if not description:
            continue
        
        description_text = description.get_text(strip=True)
        stat_value = int(stat_block.find("div", class_="stat").get_text(strip=True).replace(',', ''))
        if description_text == "Days in current team":
            time_with_team = stat_value
        elif description_text == "Days in teams":
            time_with_any_team = stat_value

    # Achievement Box
    achievement_box_div = player_profile_div.find("div", class_="tab-content hidden", id="achievementBox")

    # Helper method to get highlighted stats
    def get_highlighted_stats(total_div, plural_form: str, singular_form: str) -> dict:
        # Plural form(ex: "Majors") is used to get rid of plural form to normalize the text(in case player only has singular)
        highlighted_stats_box_div = total_div.find("div", class_="highlighted-stats-box")
        highlighted_stats_divs = highlighted_stats_box_div.find_all("div", class_="highlighted-stat")
        result = {}
        for highlighted_stats_div in highlighted_stats_divs:
            stat_description = highlighted_stats_div.find("div", class_="description").get_text(strip=True)
            if plural_form in stat_description:
                stat_description = stat_description.replace(plural_form, singular_form)

            stat_value = highlighted_stats_div.find('div', class_='stat').get_text(strip=True)
            result[stat_description] = stat_value
        return result

    major_achievement_div = achievement_box_div.find("div", class_="sub-tab-content", id="majorAchievement")
    majors_won = 0
    majors_played = 0
    if major_achievement_div:
        stats = get_highlighted_stats(major_achievement_div, "Majors", "Major")
        majors_won = stats["Major won"]
        majors_played = stats["Major played"]
                
    lan_achievement_div = achievement_box_div.find("div", class_="sub-tab-content", id="lanAchievement")
    lans_won = 0
    lans_played = 0
    if lan_achievement_div:
        stats = get_highlighted_stats(lan_achievement_div, "LANs", "LAN")
        lans_won = stats["LAN won"]
        lans_played = stats["LAN played"]


    # Trophies Box
    trophy_box_div = player_profile_div.find("div", class_="tab-content hidden", id="trophiesBox")

    mvps_achievement_div = trophy_box_div.find("div", class_="sub-tab-content-trophies mvp-section hidden", id="MVPs")
    major_mvps = 0
    total_mvps = 0
    if mvps_achievement_div:
        stats = get_highlighted_stats(mvps_achievement_div, "MVPs", "MVP")
        major_mvps = stats["Major MVP"]
        total_mvps = stats["Total MVP"]

    # Player achievements
    achievements = {
        "top20_placements" : top20_placements,
        "majors_won": majors_won,
        "majors_played": majors_played,
        "lans_won": lans_won,
        "lans_played": lans_played,
        "major_mvps": major_mvps,
        "total_mvps": total_mvps
    }
    
    player = Player(
        id=id,
        name=name,
        real_name=real_name,
        nationality=nationality,
        age=age,
        team_id=team_id,
        team_name=team_name,
        time_with_team=time_with_team,
        time_with_any_team=time_with_any_team,
        achievements=achievements,
    )

    # Adding the player to the cache before returning
    global_cache.set(CacheType.PLAYERS, id, player)

    return player

def get_player_stats(
        scraper: HLTVScraper,
        id: int,
        player_name: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        match_type: MatchType = None,
        maps: list[Maps] = None
    ) -> Player:
    """
    Gets the full player's stats for the input time interval and returns the Player object.
    """
    interval_string = CacheManager.datetime_interval_to_string(start_date, end_date) # String representing the time interval we're scraping this data for

    # Fetch the player object if not in the cache
    player = global_cache.get(CacheType.PLAYERS, id)
    if player:
        # We skip if the player already has the data
        # We process it for all time interval again though, as it could be different from when we last processed it
        if interval_string != CacheManager.ALL_TIME_INTERVAL and interval_string in player.time_specific_data:
            return player
    else:
        player = get_player(scraper, id, player_name)

    url = f"{scraper.default_url}/stats/players/{id}/{player_name if player_name else "random"}"
    url += URLUtil.get_end_of_url(start_date, end_date, match_type, maps)

    buttons = [scraper.cookie_text]
    soup = scraper.get_website(url, buttons)

    role_stats_container_div = soup.find("div", class_="role-stats-container standard-box")

    stats_section_firepower_div = role_stats_container_div.find("div", class_="role-stats-section role-firepower")
    combined_stats_section_firepower_div = stats_section_firepower_div.find("div", class_="role-stats-section-title-wrapper stats-side-combined")
    firepower = int(combined_stats_section_firepower_div.find("div", class_="row-stats-section-score").find(text=True, recursive=False).strip())

    # There is also another div with this class name as part of it, so we need to filter for the one with this class name exactly
    target_class_name = "role-stats-section-columns"
    stats_section_columns_divs = role_stats_container_div.find_all("div", class_=target_class_name)
    stats_section_columns_div = None
    for div in stats_section_columns_divs:
        classes = div.get('class')
        if len(classes) == 1 and classes[0] == target_class_name:
            stats_section_columns_div = div
    combined_stat_divs = stats_section_columns_div.find_all("div", class_="role-stats-section-title-wrapper stats-side-combined", recursive=True)
    stat_title_to_value_map = {}
    for combined_stat_div in combined_stat_divs:
        stat_section_title_div = combined_stat_div.find("div", class_="role-stats-section-title")

        # We can't get the text directly since it's not the only category, so we iterate through the fields and hardcode instead
        stat_title = stat_section_title_div.contents[2].split("\n")[1]
        stat_value = int(stat_section_title_div.find("div", class_="row-stats-section-score").find(text=True, recursive=False).strip())
        stat_title_to_value_map[stat_title] = stat_value

    statistics_div = soup.find("div", class_="statistics")
    stat_row_divs = statistics_div.find_all("div", class_="stats-row")
    for stat_row_div in stat_row_divs:
        # first span is name, second span is value
        spans = stat_row_div.find_all("span")
        stat_title = spans[0].get_text(strip=True)
        stat_value = float(spans[1].get_text(strip=True).replace('%', ''))
        stat_title_to_value_map[stat_title] = stat_value

    # Storing the stats into the player's data dictionary
    player.time_specific_data[interval_string] = {
        "firepower": firepower,
        "entrying": stat_title_to_value_map["Entrying"],
        "trading": stat_title_to_value_map["Trading"],
        "opening": stat_title_to_value_map["Opening"],
        "clutching": stat_title_to_value_map["Clutching"],
        "sniping": stat_title_to_value_map["Sniping"],
        "utility": stat_title_to_value_map["Utility"],
        "headshot_percentage": stat_title_to_value_map["Headshot %"],
        "kd_ratio": stat_title_to_value_map["K/D Ratio"],
        "rounds_played": stat_title_to_value_map["Rounds played"],
        "dpr": stat_title_to_value_map["Damage / Round"],
        "kpr": stat_title_to_value_map["Kills / round"],
        "apr": stat_title_to_value_map["Assists / round"],
        "dpr": stat_title_to_value_map["Deaths / round"],
        "rating_2.1": stat_title_to_value_map["Rating 2.1"]
    }

    # Storing the player with the additional stats into the cache
    global_cache.set(CacheType.PLAYERS, id, player)

    return player
