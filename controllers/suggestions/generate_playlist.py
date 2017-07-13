from copy import deepcopy

import numpy as np

from network import load_network
from song import load_songs

NUMBER_SOURCES = 20000


def get_n_list_intersection(dics):
    lists = []
    inter = []
    for el in dics:
        lists.append(el.keys())
    keyword_inter = list(set(lists[0]).intersection(*lists))

    for key in keyword_inter:
        inter.append(dics[0][key])

    return inter


def chunkify_playlist(playlist, chunk_size):
    return np.array_split(playlist, len(playlist) / chunk_size)


def get_total_suggestions(all_intersections):
    total_suggestions = 0
    already_visited = []
    for chunk in all_intersections:
        for band in chunk:
            if band.get_title() not in already_visited:
                total_suggestions += len(band.get_outgoing_neighbours())
                already_visited.append(band.get_title())

    return already_visited, total_suggestions


def get_number_of_songs_from_list_artists(artists):
    number_songs = 0
    for artist in artists:
        number_songs += len(artist.get_songs())
    return number_songs


def get_suggestions(required_suggestions, required_unique_bands, playlist, network, chunk_size=3):
    chunks = chunkify_playlist(playlist, chunk_size)

    order = 2
    possible_suggestions = 0
    nu_unique_bands = 0
    all_intersections = []
    while possible_suggestions < required_suggestions or nu_unique_bands < required_unique_bands:
        all_intersections = []
        for chunk in chunks:
            neighbours = []
            for artist in chunk:
                neighbours.append(network.get_source_by_title(artist).get_n_order_neighbours(order, network))
            all_intersections.append(get_n_list_intersection(neighbours))

        unique_bands, possible_suggestions = get_total_suggestions(all_intersections)
        nu_unique_bands = len(unique_bands)
        order += 1

    suggestions = []
    possible_suggestions = 0
    nu_bands_included = 0
    bands = []
    while nu_bands_included < required_unique_bands or possible_suggestions < required_suggestions:
        for chunk in all_intersections:
            if chunk:
                prospective = chunk.pop(0)
                if prospective not in bands:
                    bands.append(prospective)

        nu_bands_included = len(bands)
        for band in bands:
            if not band.get_songs():
                nu_bands_included -= 1

        possible_suggestions = get_number_of_songs_from_list_artists(bands)

    all_songs = []
    all_songs_artists = []
    for artist in bands:
        all_songs.append(deepcopy(artist.get_songs()))
        all_songs_artists.append(artist)

    while len(suggestions) < required_suggestions:
        for artist_songs, artist in zip(all_songs, all_songs_artists):
            if artist_songs and (artist_songs[0], artist) not in suggestions:
                suggestions.append((artist_songs.pop(0), artist))

    return suggestions


def main():
    network = load_network("resources/network.txt", NUMBER_SOURCES)
    load_songs("resources/songs_already_visited.txt", NUMBER_SOURCES, network)

    playlist = ["Jon Hopkins", "Radiohead", "Tame Impala", "Bonobo", "Coldplay", "Bon Iver", "Nirvana", "David Bowie",
                "The xx"]

    suggestions = get_suggestions(required_suggestions=10, required_unique_bands=20, playlist=playlist, network=network)
    print [el[0].get_title() + " by " + el[1].get_title() for el in suggestions]


if __name__ == "__main__":
    main()
