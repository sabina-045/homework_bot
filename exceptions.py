class MessageSendError(Exception):
    def __init__(self, message):
        super().__init__(
            f'Сообщение {message} не было отправлено'
        )

class NewStatusError(Exception):
    def __init__(self, status):
        super().__init__(
            f'Статус {status} не обновился'
        )

class EndpointError(Exception):
    def __init__(self, ENDPOINT):
        super().__init__(
            f'Эндпойнт {ENDPOINT} недоступен'
        )

class NewHomeworkAbsent(Exception):
    def __init__(self):
        super().__init__(
            f'Нет новых работ за послединий период'
        )
