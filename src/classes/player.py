from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Player:
    id: int # The player's ID that HLTV has assigned them
    name: str # The player's game name
    real_name: Optional[str] # The player's real name
    age: Optional[int] # The player's age
    team_id: str # The HLTV ID of the team the player is currently playing for
    # other things like achievements, wins, rating/statistics, etc
