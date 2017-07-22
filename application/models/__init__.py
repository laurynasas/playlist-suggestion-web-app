from application.models.song import db
from song import Song, Artist, Base
from sqlalchemy.exc import IntegrityError

NUMBER_SOURCES = 1000
NETWORK_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/network.txt"
SONGS_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/songs_already_visited.txt"
SOURCE_MARKER = "++"


def populate():
    songs = open(SONGS_DIR, "r")
    songs_content = songs.readlines()

    source = None
    line_counter = 0

    network_file = open(NETWORK_DIR, "r")
    content = network_file.readlines()

    i = 0
    sources = 0
    while sources != NUMBER_SOURCES:
        title = content[i].replace("\n", "")
        print sources, "/", NUMBER_SOURCES
        if SOURCE_MARKER in title:
            title = title.replace(SOURCE_MARKER, "")

            source = db.query(Artist).filter(Artist.title == title).first()
            # print title
            if not source:
                source = Artist(title=title)
                db.add(source)
            sources += 1
        else:
            similar_artist = db.query(Artist).filter(Artist.title == title).first()
            if not similar_artist:
                similar_artist = Artist(title=title)
                db.add(similar_artist)
            ret = source.add_similar_artist(similar_artist)
            if not ret:
                i += 1
                continue
            db.add(ret)
        i += 1
    db.commit()
    sources = 0
    while sources != NUMBER_SOURCES:
        print sources, "//", NUMBER_SOURCES
        title = songs_content[line_counter].replace("\n", "")
        if SOURCE_MARKER in title:
            title = title.replace(SOURCE_MARKER, "")

            source = db.query(Artist).filter(Artist.title == title).first()
            # print title
            if not source:
                source = Artist(title=title)
                db.add(source)
                db.commit()
            sources += 1
        else:
            source = db.query(Artist).filter(Artist.title == source.title).first()
            new_song = Song(title=title, artist_id=source.id, artist_title=source.title)
            db.add(new_song)
        line_counter += 1


def initialize_sql(engine):
    db.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    # try:
    #     populate()
    # except IntegrityError:
    #     print "Some entries already exists in database"
    # db.commit()
