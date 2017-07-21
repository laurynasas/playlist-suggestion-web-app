from generate_playlist import get_suggestions


def create_suggestion_list(input_playlist, network, required_suggestions=10, number_bands=3):
    NUMBER_SOURCES = 10000

    print required_suggestions
    print input_playlist
    # playlist = ["Jon Hopkins", "Radiohead", "Tame Impala", "Bonobo", "Coldplay", "Bon Iver", "Nirvana", "David Bowie",
    #             "The xx"]
    playlist = {}

    for song in input_playlist:
        data = song.split(" - ")
        data = [el.replace("'", "").lstrip() for el in data]

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

    print "keys--", playlist.keys()
    if not playlist.keys():
        return

    suggestions = get_suggestions(required_suggestions=required_suggestions, required_unique_bands=number_bands,
                                  playlist=playlist.keys(),
                                  network=network)
    if not suggestions:
        return
    return suggestions
    # return playlist.keys()
