#!/usr/bin/env python3

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite3', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer)
    screen_name = Column(String)
    friends = Column(ARRAY(Integer))

    def __repr__(self):
        return "<User(id={}, tweet_id={}, screen_name='{}', friends='{}')>".format(
            self.id, self.tweet_id, self.screen_name, self.friends
        )


Base.metadata.create_all(engine)

if __name__ == '__main__':
    pass
