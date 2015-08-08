class WunderlistListResolver:
    ''' Resolves user-entered (read: imperfect) list names to list IDs '''
    def __init__(self, wunderlist_access_token, wunderlist_client_id):
        # TODO In the future, we'll need to set up a wunderclient here to query for lists
        pass

    def resolve(self, list_name):
        # TODO We'll want to hit the local mapping of list name -> list ID, once it's set up
        # TODO For now, we just return my inbox
        return 103574383
