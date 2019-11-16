import telegram
from telegram.error import InvalidToken, TimedOut, NetworkError
from time import sleep


class TelegramPostingError(Exception):
    pass


def post_to_telegram(bot_token, chat_id, message, image_path):
    try:
        bot = telegram.Bot(token=bot_token)
        response = post_image_to_telegram(bot, chat_id, image_path)
        if not response.message_id:
            raise TelegramPostingError(f"TelegramPostingError: {response}")        
        response = post_text_to_telegram(bot, chat_id, message) 
        if not response.message_id:
            raise TelegramPostingError(f"TelegramPostingError: {response}")
    except InvalidToken as error:
        raise TelegramPostingError(f"TelegramPostingError: {error}") 
    except (NetworkError, ConnectionError) as error:
        raise TelegramPostingError(f"TelegramPostingError: {error}")


def post_text_to_telegram(bot, chat_id, message):
    try:
        return bot.send_message(chat_id=chat_id, text=message)
    except TimedOut as error:
        sleep(30)
        return bot.send_message(chat_id=chat_id, text=message)


def post_image_to_telegram(bot, chat_id, image_path):
    with open(image_path,'rb') as image_file:
        try:
            return bot.send_photo(chat_id=chat_id, photo=image_file)     
        except TimedOut as error:
            sleep(30)
            return bot.send_photo(chat_id=chat_id, photo=image_file)

