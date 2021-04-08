class CommonLabels:
    def __init__(self):
        self.blackening = None
        self.pixelating = None
        self.blurring = None

    def get_labels(self, label_name):
        methods = []
        for key, value in self.__dict__.items():
            methods.append(key)
        return methods
