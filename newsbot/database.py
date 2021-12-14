from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, insert, delete, update, select, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy_utils import database_exists, create_database

from newsbot.config import BOT_DATABASE_PATH

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    interval = Column(Integer, nullable=False, default=5)
    state = Column(Integer, nullable=False, default=0)


class Topics(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String, nullable=False)


class UserTopics(Base):
    __tablename__ = 'user_topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'))

    topic_id = Column(Integer, ForeignKey('topics.id'))
    topic = relationship('Topics', backref=backref('user_topics', order_by=topic_id))


class UserShownPosts(Base):
    __tablename__ = 'user_shown_posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, nullable=False)
    user_id = Column(String, ForeignKey('users.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))


engine = create_engine(f'sqlite://{BOT_DATABASE_PATH}')
if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)


class DatabaseController:
    def __init__(self):
        self.session = Session()

    def add_user(self, a_id):
        self.session.add(Users(id=a_id))
        self.session.commit()

    def get_user(self, a_id):
        return self.session.query(Users).get(a_id)

    def add_user_if_not_exists(self, a_id):
        if self.get_user(a_id) is None:
            self.add_user(a_id)

    def add_topic(self, a_topic_name):
        self.session.add(Topics(topic_name=a_topic_name))
        self.session.commit()

    def get_topic(self, a_topic_name):
        return self.session.query(Topics).filter_by(topic_name=a_topic_name).first()

    def add_topic_if_not_exists(self, a_topic_name):
        if self.get_topic(a_topic_name) is None:
            self.add_topic(a_topic_name)

    def add_topic_to_user(self, a_user_id, a_topic_name):
        topic_id = self.get_topic(a_topic_name).id
        self.session.add(UserTopics(user_id=a_user_id, topic_id=topic_id))
        self.session.commit()

    def has_user_topic(self, a_user_id, a_topic_name):
        topic_id = self.get_topic(a_topic_name).id
        user = self.session.query(UserTopics).filter_by(user_id=a_user_id, topic_id=topic_id).first()
        return user is not None

    def add_shown_post(self, a_user_id, a_topic_name, a_post_id):
        topic_id = self.get_topic(a_topic_name).id
        self.session.add(UserShownPosts(post_id=a_post_id, user_id=a_user_id, topic_id=topic_id))
        self.session.commit()

    def update_user_interval(self, a_user_id, a_interval):
        stmt = update(Users).where(Users.id == a_user_id).values(inverval=a_interval)
        self.session.execute(stmt)

    def update_user_state(self, a_user_id, a_state):
        stmt = update(Users).where(Users.id == a_user_id).values(state=a_state)
        self.session.execute(stmt)

    def get_users_topics(self, a_user_id):
        topic_ids = self.session.query(UserTopics.topic).filter_by(user_id=a_user_id).all()
        return [topic.topic_name for topic in topic_ids]

    def get_user_shown_posts(self, a_user_id, a_topic_name):
        topic_id = self.get_topic(a_topic_name).id
        posts_id = self.session.query(UserShownPosts.post_id).filter_by(user_id=a_user_id, topic_id=topic_id).all()
        return posts_id

    def delete_topic_of_user(self, a_user_id, a_topic_name):
        topic_id = self.get_topic(a_topic_name).id
        self.session.query(UserTopics).filter_by(UserTopics.user_id == a_user_id, UserTopics.topic_id == topic_id).\
            delete()
        self.session.commit()
