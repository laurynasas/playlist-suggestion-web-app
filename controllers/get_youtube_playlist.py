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
    black_list = ['deleted video']
    replace_list = ['with lyrics', 'official video', 'official audio', 'official music video', 'music video', 'out now',
                    'explicit', '(audio)', '(music)', '(video)', 'extended versions']
    leading_symbols = '({[]})'
    word_separators = ["-", " "]

    for song in json_info[u'items']:
        processed_song = (song[u'snippet'][u'title']).replace("\\", "").encode('utf-8').strip(" ")
        skip = False

        #Check for banned words
        for banned_word in black_list:
            if banned_word in processed_song.lower():
                skip = True
                break


        #Check for single-word titles
        counter = 0
        for sep in word_separators:
            if sep in processed_song:
                continue
            else:
                counter +=1

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


def create_playlists(playlists):
    all_instances = []
    for playlist in playlists[u'items']:
        all_instances.append(Playlist(playlist))
    return all_instances
