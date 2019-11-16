import vk_api
from requests.exceptions import ConnectionError
import os


class VKPostingError(Exception):
    pass


def post_to_vk(vk_token, album_id, group_id, message='', image_path=None,):
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()      
    try:
        photo_upload_error, attachments = get_attachments(
            vk_session, 
            album_id, 
            group_id, 
            image_path
        )
        if photo_upload_error:
            raise VKPostingError("VKPostingError while uploading photo: "
                f"{photo_upload_error}")
    except vk_api.exceptions.ApiError as error:
        raise VKPostingError(f"VKPostingError while uploading photo: {error}")
    try:
        response = post_message_to_vk(vk, group_id, message, attachments)
        if not "post_id" in response.keys():
            raise VKPostingError(f"VKPostingError while posting: {response}")
    except ConnectionError as error:
        raise VKPostingError(f"VKPostingError while posting: {error}")


def get_attachments(vk_session, album_id, group_id, image_path):
    upload = vk_api.VkUpload(vk_session)
    photo_upload_result = upload.photo(  
        image_path,
        album_id=album_id,
        group_id=group_id
    )
    if not 'id' in photo_upload_result[0]: 
        return (True, photo_upload_result)
    owner_id = photo_upload_result[0]['owner_id']
    photo_id = photo_upload_result[0]['id']
    return (False, f"photo{owner_id}_{photo_id}")


def post_message_to_vk(vk_obj, group_id, message, attachments=None):
    return vk_obj.wall.post(
        owner_id=f'-{group_id}', 
        message=message, 
        attachments=attachments,
    )

    