from util.scraper import *
from datetime import datetime

hltv_sort_by_time_page_tag = "plausible-event-name=Matches+click+time+match" # All matches in the HLTV matches page sorted by time will have this tag

def get_upcoming_matches(scraper: HLTVScraper, skip_pending_team_matches=False):
    """
    Looks through HLTV's upcoming matches and returns a list of dicts, where each dict represents a match and has the following fields:

    team1: Name of the first team of this match(None if undecided/unclear)
    team2: Name of the second team of this match(None if undecided/unclear)
    format: The type of match this is(ex: bo1, bo3, bo5)
    match_time: The time this match will be played as a datetime object

    The results are ordered based on ascending time. If skip_pending_team_matches is set to True, then matches where a team is yet to be decided will be skipped
    """
    buttons = [scraper.cookie_text]
    soup = scraper.get_website(f"{scraper.default_url}/matches", buttons)

    # Find all divs with class "match"
    match_divs = soup.find_all("div", class_="match")

    matches = []
    for match_div in match_divs:
        # We are only processing matches in the sorted by time page
        match_in_sorted_by_time_page = any(
            hltv_sort_by_time_page_tag in (a.get('class') or [])
            for a in match_div.find_all('a')
        )
        if not match_in_sorted_by_time_page:
            continue

        # Some matches don't have the teams decided yet, in which case the team event will be None
        # Other matches will have the team be the winner of another match, in which case the team div will be set but there won't be a name
        team1_div = match_div.find('div', class_='match-team team1')
        team1_name_div = team1_div.find('div', class_='match-teamname') if team1_div else None
        team1_name = team1_name_div.get_text(strip=True) if team1_name_div else None
        team2_div = match_div.find('div', class_='match-team team2')
        team2_name_div = team2_div.find('div', class_='match-teamname') if team2_div else None
        team2_name = team2_name_div.get_text(strip=True) if team2_name_div else None

        # Skipping if one of the teams is undecided and skip_pending_team_matches is set
        if skip_pending_team_matches and (not team1_name or not team2_name):
            continue

        # Type of the match
        match_format = match_div.find('div', class_='match-meta').get_text(strip=True)

        # Time of the match, which HLTV displays in your local time, represented as a Python datetime object
        match_is_live = match_div.find('div', class_="match-meta match-meta-live")
        if match_is_live is not None and match_is_live.get_text(strip=True) == "Live": # Setting live matches' time to now
            match_time = datetime.now()
        else:
            match_time_div = match_div.find('div', class_='match-time')
            match_time = datetime.fromtimestamp(float(match_time_div["data-unix"]) / 1000) # Need to convert ms to seconds

        # HLTV link for the match
        match_link = scraper.default_url + match_div.find('a', href=lambda x: x and x.startswith('/matches/'))['href']

        # Event name for the match
        event_div = match_div.find('div', class_="match-event")
        event = event_div.get("data-event-headline") if event_div else None

        # Adding the match to the list
        matches.append({
            "team1": team1_name,
            "team2": team2_name,
            "format": match_format,
            "event": event,
            "match_time": match_time,
            "match_link": match_link,
        })

    return matches
