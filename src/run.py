from enums import *
from hltv import *
from datetime import datetime

# For manual testing, delete once done w manual testing
client = HLTV(1)

# print(client.get_upcoming_matches(True))

# print(
#     client.list_top_teams(
#         datetime.strptime("2025-04-09", "%Y-%m-%d"),
#         datetime.strptime("2025-07-09", "%Y-%m-%d"),
#         maps = [Maps.DUST2, Maps.MIRAGE],
#         num_results = 50
#     )
# )

# print(client.get_team(9565)) # vitality
# print(client.get_team(7020)) # spirit

# print(client.get_player(21167)) # donk
# print(client.get_player(11893)) # zywoo
# print(client.get_player(24177)) # kyousuke

print(
    client.get_player_stats(
        21167,
        start_date=datetime.strptime("2025-04-09", "%Y-%m-%d"),
        end_date=datetime.strptime("2025-07-09", "%Y-%m-%d"),
    )
)

client.close_connection()
