import os


# Tests for user


def test_register_user(client_test, data_test_register_user):
    response = client_test.post('/admin/register/', json=data_test_register_user)
    response_json = response.json()
    assert response.status_code == 201
    assert response_json["username"] == "test"
    assert response_json["full_name"] == "User Test"
    assert response_json["email"] == "test@example.com"
    assert response_json["is_active"] == True


def test_login(client_test, data_test_login):
    response = client_test.post('/admin/login/', data=data_test_login)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None
    os.environ["BEARER_TOKEN"] = access_token
    os.environ["REFRESH_TOKEN"] = refresh_token


def test_update_user(client_test, data_test_update_user):
    response = client_test.put('/admin/update/', json=data_test_update_user, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["full_name"] == "User Test - update"
    assert response_json["email"] == "test_update@example.com"


def test_change_password(client_test, data_test_change_password):
    response = client_test.put('/admin/change_password/', json=data_test_change_password, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert response_json == {'message': 'Password changed successfully.'}

def test_refresh(client_test):
    response = client_test.post('/admin/refresh/', headers={"Authorization": f'Bearer {os.environ["REFRESH_TOKEN"]}'})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    assert access_token is not None
    os.environ["BEARER_TOKEN"] = access_token


# Tests for blog


def test_create_post(client_test, data_test_create_post):
    response = client_test.post('/blog/create_post/', json=data_test_create_post, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 201
    assert response_json["title"] == "sample_title"
    assert response_json["content"] == "sample_content"
    assert response_json["published"] == False
    assert response_json["created_at"] is not None
    assert response_json["users"] is not None
    os.environ["POST_ID"] = str(response_json["id"])


def test_update_post(client_test, data_test_update_post):
    post_id = os.environ['POST_ID']
    response = client_test.put(f'/blog/update_post/{post_id}/', json=data_test_update_post, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["content"] == "update_content"
    assert response_json["published"] == True


def test_show_my_posts(client_test):
    response = client_test.get('/blog/show_my_posts/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert len(response_json) == 1


def test_delete_post(client_test):
    post_id = os.environ['POST_ID']
    response = client_test.delete(f'/blog/delete_post/{post_id}/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert response_json == {'message': 'Post deleted successfully.'}


# Deletion of test user
def test_delete_user(client_test):
    response = client_test.delete('/admin/delete/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    assert response.status_code == 200
    assert response_json == {'message': 'User deleted successfully.'}
