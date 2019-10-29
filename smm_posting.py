import os
from dotenv import load_dotenv
import vk_posting
import telegram_posting
import fb_posting
import argparse
from requests.exceptions import ConnectionError

class PostingError(Exception):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='The script publishes post with image to social media'
    )
    parser.add_argument(
        'text_file_path',
        type=str,
        help='File path of a text file'
    )    
    parser.add_argument(
        'image_file_path',
        type=str,
        help='File path of an image file'
    )         
    return parser.parse_args()


def validate_file(file_path):
    if not os.path.isfile(file_path):
        return (False, "file doesn't exists")
    try:
        file_obj = open(file_path,'rb')
        file_obj.close()
        return (True, None)
    except(OSError, IOError) as error:
        return (False, "File can't be open")   


def post_in_socials(text_path, image_path, is_vk, is_telegram, is_fb,
    vk_token, vk_group_id, vk_album_id, telegram_bot_token, telegram_chat_id, 
    fb_app_token, fb_group_id):
    is_image, image_file_error = validate_file(image_path) 
    if not is_image:
        return f"Image {image_file_error}"
    is_text, text_file_error = validate_file(text_path) 
    if not is_text:
        return f"Text {text_file_error}"
    with open(text_path) as file:
        message = file.read()
    if is_telegram:
        try:
            telegram_posting.post_to_telegram(
                telegram_bot_token, 
                telegram_chat_id,              
                message,
                image_path
            )  
        except ConnectionError as error:
            return f"TelegramPosting error: {error}"
        except telegram_posting.TelegramPostingError as error:
            return error 
    if is_fb:
        try:
            fb_posting.post_to_fb(
                fb_app_token, 
                fb_group_id, 
                message,
                image_path
            ) 
        except ConnectionError as error:
            return f"FBPosting error: {error}"
        except fb_posting.FBPostingError as error:
            return error
    if is_vk:    
        try:
            vk_posting.post_to_vk(
                vk_token, 
                vk_album_id,
                vk_group_id,              
                message,
                image_path
            ) 
        except ConnectionError as error:
            return f"VKPosting error: {error}"
        except vk_posting.VKPostingError as error:
            return error  


def main():
    args = parse_arguments()
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")
    vk_album_id = os.getenv("VK_ALBUM_ID")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
    fb_app_token = os.getenv("FB_APP_TOKEN")
    fb_group_id = os.getenv("FB_GROUP_ID")
    is_vk = True 
    is_telegram = True  
    is_fb = True 
    post_error = post_in_socials(
        args.text_file_path,
        args.image_file_path,
        is_vk, 
        is_telegram, 
        is_fb,
        vk_token,
        vk_group_id, 
        vk_album_id,
        telegram_bot_token, 
        telegram_chat_id, 
        fb_app_token, 
        fb_group_id
    )
    if post_error: 
        print(post_error)
    else:
        print('Post is published successfully')


if __name__=='__main__':
    main()