class MessageSendError(Exception):
    def __init__(self, message):
        super().__init__(
            f'Сообщение {message} не было отправлено'
        )

class EndpointError(Exception):
    def __init__(self, ENDPOINT):
        super().__init__(
            f'Эндпойнт {ENDPOINT} недоступен'
        )
