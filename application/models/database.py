from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
import time
import json
db = scoped_session(sessionmaker())
Base = declarative_base()

followers = Table('followers',
                  Base.metadata,
                  Column('follower_id', Integer, ForeignKey('artist.id')),
                  Column('followed_id', Integer, ForeignKey('artist.id'))
                  )


class Artist(Base):
    __tablename__ = 'artist'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    title = Column(Text)

    similar_artists = relationship('Artist',
                                   secondary=followers,
                                   primaryjoin=(followers.c.follower_id == id),
                                   secondaryjoin=(followers.c.followed_id == id),
                                   backref=backref('followers', lazy='dynamic'),
                                   lazy='dynamic')


    def  add_similar_artist(self, artist):
        if not self.is_following(artist):
            self.similar_artists.append(artist)
            return self

    def get_title(self):
        return self.title

    def get_similar_artists(self):
        return self.similar_artists.all()

    def is_following(self, artist):
        return self.similar_artists.filter(followers.c.followed_id == artist.id).count() > 0

    def get_offset(self, offsets, index):
        acc = 0
        for off in offsets:
            if acc + off >= index + 1:
                return index - acc
            acc += off

    def get_n_order_similar_artists(self, order):
        frontier = self.similar_artists.all()
        all_set = {}
        scores = {}
        offset = 0
        for i in xrange(order):
            future_frontier = []
            for index, el in enumerate(frontier):
                if i != order - 1:
                    s = time.time()
                    similar_artists = el.similar_artists.all()
                    print "retrieval:", time.time() - s
                    future_frontier.extend(similar_artists)
                if not all_set.get(el.get_title()):
                    all_set[el.get_title()] = el
                    scores[el.get_title()] = offset + index

            offset = len(frontier)
            frontier = future_frontier
        return all_set, scores

    def get_songs(self):
        return self.songs


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist_title = Column(Text)
    title = Column(Text)
    artist = relationship('Artist', backref='songs')
    preview_url = Column(Text, default=None)

    def get_full_title(self):
        return self.artist_title + " - " + self.title

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Index('follower_id_index', followers.c.follower_id, mysql_length=255)
