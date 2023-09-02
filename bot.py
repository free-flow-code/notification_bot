import time
import requests
import telegram
import textwrap as tw
from environs import Env
import logging

logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.user_id)


def listen_devman_server(token):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {token}'}
    params = {}
    while True:
        try_connection = 0
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            message = response.json()
            if message['status'] == 'timeout':
                params = {'timestamp': message['timestamp_to_request']}
            elif message['status'] == 'found':
                params = {'timestamp': message['last_attempt_timestamp']}
                yield message
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            if not try_connection:
                time.sleep(3)
            else:
                time.sleep(5)
            try_connection += 1
            continue


def main():
    env = Env()
    env.read_env()
    tg_token = env.str('TG_TOKEN')
    user_id = env.str('TG_USER_ID')
    devman_token = env.str('DEVMAN_TOKEN')

    bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(bot, user_id))
    logging.info('Бот запущен')

    while True:
        try:
            review_message = listen_devman_server(devman_token)
            for message in review_message:
                if message['new_attempts'][0]['is_negative']:
                    text = f'''\
                    Работа "{message["new_attempts"][0]["lesson_title"]}" вернулась с проверки.
                    К сожалению в ней нашлись ошибки.
                    Ссылка: {message["new_attempts"][0]["lesson_url"]}.
                    '''
                else:
                    text = f'''\
                    Работа "{message["new_attempts"][0]["lesson_title"]}" вернулась с проверки.
                    Преподавателю все понравилось, можно приступать к следующему уроку!
                    '''
                bot.send_message(text=tw.dedent(text), chat_id=user_id)
        except Exception as err:
            logger.exception(err)


if __name__ == '__main__':
    main()
