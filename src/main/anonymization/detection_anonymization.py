from anonymization.base_anonymization import BaseAnonymization
from PIL import ImageFilter, Image


def find_boxes(bbox):
    nb = []
    for i in bbox:
        nb.append(i)
    return nb


class DetectionAnonymization(BaseAnonymization):
    def __init__(self):
        pass

    def blurring(self, image, response, degree=None, id=None, mask=None):
        """
        Blur the detected objects based on the user's requirements
        :param image: input image
        :param response: The response parsed from the object detection api
        :param degree: The degree of the anonymization (specified in the user_configuration file)
        :param id:
        :param mask:
        :return: The anonymized image
        """
        boxes = find_boxes(response)
        for i in boxes:
            cropped_image = image.crop((i[0], i[1], i[2], i[3]))
            blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(25*float(degree)))
            image.paste(blurred_image, (i[0], i[1], i[2], i[3]))
        return image

    def pixelating(self, image, response, degree=None, id=None, mask=None):
        """
        Pixelate the detected objects based on the user's requirements
        :param image: input image
        :param response: The response parsed from the object detection api
        :param degree: The degree of the anonymization (specified in the user_configuration file)
        :param id:
        :param mask:
        :return: The anonymized image
        """
        boxes = find_boxes(response)
        for i in boxes:
            cropped_image = image.crop((i[0], i[1], i[2], i[3]))
            w, h = cropped_image.size
            small = cropped_image.resize((int(w / (float(degree) * w)), int(h / (float(degree) * h))), Image.BILINEAR)
            result = small.resize(cropped_image.size, Image.NEAREST)
            image.paste(result, (i[0], i[1], i[2], i[3]))
        return image

    def blackening(self, image, response, degree=None, id=None, mask=None):
        """
        Blacken the detected objects based on the user's requirements
        :param image: input image
        :param response: The response parsed from the object detection api
        :param degree: The degree of the anonymization (specified in the user_configuration file)
        :param id:
        :param mask:
        :return: The anonymized image
        """
        boxes = find_boxes(response)
        for i in boxes:
            cropped = image.crop((i[0], i[1], i[2], i[3]))
            h, w = cropped.size
            black = Image.new(str(image.mode), (h, w), 'black')
            result = Image.blend(cropped, black, float(degree))
            cropped.paste(result)
            image.paste(cropped, (i[0], i[1], i[2], i[3]))
        return image
