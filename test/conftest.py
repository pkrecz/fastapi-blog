import pytest
import logging
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from config.database import get_engine, get_db 
from main import app


@pytest.fixture(scope="session")
def db():
    connection = get_engine().connect()
    logging.info("Configuration -----> Connection established.")
    transaction = connection.begin()
    logging.info("Configuration -----> Transaction started.")
    session = sessionmaker(
                            autocommit=False,
                            autoflush=False,
                            bind=connection)()
    logging.info("Configuration -----> Session ready for running.")
    yield session
    session.close()
    logging.info("Configuration -----> Session closed.")
    transaction.rollback()
    logging.info("Configuration -----> Rollback executed.")
    connection.close()
    logging.info("Configuration -----> Connection closed.")


@pytest.fixture(scope="session")
def client(db):

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    logging.info("Configuration -----> Dependency overrided.")
    with TestClient(app) as cli:
        logging.info("Configuration -----> Client ready for running.")
        yield cli
        logging.info("Configuration -----> Client finished job.")


@pytest.fixture()
def data_test_register_user():
    return {
            "username": "test",
            "full_name": "User Test",
            "email": "test@example.com",
            "password": "!ws@test_password",
            "password_confirm": "!ws@test_password"}


@pytest.fixture()
def data_test_login():
    return {
            "username": "test",
            "password": "!ws@test_password"}


@pytest.fixture()
def data_test_update_user():
    return {
            "full_name": "User Test - update",
            "email": "test_update@example.com"}


@pytest.fixture()
def data_test_change_password():
    return {
            "old_password": "!ws@test_password",
            "new_password": "new@test_password",
            "new_password_confirm": "new@test_password"}


@pytest.fixture()
def data_test_create_post_no_file():
    return {
            "title": "sample_title",
            "content": "sample_content"}


@pytest.fixture()
def data_test_create_post_with_files():
    return {
            "title": "sample_title_with_files",
            "content": "sample_content"}


@pytest.fixture()
def data_test_update_post():
    return {
            "content": "update_content",
            "published": True}


@pytest.fixture()
def data_test_filter_show_post_positive():
    return str("?title__like=ample_&published=1")


@pytest.fixture()
def data_test_filter_show_post_negative():
    return str("?title__like=ample_&published=0")


@pytest.fixture()
def data_test_filter_find_post_positive():
    return str("?title__like=ample_&published=1&username=test")


@pytest.fixture()
def data_test_filter_find_post_negative():
    return str("?title__like=ample_&published=1&username=testowy")


@pytest.fixture()
def data_test_post_files():
    list_of_files = [
                        ("image", open("./test/image_example_1.jpg", "rb")),
                        ("image", open("./test/image_example_2.jpg", "rb"))]
    return list_of_files
