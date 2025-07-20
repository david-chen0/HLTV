from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Player:
    id: int # The player's ID that HLTV has assigned them
    name: str # The player's game name
    real_name: Optional[str] # The player's real name
    nationality: Optional[str] # The player's nationality
    age: Optional[int] # The player's age
    team_id: int # The HLTV ID of the team the player is currently playing for
    team_name: str # The name of the team the player is currently playing for
    time_with_team: int # Number of days the player has been on their current team
    time_with_any_team: int # Number of days the player has been with any team

    # Dictionary containing the achievements of the player
    # Current supported achievements(by sum of all APIs, not each API):
    #   top20_placements: Dict mapping from year to the player's placement in HLTV's top 20
    #   majors_won: Number of majors won
    #   majors_played: Number of majors played in
    #   lans_won: Number of LANs won
    #   lans_played: Number of LANS played in
    #   major_mvps: Number of Major MVPs
    #   total_mvps: Number of total MVPs
    achievements: Dict[str, any] = field(default_factory=dict)

    # Dictionary containing the statistics of the player
    # HOW SHOULD WE STRUCTURE THIS, SINCE HLTV GIVES LAST 3 MONTHS OF STATS, MAYBE DICT OF DICTS?
    # WE COULD DO THE SAME AS WITH TEAMS, WHERE THERE ARE TOTAL AND THERE'S TIME BASED
    statistics: Dict[str, any] = field(default_factory=dict)
