class EndpointError(Exception):
    def __init__(self, ENDPOINT):
        super().__init__(
            f'Эндпойнт {ENDPOINT} недоступен'
        )
