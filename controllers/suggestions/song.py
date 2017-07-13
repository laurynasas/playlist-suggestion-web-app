from constants import Text


class Song:
    def __init__(self, title):
        self._title = title

    def get_title(self):
        return self._title

def load_songs(songs_file_dir, sources_to_load, network):
    songs = open(songs_file_dir, "r")
    songs_content = songs.readlines()

    sources = 0
    source = None
    while sources != sources_to_load:
        title = songs_content[sources].replace("\n", "")

        if Text.SOURCE_MARKER in title:
            title = title.replace(Text.SOURCE_MARKER, "")
            source = network.get_member_by_title(title)
        else:
            song = Song(title)
            source.append_song(song)
        sources += 1
