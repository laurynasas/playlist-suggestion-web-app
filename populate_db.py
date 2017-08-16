
from application.models.database import db
from application.models.database import Song, Artist

NUMBER_SOURCES = 22205
NETWORK_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/network.txt"
SONGS_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/songs_already_visited.txt"
SOURCE_MARKER = "++"


def remove_blacklisted(lines, blacklist):
    skip = False
    for index,line in enumerate(lines):
        if SOURCE_MARKER not in line and skip:
            lines[index] = ""
            continue
        if line.replace("\n", "").replace(SOURCE_MARKER, "") in blacklist:
            lines[index] = ""
            if SOURCE_MARKER in line:
                skip=True
        elif SOURCE_MARKER in line and line.replace("\n", "").replace(SOURCE_MARKER, "") not in blacklist:
            skip=False
    return lines

def populate():
    f = open("/home/laurynas/workspace/suggest_playlist/application/resources/final_black_list.txt", "r")

    data = f.readlines()

    blacklist = []
    for line in data:
        artist, title = line.split(" | ")
        blacklist.append(artist)

    songs = open(SONGS_DIR, "r")
    songs_content = songs.readlines()
    songs_content = remove_blacklisted(songs_content, blacklist)
    source = None
    line_counter = 0

    network_file = open(NETWORK_DIR, "r")
    content = network_file.readlines()
    content = remove_blacklisted(content, blacklist)
    already_visited_sources={}
    sources = 0
    for line in content:
        if not line:
            print "Skipping"
            continue
        # if sources == 100:
        #     break
        title = line.replace("\n", "")
        print sources, "/", NUMBER_SOURCES
        # if line.replace("\n", "").replace(SOURCE_MARKER, "") in blacklist:
        #     print title + " is blacklisted"
        #     continue
        if SOURCE_MARKER in title:
            title = title.replace(SOURCE_MARKER, "")

            # source = db.query(Artist).filter(Artist.title == title).first()
            source = already_visited_sources.get(title)
            # print title
            if not source:
                source = Artist(title=title)
                already_visited_sources[title] = source
                db.add(source)
            sources += 1
        else:
            similar_artist = already_visited_sources.get(title)
            if not similar_artist:
                similar_artist = Artist(title=title)
                already_visited_sources[title] = similar_artist
                db.add(similar_artist)
            ret = source.add_similar_artist(similar_artist)
            if not ret:
                continue
            db.add(ret)

    db.commit()
    sources = 0
    # skip = False
    for line in songs_content:
        # if sources == 100:
        #     break
        print sources, "//", NUMBER_SOURCES
        title = line.replace("\n", "")
        if SOURCE_MARKER in title:
            title = title.replace(SOURCE_MARKER, "")
            # skip=False
            # if title in blacklist:
            #     skip=True
            #     print title + " Skipping blacklisted source--->>>>>>>>>>"
            #     continue
            source = db.query(Artist).filter(Artist.title == title).first()
            # print title
            if not source:
                source = Artist(title=title)
                db.add(source)
                db.commit()
            sources += 1
        else:
            # if skip:
            #     continue
            new_song = Song(title=title, artist_id=source.id, artist_title=source.title)
            db.add(new_song)
        line_counter += 1


