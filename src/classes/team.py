from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Team:
    id: int # The team's ID that HLTV has assigned it
    name: str # The name of the team
    region: str # The country/region the team is based in(ex: Russia, Europe, Brazil, Other, etc)
    players: List[str] = field(default_factory=list) # The HLTV IDs of the current players on this team
    coach: Optional[int] = None # The HLTV ID of the team's coach
    time_specific_data: Dict[str, any] = field(default_factory=dict) # Dictionary containing info about the team across a period of time(ex: games played)
