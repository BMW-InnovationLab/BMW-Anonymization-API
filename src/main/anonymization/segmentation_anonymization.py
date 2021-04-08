from anonymization.base_anonymization import BaseAnonymization
import os
from PIL import ImageFilter, Image
import numpy as np
import cv2
import io

class SegmentationAnonymization(BaseAnonymization):
    def __init__(self):
        pass

    def blurring(self, image, response, degree=None, id=None, mask=None):
        """
        Blur the segmented objects based on the user's requirements
        :param image: input image
        :param response: The response parsed from the semantic segmentation api
        :param degree: The degree of the anonymization (specified in the user_configuration file)
        :param id: The id of the segmented class
        :param mask: The mask we will apply the anonymization on
        :return: The anonymized image
        """
        cropped = image.crop((response[0], response[1], response[2], response[3]))
        blurred = cropped.filter(ImageFilter.GaussianBlur(25 * float(degree)))
        mask = Image.open(io.BytesIO(mask.content))
        img_array = np.array(mask)
        img=Image.fromarray(img_array)
        im = img.crop((response[0], response[1], response[2], response[3]))
        rgb_image=np.array(im.convert(mode="RGB"))
        src=cv2.cvtColor( rgb_image, cv2.COLOR_RGB2BGR)
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        ex1=cv2.inRange(tmp,int(id),int(id))
        ex, alpha = cv2.threshold(ex1, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b, g, r, alpha]
        dst = cv2.merge(rgba, 4)
        test=Image.fromarray(np.array(dst))
        image.paste(blurred, (response[0], response[1], response[2], response[3]), mask=test)
        return image

    def pixelating(self, image, response, degree=None, id=None, mask=None):
        """
         Pixelate the segmented objects based on the user's requirements
         :param image: input image
         :param response: The response parsed from the semantic segmentation api
         :param degree: The degree of the anonymization (specified in the user_configuration file)
         :param id: The id of the segmented class
         :param mask: The mask we will apply the anonymization on
         :return: The anonymized image
         """
        cropped = image.crop((response[0], response[1], response[2], response[3]))
        mask = Image.open(io.BytesIO(mask.content))
        img_array = np.array(mask)
        img=Image.fromarray(img_array)
        im = img.crop((response[0], response[1], response[2], response[3]))
        rgb_image=np.array(im.convert(mode="RGB"))
        src=cv2.cvtColor( rgb_image, cv2.COLOR_RGB2BGR)
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        ex1=cv2.inRange(tmp,int(id),int(id))
        ex, alpha = cv2.threshold(ex1, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b, g, r, alpha]
        dst = cv2.merge(rgba, 4)
        test=Image.fromarray(np.array(dst))
        w, h = cropped.size
        small = cropped.resize((int(w / (float(degree) * w)), int(h / (float(degree) * h))), Image.BILINEAR)
        result = small.resize(cropped.size, Image.NEAREST)
        image.paste(result, (response[0], response[1], response[2], response[3]), mask=test)
        return image

    def blackening(self, image, response, degree=None, id=None, mask=None):
        """
         Blacken the segmented objects based on the user's requirements
         :param image: input image
         :param response: The response parsed from the semantic segmentation api
         :param degree: The degree of the anonymization (specified in the user_configuration file)
         :param id: The id of the segmented class
         :param mask: The mask we will apply the anonymization on
         :return: The anonymized image
         """
        cropped = image.crop((response[0], response[1], response[2], response[3]))
        mask = Image.open(io.BytesIO(mask.content))
        img_array = np.array(mask)
        img=Image.fromarray(img_array)
        im = img.crop((response[0], response[1], response[2], response[3]))
        rgb_image=np.array(im.convert(mode="RGB"))
        src=cv2.cvtColor( rgb_image, cv2.COLOR_RGB2BGR)
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        ex1=cv2.inRange(tmp,int(id),int(id))
        ex, alpha = cv2.threshold(ex1, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b, g, r, alpha]
        dst = cv2.merge(rgba, 4)
        test=Image.fromarray(np.array(dst))
        h, w = cropped.size
        black = Image.new(str(image.mode), (h, w), 'black')
        result = Image.blend(cropped, black, float(degree))
        cropped.paste(result)
        image.paste(cropped, (response[0], response[1], response[2], response[3]), mask=test)
        return image
