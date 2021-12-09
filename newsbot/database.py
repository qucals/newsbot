from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, insert, delete, update, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

from newsbot.config import BOT_DATABASE_PATH

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    interval_send_news = Column(Integer, nullable=False, default=5)
    current_page = Column(Integer, nullable=False, default=0)
    current_state = Column(Integer, nullable=False, default=0)


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


class DatabaseController:
    @staticmethod
    def add_user(a_id):
        stmt = (
            insert(Users).
            values(user_id=a_id)
        )
        engine.execute(stmt)

    @staticmethod
    def is_there_user(a_id):
        stmt = (
            select(Users.user_id).
            where(Users.user_id == a_id)
        )
        results = engine.execute(stmt).fetchall()
        return len(results) != 0

    @staticmethod
    def add_user_if_there_is_not(a_id):
        if not DatabaseController.is_there_user(a_id):
            DatabaseController.add_user(a_id)

    @staticmethod
    def change_user_interval(a_id, a_interval):
        stmt = (
            update(Users).
            where(Users.user_id == a_id).
            values(interval_send_news=a_interval)
        )
        engine.execute(stmt)

    @staticmethod
    def get_users_topics(a_id):
        stmt = (
            select(UserTopics.chosen_topic).
            where(UserTopics.user_id == a_id)
        )
        cursor = engine.execute(stmt)
        return [d[0] for d in cursor.fetchall()]

    @staticmethod
    def get_user_interval(a_id):
        stmt = (
            select(Users.interval_send_news).
            where(Users.user_id == a_id)
        )
        cursor = engine.execute(stmt)
        return cursor.fetchall()[0][0]

    @staticmethod
    def has_user_topic(a_user_id, a_topic):
        stmt = (
            select(UserTopics.user_id).
            where(UserTopics.user_id == a_user_id).
            where(UserTopics.chosen_topic == a_topic)
        )
        cursor = engine.execute(stmt)
        return len(cursor.fetchall()) != 0

    @staticmethod
    def add_topic_to_user(a_id, a_topic):
        stmt = (
            insert(UserTopics).
            values(user_id=a_id, chosen_topic=a_topic)
        )
        engine.execute(stmt)

    @staticmethod
    def remove_topic_of_user(a_id, a_topic):
        stmt = (
            delete(UserTopics).
            where(UserTopics.user_id == a_id).
            where(UserTopics.chosen_topic == a_topic)
        )
        engine.execute(stmt)

    @staticmethod
    def get_user_state(a_id):
        stmt = (
            select(Users.current_state).
            where(Users.user_id == a_id)
        )
        cursor = engine.execute(stmt)
        return cursor.fetchall()[0][0]

    @staticmethod
    def set_user_state(a_id, a_state):
        stmt = (
            update(Users).
            where(Users.user_id == a_id).
            values(current_state=a_state)
        )
        engine.execute(stmt)
