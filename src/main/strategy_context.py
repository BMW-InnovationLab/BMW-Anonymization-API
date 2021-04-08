from anonymization.base_anonymization import BaseAnonymization


class StrategyContext:
    def __init__(self):
        pass

    def anonymize(self, detection_type: BaseAnonymization, technique: str, image, response, degree,label_id, mask):
        """
        :param detection_type: Either it is semantic segmentation or object detection
        :param technique: The anonymization method
        :param image: Input image
        :param response: The bounding boxes taken from the output of the inference api
        :param degree: The degree used to specify the opacity of the anonymization
        :param label_id: The id of the detected class
        :param mask: The mask used to apply the anonymzation
        :return:
        """
        return getattr(detection_type, technique)(image, response, degree, label_id, mask)
