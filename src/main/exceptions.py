__metaclass__ = type


class ApplicationError(Exception):
    """Base class for other exceptions"""

    def __init__(self, default_message, additional_message=''):
        self.default_message = default_message
        self.additional_message = additional_message

    def __str__(self):
        return self.get_message()

    def get_message(self):
        return self.default_message if self.additional_message == '' else "{}: {}".format(self.default_message,
                                                                                          self.additional_message)


class InvalidModelConfiguration(ApplicationError):
    """Raised when the model's configuration is corrupted"""

    def __init__(self, additional_message=''):
        super().__init__('Invalid model configuration', additional_message)


class InvalidInputData(ApplicationError):
    """Raised when the input data is corrupted"""

    def __init__(self, additional_message=''):
        super().__init__('Invalid input data', additional_message)


class InvalidUrlConfiguration(ApplicationError):
    """Raised when the model's configuration is corrupted"""

    def __init__(self, additional_message=''):
        super().__init__('Invalid url configuration', additional_message)