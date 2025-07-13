from enums import *
from hltv import *
from datetime import datetime

# For manual testing, delete once done w manual testing
client = HLTV(1)
# client.get_upcoming_matches(True)

client.list_top_teams(
    datetime.strptime("2025-04-09", "%Y-%m-%d"),
    datetime.strptime("2025-07-09", "%Y-%m-%d"),
    maps = Maps.DUST2,
    num_results = 50
)
