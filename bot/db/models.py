from datetime import date

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Date

from bot.db.base import Base


class User(Base):
    __tablename__ = 'user'

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    name = Column(String(255), default='')
    username = Column(String(255), default='')
    stars_count = Column(Integer, default=0)
    free_throws = Column(Integer, default=4)
    last_free_throw_date = Column(Date, default=date.today)
    channel_ids_to_subscribe = Column(String(255), default='')
    games_count = Column(Integer, default=0)
    referer_id = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)


class Channel(Base):
    __tablename__ = 'channel'

    channel_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    link = Column(String(255), default='')
    name = Column(String(255), default='')
    is_active = Column(Boolean, default=True)


class NFT(Base):
    __tablename__ = 'nft'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String(255), default='')
    owner_id = Column(BigInteger, default=0)
