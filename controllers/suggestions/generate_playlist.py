import time

import numpy as np

from application import db
from application.models.database import Artist

NUMBER_SOURCES = 20000
from scoring import calculate_score


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
    if chunk_size > len(playlist):
        return np.array_split(playlist, len(playlist))
    return np.array_split(playlist, len(playlist) / chunk_size)


def get_total_suggestions(all_intersections, required_suggestions, required_unique_bands):
    total_suggestions = 0
    already_visited = []
    for chunk in all_intersections:
        for band in chunk:
            if total_suggestions > required_suggestions and len(already_visited) >= required_unique_bands:
                return already_visited, total_suggestions
            if band.get_title() not in already_visited:
                ss = time.time()
                # print db.query(Artist).filter(Artist.id == band.id).first().similar_artists.count()
                total_suggestions += db.query(Artist).filter(Artist.id == band.id).first().similar_artists.count()
                ee = time.time()
                print "simi arti", ee - ss
                already_visited.append(band.get_title())

    return already_visited, total_suggestions


def get_number_of_songs_from_list_artists(artists):
    number_songs = 0
    for artist in artists:
        number_songs += len(artist.get_songs())
    return number_songs


def get_suggestions(required_suggestions, required_unique_bands, playlist):
    chunks = chunkify_playlist(playlist, required_unique_bands)
    order = 2
    possible_suggestions = 0
    nu_unique_bands = 0
    all_intersections = []
    start = time.time()
    while possible_suggestions < required_suggestions or nu_unique_bands < required_unique_bands:
        all_intersections = []
        for chunk in chunks:
            s = time.time()

            ss =time.time()
            neighbours = []
            neighbour_rankings = {}
            for artist in chunk:
                source = db.query(Artist).filter(Artist.title == artist).first()
                if source and source.similar_artists.all():
                    sss = time.time()
                    n_similar_artists, rankings = source.get_n_order_similar_artists(order)
                    eee = time.time()
                    print "Chunk--> n order function:", eee-sss
                    neighbours.append(n_similar_artists)
                    neighbour_rankings[source.get_title()] = rankings
            ee=time.time()
            print "Chunk-> n order: ", ee-ss
            if not neighbours:
                continue
            ss=time.time()
            intersection = get_n_list_intersection(neighbours)
            ee=time.time()
            print "Chunk-> intersection: ", ee-ss
            if not intersection:
                continue

            scores = []
            ss=time.time()
            for prospect_suggestion in intersection:
                scores.append(calculate_score(prospect_suggestion, neighbour_rankings))

            scores, ranked_intersection = zip(*sorted(zip(scores, intersection)))
            ranked_intersection = list(ranked_intersection)
            all_intersections.append(ranked_intersection)
            ee=time.time()
            print "Chunk-> scoring: ", ee-ss
            e = time.time()
            print "Chunk time", e - s
        ss = time.time()
        unique_bands, possible_suggestions = get_total_suggestions(all_intersections, required_suggestions,
                                                                   required_unique_bands)
        ee = time.time()
        print "get total sugg time: ", ee - ss

        nu_unique_bands = len(unique_bands)
        order += 1

    end = time.time()
    print "Stage 1: ", (end - start)

    suggestions = []
    possible_suggestions = 0
    nu_bands_included = 0
    bands = []
    start = time.time()
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
                bands.remove(band)

        possible_suggestions = get_number_of_songs_from_list_artists(bands)
    end = time.time()
    print "Stage 2: ", (end - start)
    start = time.time()
    all_songs = []
    all_songs_artists = []
    for artist in bands:
        all_songs.append(artist.get_songs())
        all_songs_artists.append(artist)
    i = 0
    while len(suggestions) < required_suggestions:
        for artist_songs, artist in zip(all_songs, all_songs_artists):
            if i < len(artist_songs):
                if artist_songs and (artist_songs[i], artist) not in suggestions:
                    suggestions.append((artist_songs[i], artist))
            else:
                continue
        i += 1

    end = time.time()
    print "Stage 3: ", (end - start)

    return suggestions


def main():
    playlist = ["Jon Hopkins", "Radiohead", "Tame Impala", "Bonobo", "Coldplay", "Bon Iver", "Nirvana", "David Bowie",
                "The xx"]

    suggestions = get_suggestions(required_suggestions=10, required_unique_bands=20, playlist=playlist)
    print [el[0].get_title() + " by " + el[1].get_title() for el in suggestions]


if __name__ == "__main__":
    main()
