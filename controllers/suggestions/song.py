from constants import Text


class Song:
    def __init__(self, title, artist):
        self._title = title.decode("utf-8")
        self._artist = artist.decode("utf-8")

    def get_title(self):
        return self._title

    def get_song_artist(self):
        return self._artist


def load_songs(songs_file_dir, sources_to_load, network):
    songs = open(songs_file_dir, "r")
    songs_content = songs.readlines()

    sources = 0
    source = None
    line_counter = 0
    while sources != sources_to_load:
        title = songs_content[line_counter].replace("\n", "")
        if Text.SOURCE_MARKER in title:
            title = title.replace(Text.SOURCE_MARKER, "")
            source = network.get_member_by_title(title)
            sources += 1
        else:
            song = Song(title, source.get_title())
            source.append_song(song)
            network.register_new_song(song)
        line_counter += 1
