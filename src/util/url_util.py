from enums.maps import Maps
from enums.match_types import MatchType
from datetime import datetime

class URLUtil:
    def get_end_of_url(
        start_date: datetime,
        end_date: datetime,
        match_type: MatchType = None,
        maps: list[Maps] = []
    ) -> str:
        """
        Constructs the string to attach to the end of the url to customize the options for certain HLTV pages
        """
        url = f"startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}"
        if match_type: # When match_type is null, we make the query for all match types, which is done by not specifying any arguments in the url
            url += f"&matchType={match_type.value}"
        if maps: # When maps is null, we make the query for all maps, which is done by not specifying any arguments in the url
            for map in maps:
                url += f"&maps={map.value}"
        return url

