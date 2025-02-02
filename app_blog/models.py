from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Boolean, TIMESTAMP, text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base


class UserModel(Base):

    __tablename__ = "user"
    __table_args__ = (
                        Index("idx_user_id", "id", postgresql_using="btree"),
                        Index("idx_user_username", "username", postgresql_using="btree"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    posts: Mapped[list["PostModel"]] = relationship("PostModel", back_populates="users")


class PostModel(Base):

    __tablename__ = "post"
    __table_args__ = (
                        Index("idx_post_id", "id", postgresql_using="btree"),
                        Index("idx_post_title", "title", postgresql_using="btree"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, server_default="False")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    users: Mapped["UserModel"] = relationship("UserModel", back_populates="posts")
    images: Mapped[list["ImageModel"]] = relationship("ImageModel", back_populates="posts")


class ImageModel(Base):

    __tablename__ = "image"
    __table_args__ = (
                        Index("idx_image_id", "id", postgresql_using="btree"),
                        Index("idx_image_post_id", "post_id", postgresql_using="btree"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"))
    posts: Mapped["PostModel"] = relationship("PostModel", back_populates="images")
