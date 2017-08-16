from application.models.database import db, Artist, Song
from generate_playlist import get_suggestions
from sqlalchemy import and_
import time
def create_suggestion_list(input_playlist, required_suggestions=10, number_bands=3):
    print required_suggestions
    print input_playlist
    start = time.time()
    playlist = []
    print "Will be trying to find artists and songs"
    word_separators = ["-"]
    artist = None
    song_title = None
    s = time.time()

    for song in input_playlist:
        done = False
        for existing_artist in playlist:
            if existing_artist in song:
                done = True
                print existing_artist, "already exists -SKIPPITNG"
                break
        if done:
            continue

        for sep in word_separators:
            data = song.split(sep)
            data = [el.strip(" '\"-") for el in data]

            if len(data) < 2:
                continue

            if db.query(Song).filter(Song.artist_title.like(data[1])).first():
                artist = data[1]
                done = True
                break
            elif db.query(Song).filter(Song.artist_title.like(data[0])).first():
                artist = data[0]
                done = True
                break

        if not done:
            continue

        playlist.append(artist)
    e = time.time()
    print "Song time to process artist only: ", e - s
    print "keys--", playlist, len(playlist)
    if not playlist:
        return
    end = time.time()
    print "Stage -1: ", (end - start)

    start = time.time()

    suggestions = get_suggestions(required_suggestions=required_suggestions, required_unique_bands=number_bands,
                                  playlist=playlist)
    end = time.time()
    print "Stage 0: ", (end - start)

    if not suggestions:
        return
    return suggestions
