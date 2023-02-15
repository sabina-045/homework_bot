import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (EndpointError, MessageSendError, NewHomeworkAbsent,
                        NewStatusError)

logging.basicConfig(
    handlers=[logging.FileHandler('program.log', 'w', 'utf-8')],
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Доступность переменных окружения."""
    variables = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for variable in variables:
        try:
            if variable:
                return True
        except KeyError:
            logging.error(f'Ошибка ключа: {variable}')
            return False


def send_message(bot, message):
    """Сообщение в чат о статусе домашней работы."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Сообщение {message} успешно отправлено')
    except Exception as error:
        logging.error(f'{error}')
        raise MessageSendError


def get_api_answer(timestamp):
    """Запрос к API."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        if response.status_code != 200:
            logging.error(f'Нет доступа к {ENDPOINT}, {response.status_code}')
            raise EndpointError
    except Exception as error:
        logging.error(f'Сбой при запросе к API: {error}')
        raise EndpointError
    return response.json()


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        raise TypeError
    if 'homeworks' not in response:
        raise KeyError
    if 'current_date' not in response:
        raise KeyError
    if not isinstance(response['homeworks'], list):
        raise TypeError
    if len(response['homeworks']) == 0:
        raise IndexError
    return response['homeworks'][0]


def parse_status(homework):
    """Получение информации о статусе домашней работы."""
    old_status = ''
    if not homework.get('homework_name'):
        logging.error('В ответе API нет ключа homework_name')
        raise KeyError
    homework_name = homework.get('homework_name')
    if not homework.get('homework_name'):
        logging.error('В ответе API нет ключа status')
        raise KeyError
    status = homework.get('status')
    if status == old_status:
        logging.debug(f'Статус {status} не обновился')
        raise NewStatusError
    old_status = status
    try:
        verdict = HOMEWORK_VERDICTS[status]
        logging.info(f'{status} совпал с ключом HOMEWORK_VERDICTS')
    except KeyError:
        logging.error(f'{status} не совпал с ключом HOMEWORK_VERDICTS')
    logging.info(f'Изменился статус проверки работы'
                 f'"{homework_name}". {verdict}')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():   # noqa: C901
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_message = ''
    error_message_old = ''
    while True:
        if not check_tokens():
            logging.critical('Отсутствует переменная окружения')
            break
        try:
            response = get_api_answer(timestamp)
            timestamp = int(response.get('current_date'))
            try:
                homework = check_response(response)
            except IndexError:
                raise NewHomeworkAbsent
            try:
                message = parse_status(homework)
                if message != old_message:
                    send_message(bot, message)
                    old_message = message
            except Exception:
                raise NewStatusError

        except Exception as error:
            message = f'Программа молчит по причине: {error}'
            logging.error(f'В работе программы сбой, ошибка: {error}')
            if message != error_message_old:
                error_message_old = message
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                logging.info(f'Сообщение об ошибке {error} отправлено в чат')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
