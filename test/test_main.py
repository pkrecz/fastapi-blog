import os
import logging


# Subtests for user
def sub_test_register_user(client_test, data_test_register_user):
    response = client_test.post('/admin/register/', json=data_test_register_user)
    response_json = response.json()
    logging.info('Register user testing ...')
    assert response.status_code == 201
    assert response_json["username"] == "test"
    assert response_json["full_name"] == "User Test"
    assert response_json["email"] == "test@example.com"
    assert response_json["is_active"] == True
    logging.info('Register user testing finished.')

def sub_test_login(client_test, data_test_login):
    response = client_test.post('/admin/login/', data=data_test_login)
    response_json = response.json()
    logging.info('Login user testing ...')
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    assert response_json["refresh_token"] is not None
    logging.info('Login user testing finished.')
    os.environ["BEARER_TOKEN"] = response_json["access_token"]
    os.environ["REFRESH_TOKEN"] = response_json["refresh_token"]

def sub_test_update_user(client_test, data_test_update_user):
    response = client_test.put('/admin/update/', json=data_test_update_user, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Update user testing ...')
    assert response.status_code == 200
    assert response_json["full_name"] == "User Test - update"
    assert response_json["email"] == "test_update@example.com"
    logging.info('Update user testing finished.')

def sub_test_change_password(client_test, data_test_change_password):
    response = client_test.put('/admin/change_password/', json=data_test_change_password, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Changing password testing ...')
    assert response.status_code == 200
    assert response_json == {'message': 'Password changed successfully.'}
    logging.info('Changing password testing finished.')

def sub_test_refresh(client_test):
    response = client_test.post('/admin/refresh/', headers={"Authorization": f'Bearer {os.environ["REFRESH_TOKEN"]}'})
    response_json = response.json()
    logging.info('Refresh token testing ...')
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    logging.info('Refresh token testing finished.')
    os.environ["BEARER_TOKEN"] = response_json["access_token"]


# Subtests for blog
def sub_test_create_post(client_test, data_test_create_post):
    response = client_test.post('/blog/create_post/', json=data_test_create_post, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Creating post testing ...')
    assert response.status_code == 201
    assert response_json["title"] == "sample_title"
    assert response_json["content"] == "sample_content"
    assert response_json["published"] == False
    assert response_json["created_at"] is not None
    assert response_json["users"] is not None
    logging.info('Creating post testing finished.')
    os.environ["POST_ID"] = str(response_json["id"])

def sub_test_update_post(client_test, data_test_update_post):
    post_id = os.environ['POST_ID']
    response = client_test.put(f'/blog/update_post/{post_id}/', json=data_test_update_post, headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Updating post testing ...')
    assert response.status_code == 200
    assert response_json["content"] == "update_content"
    assert response_json["published"] == True
    logging.info('Updating post testing finished.')

def sub_test_show_my_posts(client_test):
    response = client_test.get('/blog/show_my_posts/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Show my posts testing ...')
    assert response.status_code == 200
    assert len(response_json) == 1
    logging.info('Show my posts testing finished.')

def sub_test_delete_post(client_test):
    post_id = os.environ['POST_ID']
    response = client_test.delete(f'/blog/delete_post/{post_id}/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Deletion post testing ...')
    assert response.status_code == 200
    assert response_json == {'message': 'Post deleted successfully.'}
    logging.info('Deletion post testing finished.')

def sub_test_delete_user(client_test):
    response = client_test.delete('/admin/delete/', headers={"Authorization": f'Bearer {os.environ["BEARER_TOKEN"]}'})
    response_json = response.json()
    logging.info('Deletion user testing ...')
    assert response.status_code == 200
    assert response_json == {'message': 'User deleted successfully.'}
    logging.info('Deletion user testing finished.')


# Test to be performed
def test_user(
                client_test,
                data_test_register_user,
                data_test_login,
                data_test_update_user,
                data_test_change_password):

    logging.info('START - testing user')
    sub_test_register_user(client_test, data_test_register_user)
    sub_test_login(client_test, data_test_login)
    sub_test_update_user(client_test, data_test_update_user)
    sub_test_change_password(client_test, data_test_change_password)
    sub_test_refresh(client_test)
    logging.info('STOP - testing user')

def test_blog(
                client_test,
                data_test_create_post,
                data_test_update_post):

    logging.info('START - testing blog')
    sub_test_create_post(client_test, data_test_create_post)
    sub_test_update_post(client_test,data_test_update_post)
    sub_test_show_my_posts(client_test)
    sub_test_delete_post(client_test)
    sub_test_delete_user(client_test)
    logging.info('STOP - testing blog')
