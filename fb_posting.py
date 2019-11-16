import requests 
import os


class FBPostingError(Exception):
    pass


def post_to_fb(token, group_id, message, image_path):
    try:
        response = post_photo_and_text_to_fb(
            token, 
            group_id, 
            message, 
            image_path
        )
    except ConnectionError as error:
        raise FBPostingError(error)
    if not response.ok or 'id' not in response.json().keys():
        raise FBPostingError(response.json())
    

def post_photo_and_text_to_fb(token, group_id, message, image_path):
    url_photo_template = 'https://graph.facebook.com/{page_id}/photos'
    with open(image_path,'rb') as image_file:
        response = requests.post(
            url_photo_template.format(page_id = group_id),
            files = {
                'files': image_file,
            },
            data = {
                'caption': message,
                'access_token': token
            }
        )
    return response