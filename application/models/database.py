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

db = scoped_session(sessionmaker())
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

    def get_n_order_similar_artists(self, order, all_set=None, frontier=None):
        # if not all_set:
        #     all_set = {}
        # if not frontier:
        #     frontier = self.similar_artists.all()
        # if order == 0:
        #     return all_set
        # else:
        #     future_frontier = []
        #     for el in frontier:
        #         future_frontier.extend(db.query(Artist).filter(Artist.title == el.get_title()).first().get_similar_artists())
        #         if not all_set.get(el.get_title()):
        #             all_set[el.get_title()] = el
        #     return self.get_n_order_similar_artists(order - 1, all_set, future_frontier)
        frontier = self.similar_artists.all()
        # frontier_offsets = [len(frontier)]
        all_set = {}
        scores = {}
        offset = 0
        for i in xrange(order):
            future_frontier = []
            # future_frontier_offsets = []
            for index, el in enumerate(frontier):
                if i != order - 1:
                    similar_artists = db.query(Artist).filter(
                        Artist.title == el.get_title()).first().get_similar_artists()
                    # future_frontier_offsets.append(len(similar_artists))
                    # for child in similar_artists:
                    #     paths[child.get_title()] = {'parent': el.get_title()}

                    future_frontier.extend(similar_artists)
                if not all_set.get(el.get_title()):
                    all_set[el.get_title()] = el
                    scores[el.get_title()] = offset + index
                    # offset, parent_index = self.get_offset(frontier_offsets, index)
                    # if i == 0:
                    #     paths[el.get_title()] = {}
                    # else:
                    #     paths[el.get_title()] = paths[paths[el.get_title()]['parent']]
                    # if not paths[el.get_title()].get(i + 1):
                    #     paths[el.get_title()][i + 1] = self.get_offset(frontier_offsets, index)
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


Index('my_index', Artist.id, unique=True, mysql_length=255)
