## Бот для проверки статуса урока на Devman

Скрипт запускает телеграм бота и с помощью [API Devman](https://dvmn.org/api/docs/)
отслеживает изменение статуса урока. Когда урок будет возвращен с проверки,
бот отправит соответствующее сообщение в телеграм, в зависимости от того,
принят урок или нет.

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Создайте телеграм бота с помощью [BotFather](https://t.me/BotFather), который выдаст
вам токен вида:

`5798143041:AXGbv_HjqQijxGjk4zbYBe5u8GiJhyDtAsd`

Токен Devman можно получить по [ссылке](https://dvmn.org/api/docs/).

Затем в директории с программой создайте `.env` файл:

```
TG_USER_ID='you telegran id'
TG_TOKEN='you bot token'
DEVMAN_TOKEN='you devman token'
```
Запустите скрипт командой:

```
python bot.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).