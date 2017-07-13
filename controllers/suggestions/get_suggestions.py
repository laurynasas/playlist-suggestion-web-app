from generate_playlist import get_suggestions
from network import load_network
from song import load_songs


def create_suggestion_list(input_playlist):
    NUMBER_SOURCES = 10000

    network = load_network("/home/laurynas/workspace/suggest_playlist/application/resources/network.txt", NUMBER_SOURCES)
    load_songs("/home/laurynas/workspace/suggest_playlist/application/resources/songs_already_visited.txt", NUMBER_SOURCES, network)

    # playlist = ["Jon Hopkins", "Radiohead", "Tame Impala", "Bonobo", "Coldplay", "Bon Iver", "Nirvana", "David Bowie",
    #             "The xx"]
    playlist = {}
    for song in input_playlist:
        data = song.split(" - ")
        #TODO add verification (songs and titles if they exists check thaat)
        artist = data[0]
        if not network.get_member_by_title(artist):
            continue
        song_title = data[1]
        playlist[artist] = song_title

    print playlist.keys()

    suggestions = get_suggestions(required_suggestions=10, required_unique_bands=3, playlist=playlist.keys(), network=network)
    return [(el[0].get_title() + " by " + el[1].get_title()).decode('utf-8') for el in suggestions]
    # return playlist.keys()