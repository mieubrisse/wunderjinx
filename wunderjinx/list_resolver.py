"""
Description: REST service that caches Wunderlist list names and IDs and provides fuzzy name list lookup
Author: mieubrisse
"""
 
import sys
import argparse
import difflib
import wunderpy2
import datetime

# Wunderjinx-specific imports
import config

# Number of minutes before the Wunderlist list cache will be forcibly refreshed
DEFAULT_CACHE_EXPIRATION_MIN = 10

class ResolverService():
    """
    Class containing the Wunderlist list cache, with functions for looking up a list by name
    """

    def __init__(self, cache_expiration_min=DEFAULT_CACHE_EXPIRATION_MIN):
        self.wunderclient = wunderpy2.WunderApi().get_client(config.ACCESS_TOKEN, config.CLIENT_ID)
        self.cache_expiration_min=cache_expiration_min
        self.last_refresh_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=cache_expiration_min)
        self._refresh_lists()

    def _refresh_lists(self):
        """
        Make a best-effort attempt to refresh the cache
        """
        try:
            wunderlist_lists = self.wunderclient.get_lists()
            self.lists = { wl_list[wunderpy2.List.TITLE]: wl_list for wl_list in wunderlist_lists }
            self.last_refresh_timestamp = datetime.datetime.now()
        except (wunderpy2.exceptions.ConnectionError, wunderpy2.exceptions.TimeoutError) as e:
            print "Warning: Couldn't refresh cache of Wunderlist lists: " + str(e)

    def _is_cache_stale(self):
        return datetime.datetime.now() - self.last_refresh_timestamp > datetime.timedelta(minutes=self.cache_expiration_min)

    def get_list_by_name(self, name, force_refresh=False):
        """
        Gets the ID of the Wunderlist list whose name most closely matches the given name

        Return:
        ID of the matching Wunderlist list, or None if no list matched
        """
        if force_refresh or self._is_cache_stale():
            self._refresh_lists()
        matching_list_names = difflib.get_close_matches(name.strip(), self.lists.keys(), n=1)
        target_list_name = matching_list_names[0] if len(matching_list_names) > 0 else None
        if target_list_name is None:
            return None
        return self.lists[target_list_name][wunderpy2.List.ID]
