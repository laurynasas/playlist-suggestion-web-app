from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

followers = Table('followers',
                  Base.metadata,
                  Column('follower_id', Integer, ForeignKey('artist.id')),
                  Column('followed_id', Integer, ForeignKey('artist.id'))
                  )


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    title = Column(Text)

    similar_artists = relationship('Artist',
                                   secondary=followers,
                                   primaryjoin=(followers.c.follower_id == id),
                                   secondaryjoin=(followers.c.followed_id == id),
                                   backref=backref('followers', lazy='dynamic'),
                                   lazy='dynamic')

    def add_similar_artist(self, artist):
        if not self.is_following(artist):
            self.similar_artists.append(artist)
            return self

    def is_following(self, artist):
        return self.similar_artists.filter(followers.c.followed_id == artist.id).count() > 0


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    title = Column(Text)
    artist = relationship('Artist', backref='songs')


Index('my_index', Artist.id, unique=True, mysql_length=255)
