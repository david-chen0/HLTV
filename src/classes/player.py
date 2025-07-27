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

    """
    Dictionary containing the achievements of the player
    Current supported achievements(by sum of all APIs, not each API):
        top20_placements: Dict mapping from year to the player's placement in HLTV's top 20
        majors_won: Number of majors won
        majors_played: Number of majors played in
        lans_won: Number of LANs won
        lans_played: Number of LANS played in
        major_mvps: Number of Major MVPs
        total_mvps: Number of total MVPs
    """
    achievements: Dict[str, any] = field(default_factory=dict)

    """
    Dictionary containing info about the player over a period of time
    Current supported data(by sum of all APIs, not each API):
        firepower: Weighted average that represents a player's firepower, from 0-100
        entrying: How likely a player is to be the first one in, from 0-100
        trading: How good a player is at trading each other, from 0-100
        opening: How likely a player is to get the opening frag, from 0-100
        clutching: How good a player is in the clutch, from 0-100
        sniping: How likely a player is to get a kill with a sniper, from 0-100
        utility: How good a player is with utility, from 0-100
        headshot_percentage: The player's total headshot percentage, from 0-100
        kd_ratio: The player's KD ratio
        rounds_played: The player's rounds played
        dpr: The player's damage per round
        kpr: The player's kills per round, from 0-5
        apr: The player's assists per round, from 0-5
        dpr: The player's deaths per round, from 0-1
        rating_2.1: The player's HLTV v2.1 rating, where 1.0 is the average
    """
    time_specific_data: Dict[str, any] = field(default_factory=dict)
