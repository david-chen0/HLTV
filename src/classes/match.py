from dataclasses import dataclass, field
from datetime import datetime
# from typing import List, Optional

@dataclass
class Match:
    match_link: str # The link to the match on HLTV
    team1: str # Name of the first team playing
    team2: str # Name of the second team playing
    format: str # The format of the match(ex: bo1, bo3, or bo5)
    event: str # The event the match is a part of
    match_time: datetime # The time the match will be played, represented as a datetime object
