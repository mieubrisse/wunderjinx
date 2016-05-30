"""
Description: REST service that caches Wunderlist list names and IDs and provides fuzzy name list lookup
Author: mieubrisse
"""
 
import sys
import argparse
import flask
import difflib
import wunderpy2
import datetime

# Wunderjinx-specific imports
import config

# TODO Add variable names for use when parsing args, e.g.:
DEBUG_FLAG_ARGVAR = "is_debug"

LIST_LOOKUP_ENDPOINT = "/list"
LIST_LOOKUP_NAME_URL_PARAM = "name"
LIST_LOOKUP_REFRESH_URL_PARAM = "refresh"
DEFAULT_LIST_ENDPOINT = "/default-list"

HTTP_BAD_REQUEST_ERROR_CODE = 400
HTTP_NOT_FOUND_ERROR_CODE = 404

# Number of minutes before the Wunderlist list cache will be forcibly refreshed
RESOLVER_CACHE_EXPIRATION_MIN = 10

def _print_error(msg):
    sys.stderr.write('Error: ' + msg + '\n')

class ResolverService():
    """
    Class containing the Wunderlist list cache, with functions for looking up a list by name
    """

    def __init__(self):
        self.wunderclient = wunderpy2.WunderApi().get_client(config.ACCESS_TOKEN, config.CLIENT_ID)
        self.last_refresh_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=RESOLVER_CACHE_EXPIRATION_MIN)
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
        return datetime.datetime.now() - self.last_refresh_timestamp > datetime.timedelta(minutes=RESOLVER_CACHE_EXPIRATION_MIN)

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

def _parse_args(argv):
    """ Parses args into a dict of ARGVAR=value, or None if the argument wasn't supplied """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", dest=DEBUG_FLAG_ARGVAR, action="store_true", default=False, help="If true, the server will reload itself upon code changes")
    return vars(parser.parse_args(argv))
 
def _validate_args(args):
    """ Performs validation on the given args dict, returning a non-zero exit code if errors were found or None if all is well """
    return None
 

def main(argv):
    args = _parse_args(map(str, argv))
    err_code = _validate_args(args)
    if err_code is not None:
        return err_code

    is_debug = args[DEBUG_FLAG_ARGVAR]

    app = flask.Flask("Wunderjinx List Resolver")
    try:
        resolver = ResolverService()
    except Error as e:
        _print_error("Could not connect to Wunderlist")
        sys.exit(1)

    @app.route(LIST_LOOKUP_ENDPOINT)
    def handle_list_lookup():
        """
        Endpoint to fuzzily look up a list's ID by its name
        """
        # Flask somehow has a global "request" variable that contains request information... I don't understand
        #  why they do it this way, but whatever
        name = flask.request.args.get(LIST_LOOKUP_NAME_URL_PARAM, None)
        if name is None:
            flask.abort(HTTP_BAD_REQUEST_ERROR_CODE)
        force_refresh_str = flask.request.args.get(LIST_LOOKUP_REFRESH_URL_PARAM, '')
        force_refresh = force_refresh_str.lower() == "true"
        matching_id = resolver.get_list_by_name(name, force_refresh=force_refresh)
        if matching_id is None:
            flask.abort(HTTP_NOT_FOUND_ERROR_CODE)
        return str(matching_id)

    app.run(debug=is_debug, port=config.RESOLVER_PORT)
 
    return 0
 
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
