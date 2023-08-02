import time
import requests
import telegram
from environs import Env


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
        except requests.exceptions.ConnectionError as err:
            print(err)
            if not try_connection:
                time.sleep(3)
            else:
                time.sleep(5)
            try_connection += 1
            continue


def main():
    env = Env()
    env.read_env()
    user_id = env.str('TG_USER_ID')
    tg_token = env.str('TG_TOKEN')
    devman_token = env.str('DEVMAN_TOKEN')

    bot = telegram.Bot(token=tg_token)
    response = listen_devman_server(devman_token)

    for message in response:
        if message['new_attempts'][0]['is_negative']:
            text = f'Работа {message["new_attempts"][0]["lesson_title"]} вернулась с проверки\n\n'\
                   f'К сожалению в ней нашлись ошибки.\n{message["new_attempts"][0]["lesson_url"]}.'
        else:
            text = f'Работа {message["new_attempts"][0]["lesson_title"]} вернулась с проверки\n\n' \
                   f'Преподавателю все понравилось, можно приступать к следующему уроку!'
        bot.send_message(text=text, chat_id=user_id)


if __name__ == '__main__':
    main()
