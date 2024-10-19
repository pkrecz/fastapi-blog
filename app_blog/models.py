from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship
from config.database import Base


class UserModel(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100))
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(250), nullable=False)
    is_active = Column(Boolean, default=True)
    posts = relationship('PostModel', back_populates='users')


class PostModel(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='FALSE')
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    created_by = Column(Integer, ForeignKey('user.id'))
    users = relationship('UserModel', back_populates='posts')
