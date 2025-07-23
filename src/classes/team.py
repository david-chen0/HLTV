from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Team:
    id: int # The team's ID that HLTV has assigned it
    name: str # The name of the team
    region: str # The country/region the team is based in(ex: Russia, Europe, Brazil, Other, etc)
    valve_rank: int # The team's current Valve rank
    world_rank: int # The team's current World rank
    players: Dict[str, int] = field(default_factory=dict) # Map from the team's current players' game names to their HLTV IDs
    coach: Dict[str, int] = field(default_factory=dict) # Map from coach's game name to their HLTV ID
    time_specific_data: Dict[str, any] = field(default_factory=dict) # Dictionary containing info about the team across a period of time(ex: games played)
