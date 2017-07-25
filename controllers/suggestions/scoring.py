import warnings

from application.models.database import db, Artist


def calculate_score(suggested_artist, source_rankings):
    acc_similarity_rating = 0

    for source, rankings in source_rankings.iteritems():
        acc_similarity_rating += rankings[suggested_artist.get_title()]

    return acc_similarity_rating

    # for given_artist in playlist:
    #     given_artist = db.query(Artist).filter(Artist.title == given_artist).first()
    #     if given_artist:
    #         similar_artists = given_artist.similar_artists.all()
    #     else:
    #         warnings.warn("Artist in chunk does not exist in database!")
    #         continue
    #
    #     # We start from 1st
    #     if suggested_artist in paths:
    #         indices = paths[suggested_artist].values()
    #         rating = sum([indx for indx in indices]) + len(indices)
    #         acc_similarity_rating += rating
    #     else:
    #         warnings.warn("For some reason I coulnd't find this artist in similar artist list")
    #
    # return acc_similarity_rating
