import os
import logging
from config.settings import settings

list_of_files_to_be_deleted = []


def sub_test_register_user(
                                client,
                                data_test_register_user):
    response = client.post(
                                url="/admin/register/",
                                json=data_test_register_user)
    response_json = response.json()
    logging.info("Register user testing ...")
    assert response.status_code == 201
    assert response_json["username"] == data_test_register_user["username"]
    assert response_json["full_name"] == data_test_register_user["full_name"]
    assert response_json["email"] == data_test_register_user["email"]
    assert response_json["is_active"] == True
    logging.info("Register user testing finished.")


def sub_test_login(
                                client,
                                data_test_login):
    response = client.post(
                                url="/admin/login/",
                                data=data_test_login)
    response_json = response.json()
    logging.info("Login user testing ...")
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    assert response_json["refresh_token"] is not None
    logging.info('Login user testing finished.')
    os.environ["BEARER_TOKEN"] = response_json["access_token"]
    os.environ["REFRESH_TOKEN"] = response_json["refresh_token"]


def sub_test_update_user(
                                client,
                                data_test_update_user):
    response = client.put(
                                url="/admin/update/",
                                json=data_test_update_user,
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Update user testing ...")
    assert response.status_code == 200
    assert response_json["full_name"] == data_test_update_user["full_name"]
    assert response_json["email"] == data_test_update_user["email"]
    logging.info("Update user testing finished.")


def sub_test_change_password(
                                client,
                                data_test_change_password):
    response = client.put(
                                url="/admin/change_password/",
                                json=data_test_change_password,
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Changing password testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "Password changed successfully."}
    logging.info("Changing password testing finished.")


def sub_test_refresh(client):
    response = client.post(
                                url="/admin/refresh/",
                                headers={"Authorization": f"Bearer {os.environ["REFRESH_TOKEN"]}"})
    response_json = response.json()
    logging.info("Refresh token testing ...")
    assert response.status_code == 200
    assert response_json["access_token"] is not None
    logging.info("Refresh token testing finished.")
    os.environ["BEARER_TOKEN"] = response_json["access_token"]


def sub_test_create_post_no_file(
                                client,
                                data_test_create_post_no_file):
    response = client.post(
                                url="/blog/create_post/",
                                data=data_test_create_post_no_file,
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Creating post testing ...")
    assert response.status_code == 201
    assert response_json["title"] == data_test_create_post_no_file["title"]
    assert response_json["content"] == data_test_create_post_no_file["content"]
    assert response_json["published"] == False
    assert response_json["created_at"] is not None
    assert response_json["users"] is not None
    logging.info("Creating post testing finished.")
    os.environ["POST_ID"] = str(response_json["id"])


def sub_test_create_post_with_files(
                                client,
                                data_test_create_post_with_files,
                                data_test_post_files):
    response = client.post(
                                url="/blog/create_post/",
                                data=data_test_create_post_with_files,
                                files=data_test_post_files,
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Creating post with files testing ...")
    assert response.status_code == 201
    assert response_json["title"] == data_test_create_post_with_files["title"]
    assert len(response_json["images"]) == 2
    logging.info("Creating post with files testing finished.")
    os.environ["FILE_NAME"] = str(response_json["images"][1]["filename"])
    for i in range(2):
        list_of_files_to_be_deleted.append(str(response_json["images"][i]["filename"]))


def sub_test_update_post(
                                client,
                                data_test_update_post):
    post_id = os.environ["POST_ID"]
    response = client.put(
                                url=f"/blog/update_post/{post_id}/",
                                json=data_test_update_post,
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Updating post testing ...")
    assert response.status_code == 200
    assert response_json["content"] == data_test_update_post["content"]
    assert response_json["published"] == data_test_update_post["published"]
    logging.info("Updating post testing finished.")


def sub_test_show_my_posts_positive(
                                client,
                                data_test_filter_post):
    response = client.get(
                                url=f"/blog/show_my_posts/{data_test_filter_post}",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    logging.info("Show my posts positive testing ...")
    assert response.status_code == 200
    logging.info("Show my posts positive testing finished.")


def sub_test_show_my_posts_negative(
                                client,
                                data_test_filter_post):
    response = client.get(
                                url=f"/blog/show_my_posts/{data_test_filter_post}",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Show my posts negative testing ...")
    assert response.status_code == 404
    assert response_json == {"detail": "You do not have any post."}
    logging.info("Show my posts negative testing finished.")


def sub_test_find_post_positive(
                                client,
                                data_test_filter_post):
    response = client.get(
                                url=f"/blog/find_post/{data_test_filter_post}",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    logging.info("Find post positive testing ...")
    assert response.status_code == 200
    logging.info("Find post positive testing finished.")


def sub_test_find_post_negative(
                                client,
                                data_test_filter_post):
    response = client.get(
                                url=f"/blog/find_post/{data_test_filter_post}",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Find post negative testing ...")
    assert response.status_code == 404
    assert response_json == {"detail": "Expected post was not found."}
    logging.info("Find post negative testing finished.")


def sub_test_delete_post(client):
    post_id = os.environ["POST_ID"]
    response = client.delete(
                                url=f"/blog/delete_post/{post_id}/",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Deletion post testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "Post deleted successfully."}
    logging.info("Deletion post testing finished.")


def sub_test_delete_user(client):
    response = client.delete(
                                url="/admin/delete/",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    response_json = response.json()
    logging.info("Deletion user testing ...")
    assert response.status_code == 200
    assert response_json == {"message": "User deleted successfully."}
    logging.info("Deletion user testing finished.")


def sub_test_download_file(client):
    file_name = os.environ["FILE_NAME"]
    response = client.get(
                                url=f"/blog/download_file/{file_name}/",
                                headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"})
    logging.info("Download file testing ...")
    assert response.status_code == 200
    assert int(response.headers["content-length"]) != 0
    logging.info("Download file testing finished.")


def sub_test_delete_media_files():
    logging.info("Deletion media files testing ...")
    for file in list_of_files_to_be_deleted:
        file_path = os.path.join(settings.MEDIA_ROOT, file)
        assert os.path.exists(file_path) == True
        if os.path.exists(file_path):
            os.remove(file_path)
    logging.info("Deletion media files testing finished.")


def test_user(
                client,
                data_test_register_user,
                data_test_login,
                data_test_update_user,
                data_test_change_password):

    logging.info("START - testing user")
    sub_test_register_user(client, data_test_register_user)
    sub_test_login(client, data_test_login)
    sub_test_update_user(client, data_test_update_user)
    sub_test_change_password(client, data_test_change_password)
    sub_test_refresh(client)
    logging.info("STOP - testing user")


def test_blog(
                client,
                data_test_create_post_no_file,
                data_test_update_post,
                data_test_filter_show_post_positive,
                data_test_filter_show_post_negative,
                data_test_filter_find_post_positive,
                data_test_filter_find_post_negative):

    logging.info("START - testing blog")
    sub_test_create_post_no_file(client, data_test_create_post_no_file)
    sub_test_update_post(client,data_test_update_post)
    sub_test_show_my_posts_positive(client, data_test_filter_show_post_positive)
    sub_test_show_my_posts_negative(client, data_test_filter_show_post_negative)
    sub_test_find_post_positive(client, data_test_filter_find_post_positive)
    sub_test_find_post_negative(client, data_test_filter_find_post_negative)
    sub_test_delete_post(client)
    sub_test_delete_user(client)
    logging.info("STOP - testing blog")


def test_file_operation(
                        client,
                        data_test_register_user,
                        data_test_login,
                        data_test_create_post_with_files,
                        data_test_post_files):

    logging.info("START - testing file operation")
    sub_test_register_user(client, data_test_register_user)
    sub_test_login(client, data_test_login)
    sub_test_create_post_with_files(client, data_test_create_post_with_files, data_test_post_files)
    sub_test_download_file(client)
    sub_test_delete_media_files()
    logging.info("STOP - testing file operation")
