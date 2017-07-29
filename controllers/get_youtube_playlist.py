from abc import ABCMeta, abstractmethod


class Playlist(object):
    __metaclass__ = ABCMeta

    def __init__(self, id, title):
        self._id = id
        self._title = title

    def get_title(self):
        return self._title


class SpotifyPlaylist(Playlist):
    def __init__(self, playlist_data):
        id = playlist_data.get(u'id')
        title = playlist_data.get(u'name')
        super(SpotifyPlaylist, self).__init__(id, title)

    @staticmethod
    def get_playlist_songs(full_info):
        songs = []

        for song in full_info.get('items'):
            track_info = song.get('track')
            title = " & ".join([artist['name'] for artist in track_info['artists']])
            title = title + ' - ' + track_info['name']
            songs.append(title)

        return songs


class YoutubePlaylist(Playlist):
    def __init__(self, playlist_data):
        id = playlist_data.get(u'id')
        title = playlist_data.get(u'snippet').get(u'title')
        super(YoutubePlaylist, self).__init__(id, title)

    @staticmethod
    def get_playlist_songs(full_info):
        songs = []
        black_list = ['deleted video']
        replace_list = ['with lyrics', 'official video', 'official audio', 'official music video', 'music video',
                        'out now',
                        'explicit', '(audio)', '(music)', '(video)', 'extended versions']
        leading_symbols = '({[]})'
        word_separators = ["-", " "]

        for song in full_info[u'items']:
            processed_song = (song[u'snippet'][u'title']).replace("\\", "").encode('utf-8').strip(" ")
            skip = False

            # Check for banned words
            for banned_word in black_list:
                if banned_word in processed_song.lower():
                    skip = True
                    break

            # Check for single-word titles
            counter = 0
            for sep in word_separators:
                if sep in processed_song:
                    continue
                else:
                    counter += 1

            if counter == len(word_separators) or skip:
                continue

            # Check for shitwords
            for replacement in replace_list:
                start = processed_song.lower().find(replacement)
                if start >= 0:
                    processed_song = processed_song[:start] + processed_song[start + len(replacement):]
                    for _ in xrange(2):
                        if len(processed_song) > start:
                            leading_sym = leading_symbols.find(processed_song[start])
                            if leading_sym >= 0:
                                processed_song = processed_song.replace(processed_song[start], "")
                                start -= 1

            songs.append(processed_song)
        return songs


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


def create_playlists(class_name, playlists):
    all_instances = []
    for playlist in playlists.get('items'):
        all_instances.append(class_name(playlist))
    return all_instances
