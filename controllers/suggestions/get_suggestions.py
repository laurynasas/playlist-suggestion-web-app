from application import db
from application.models.database import Artist
from generate_playlist import get_suggestions
import re


def create_suggestion_list(input_playlist, required_suggestions=10, number_bands=3):

    print required_suggestions
    print input_playlist

    playlist = {}

    word_separators = ["-", " ", " - ", "&"]
    artist = None
    song_title = None
    for song in input_playlist:
        done = False
        for sep in word_separators:
            data = song.split(sep)
            data = [el.strip(" '\"-") for el in data]

            if len(data) < 2:
                continue
            # print "->", data

            if db.query(Artist).filter(Artist.title == data[0]).first():
                artist = data[0]
                song_title = data[1]
                done = True
                break
            elif db.query(Artist).filter(Artist.title == data[1]).first():
                artist = data[1]
                song_title = data[0]
                done = True
                break
        if not done:
            continue

        playlist[artist] = song_title

    print "keys--", playlist.keys()
    if not playlist.keys():
        return

    suggestions = get_suggestions(required_suggestions=required_suggestions, required_unique_bands=number_bands,
                                  playlist=playlist.keys())
    if not suggestions:
        return
    return suggestions
