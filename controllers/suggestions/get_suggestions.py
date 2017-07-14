from generate_playlist import get_suggestions
from network import load_network_with_songs
from song import load_songs


def create_suggestion_list(input_playlist, network):
    NUMBER_SOURCES = 10000


    # playlist = ["Jon Hopkins", "Radiohead", "Tame Impala", "Bonobo", "Coldplay", "Bon Iver", "Nirvana", "David Bowie",
    #             "The xx"]
    playlist = {}
    for song in input_playlist:
        data = song.split(" - ")
        if len(data) < 2:
            continue
        if network.get_member_by_title(data[0]):
            artist = data[0]
            song_title = data[1]
        elif network.get_member_by_title(data[1]):
            artist = data[1]
            song_title = data[0]
        else:
            continue

        playlist[artist] = song_title

    print playlist.keys()
    if not playlist.keys():
        return

    suggestions = get_suggestions(required_suggestions=10, required_unique_bands=3, playlist=playlist.keys(),
                                  network=network)
    if not suggestions:
        return
    return [(el[0].get_title() + " by " + el[1].get_title()).decode('utf-8') for el in suggestions]
    # return playlist.keys()
