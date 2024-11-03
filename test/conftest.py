import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from config.database import engine, get_db 
from main import app


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Preparing test envoirment
@pytest.fixture(scope='session')
def db_test():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='session')
def client_test(db_test):

    def override_get_db():
        try:
            yield db_test
        finally:
            db_test.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client_test:
        yield client_test


# Preparing sample data
@pytest.fixture
def data_test_register_user():
    return {
            "username": "test",
            "full_name": "User Test",
            "email": "test@example.com",
            "password": "!ws@test_password",
            "password_confirm": "!ws@test_password"}

@pytest.fixture
def data_test_login():
    return {
            "username": "test",
            "password": "!ws@test_password"}

@pytest.fixture
def data_test_update_user():
    return {
            "full_name": "User Test - update",
            "email": "test_update@example.com"}

@pytest.fixture
def data_test_change_password():
    return {
            "old_password": "!ws@test_password",
            "new_password": "new@test_password",
            "new_password_confirm": "new@test_password"}

@pytest.fixture
def data_test_create_post():
    return {
            "title": "sample_title",
            "content": "sample_content"}

@pytest.fixture
def data_test_update_post():
    return {
            "content": "update_content",
            "published": True}
