import time
import requests
import telegram
import textwrap as tw
from environs import Env
import logging


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
    logging.basicConfig(level=logging.DEBUG)
    env = Env()
    env.read_env()
    user_id = env.str('TG_USER_ID')
    tg_token = env.str('TG_TOKEN')
    devman_token = env.str('DEVMAN_TOKEN')

    bot = telegram.Bot(token=tg_token)
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


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        logging.exception(err)
