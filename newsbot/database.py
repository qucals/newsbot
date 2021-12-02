from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

from newsbot.config import BOT_DATABASE_PATH

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    interval_send_news = Column(Integer, nullable=False, default=5)
    current_page = Column(Integer, nullable=False, default=0)


class UserTopics(Base):
    __tablename__ = 'user_topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    chosen_topic = Column(String, nullable=False)


class UserPagesShown(Base):
    __tablename__ = 'user_pages_shown'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    page_id = Column(Integer, nullable=False)
    topic = Column(String, nullable=False)


engine = create_engine(f'sqlite://{BOT_DATABASE_PATH}')
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(bind=engine)
