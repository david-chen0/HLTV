from cachetools import LRUCache
from dataclasses import is_dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, Dict

class CacheType(Enum):
    PLAYERS = "players" # Maps from player ID to the player info
    TEAMS = "teams" # Maps from team ID to the team info
    MATCHES = "matches" # Maps from match ID to the match info

class CacheManager:
    DATE_FORMAT = "%Y-%m-%d"
    
    @staticmethod
    def datetime_interval_to_string(start_date: datetime, end_date: datetime) -> str:
        return f"{start_date.strftime(CacheManager.DATE_FORMAT)} to {end_date.strftime(CacheManager.DATE_FORMAT)}"
    
    @staticmethod
    def interval_string_to_datetime(interval_string) -> tuple[datetime, datetime]:
        start_str, end_str = interval_string.split(" to ")
        start_date = datetime.strptime(start_str, CacheManager.DATE_FORMAT)
        end_date = datetime.strptime(end_str, CacheManager.DATE_FORMAT)
        return start_date, end_date
    
    # Merges two dataclass objects together
    # The new object is used to deep overwrite(recursively goes through dicts) any duplicate values in the old object
    # Python passes by reference, so calling this with existing_object as the object in the cache is sufficient to editing
    # and does not require an additional call to put the item back in the cache.
    @staticmethod
    def merge_dataclasses(existing_object: Any, new_object: Any):
        # Helper method to deep merge dicts, where the incoming dict's values are prioritized over the base dict
        def deep_merge_dicts(base: dict, incoming: dict) -> dict:
            for key, new_value in incoming.items():
                if key in base:
                    base_value = base[key]
                    # Recurse if both are dicts
                    if isinstance(base_value, dict) and isinstance(new_value, dict):
                        deep_merge_dicts(base_value, new_value)
                    else:
                        # Overwrite non-dict or conflicting types
                        base[key] = new_value
                else:
                    # Key not in base — just add
                    base[key] = new_value
            return base

        if not (is_dataclass(existing_object) and is_dataclass(new_object)):
            raise ValueError("Both arguments must be dataclass instances")

        for f in fields(new_object):
            field_name = f.name
            new_value = getattr(new_object, field_name)
            current_value = getattr(existing_object, field_name)

            if current_value is None:
                setattr(existing_object, field_name, new_value)
            elif isinstance(current_value, list) and isinstance(new_value, list):
                # Merge lists without duplicates, where the new values are used to overwrite the old ones
                merged = new_value + [item for item in current_value if item not in new_value]
                setattr(existing_object, field_name, merged)
            elif isinstance(current_value, dict) and isinstance(new_value, dict):
                # Deep merge the dicts together
                setattr(existing_object, field_name, deep_merge_dicts(current_value, new_value))
            else:
                # Overwrite scalars
                setattr(existing_object, field_name, new_value)

    def __init__(self):
        # Can also set a TTL for the cache using ttl=x for x seconds
        self.cache = {
            CacheType.PLAYERS: LRUCache(maxsize=500),
            CacheType.TEAMS: LRUCache(maxsize=100),
            CacheType.MATCHES: LRUCache(maxsize=1000),
        }

    # Retrieves a single item
    # None is returned if there is no item corresponding to the entity_id in the table
    def get(self, entity_type: CacheType, entity_id: int) -> Any:
        if entity_type not in self.cache:
            raise KeyError(f"Cache type {entity_type} not initialized.")
        return self.cache[entity_type].get(entity_id)

    # Sets the value of a single item
    def set(self, entity_type: CacheType, entity_id: int, data: Any):
        if entity_type not in self.cache:
            raise KeyError(f"Cache type {entity_type} not initialized.")
        self.cache[entity_type][entity_id] = data

    # Gets all items of a specific type
    def get_all(self, entity_type: CacheType) -> Dict[str, Any]:
        if entity_type not in self.cache:
            raise KeyError(f"Cache type {entity_type} not initialized.")
        return self.cache.get[entity_type]
    
# Singleton instance
global_cache = CacheManager()
