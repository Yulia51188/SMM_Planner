import os
from dotenv import load_dotenv
import vk_posting
import telegram_posting
import fb_posting
import argparse
from requests.exceptions import ConnectionError


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


def post_in_socials(text_path, image_path, vk_token, vk_group_id, vk_album_id, 
    telegram_bot_token, telegram_chat_id, fb_app_token, fb_group_id):
    is_image, image_file_error = validate_file(image_path) 
    if not is_image:
        yield f"Image {image_file_error}"
        return
    is_text, text_file_error = validate_file(text_path) 
    if not is_text:
        yield f"Text {text_file_error}"
        return
    with open(text_path) as file:
        message = file.read()
    try:
        telegram_posting.post_to_telegram(
            telegram_bot_token, 
            telegram_chat_id,              
            message,
            image_path
        ) 
        yield "Post is published in Telegram."  
    except ConnectionError as error:
        yield f"TelegramPosting error: {error}"
    except telegram_posting.TelegramPostingError as error:
        yield error 
    try:
        fb_posting.post_to_fb(
            fb_app_token, 
            fb_group_id, 
            message,
            image_path
        ) 
        yield "Post is published in FB."  
    except ConnectionError as error:
        yield f"FBPosting error: {error}"
    except fb_posting.FBPostingError as error:
        yield error
    try:
        vk_posting.post_to_vk(
            vk_token, 
            vk_album_id,
            vk_group_id,              
            message,
            image_path
        ) 
        yield "Post is published in VK."  
    except ConnectionError as error:
        yield f"VKPosting error: {error}"
    except vk_posting.VKPostingError as error:
        yield error  


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
    post_results = list(post_in_socials(
        args.text_file_path,
        args.image_file_path,
        vk_token,
        vk_group_id, 
        vk_album_id,
        telegram_bot_token, 
        telegram_chat_id, 
        fb_app_token, 
        fb_group_id
    ))
    for result in post_results:
        print(result)


if __name__=='__main__':
    main()