from abc import ABC, abstractmethod


class BaseAnonymization(ABC):
    """
    Base anonymization class for the detection and the semantic anonymization
    """
    @abstractmethod
    def blurring(self, image, response, degree=None, id=None, mask=None):
        pass

    @abstractmethod
    def pixelating(self, image, response, degree=None, id=None, mask=None):
        pass

    @abstractmethod
    def blackening(self, image, response, degree=None, id=None, mask=None):
        pass
