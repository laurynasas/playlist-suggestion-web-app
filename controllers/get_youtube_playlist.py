class Playlist:
    def __init__(self, json_info):
        self._id = json_info[u'id']
        self._title = json_info[u'snippet'][u'title']

    def get_title(self):
        return self._title


def print_results(results):
    print(results)


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def list_playlists_mine(service, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    results = service.playlists().list(
        **kwargs
    ).execute()
    return results


def playlist_items_list_by_playlist_id(service, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    results = service.playlistItems().list(
        **kwargs
    ).execute()
    return results


def get_playlist_songs(json_info):
    songs = []
    for song in json_info[u'items']:
        songs.append((song[u'snippet'][u'title']).replace("\\", "").encode('utf-8'))
    return songs


def create_playlists(playlists):
    all_instances = []
    for playlist in playlists[u'items']:
        all_instances.append(Playlist(playlist))
    return all_instances
