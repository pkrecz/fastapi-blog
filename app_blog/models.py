from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Boolean, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base


class UserModel(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    posts: Mapped[list["PostModel"]] = relationship(back_populates="users")


class PostModel(Base):

    __tablename__ = "post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, server_default="False")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    users: Mapped["UserModel"] = relationship(back_populates="posts")
    images: Mapped[list["ImageModel"]] = relationship(back_populates="posts")


class ImageModel(Base):

    __tablename__ = "image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    location: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"))
    posts: Mapped["PostModel"] = relationship(back_populates="images")
