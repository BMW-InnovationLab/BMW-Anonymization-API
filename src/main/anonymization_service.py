import io
import os
import cv2
import sys
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import datetime
from APIClient import ApiClient
from fastapi import File, UploadFile
from exceptions import ApplicationError, InvalidInputData
from strategy_context import StrategyContext
from helpers import get_user_models
import helpers
import moviepy.editor

sys.path.append("anonymization")


class AnonymizationService:

    def __init__(self):
        self.strategy_context = StrategyContext()

    def anonymize(self, image: UploadFile = File(...), configuration: UploadFile = File(...)):
        """
        Calls the correct anonymization method based on the model type and the technique
        :param image: Input image
        :param configuration: user configuration file
        :return: File response representing the anonymized image
        """
        result = None
        im = Image.open(image.file).convert('RGB')
        rgb_image_0 = np.array(im)
        bgr_image_0 = cv2.cvtColor(rgb_image_0, cv2.COLOR_RGB2BGR)
        response = []
        configuration_path = '../jsonFiles/user_configuration.json'

        with open(configuration_path, 'wb') as config:
            config.write(configuration.file.read())
        try:
            users_models = get_user_models(configuration_path)
        except ApplicationError as e:
            raise e
        _, im_png = cv2.imencode(".png", bgr_image_0)
        errors = []
        i = 0
        for each in users_models:
            i = i + 1
            try:
                response, mask = getattr(helpers, "parse_" + each["model_type"] + "_response")(each, im_png, i, errors)
            except Exception as e:
                errors.append(
                    "The model type <" + each["model_type"] + "> in sensitive info <" + str(i) + "> is not supported.")
            if response:
                if not errors:
                    for r in response:
                        inference_type = r['type']
                        technique = r['technique']
                        box = r['boxes']
                        degree = r['degree']
                        label_id = r['label_id']
                        anonymization_name = inference_type + "_anonymization"
                        anonymization_class = anonymization_name.title().replace("_", "")
                        try:
                            result = self.strategy_context.anonymize(
                                getattr(__import__(anonymization_name), anonymization_class)(),
                                technique=technique, image=im, response=box,
                                degree=degree, label_id=label_id, mask=mask)
                        except ApplicationError as e:
                            raise e
                    rgb_image = np.array(result)
                    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
                else:
                    bgr_image = None
            else:
                rgb_image = np.array(im)
                bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        return bgr_image, errors

    def anonymize_video(self, video: UploadFile = File(...), configuration: UploadFile = File(...)):
        result = None
        configuration_path = '../jsonFiles/user_configuration.json'
        with open(configuration_path, 'wb') as config:
            config.write(configuration.file.read())
        try:
            users_models = get_user_models(configuration_path)
        except ApplicationError as e:
            raise e
        response = []
        with open('video.mp4', 'wb') as v:
            try:
                v.write(video.file.read())
            except Exception as e:
                raise InvalidInputData(e)
            initial_video = moviepy.editor.VideoFileClip("video.mp4")
            initial_video_audio = initial_video.audio
            cap = cv2.VideoCapture('video.mp4')
            fps = cap.get(cv2.CAP_PROP_FPS)
            i = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if ret is True:
                    im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(im)
                    bgr_image_0 = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
                    _, im_png = cv2.imencode(".png", bgr_image_0)
                    path = os.getcwd() + "/frames/" + str(i) + ".jpg"
                    i = i + 1
                    errors = []
                    n = 0
                    for each in users_models:
                        n = n + 1
                        result = None
                        try:
                            response, mask = getattr(helpers, "parse_" + each["model_type"] + "_response")(each, im_png,
                                                                                                           n, errors)
                        except Exception as e:
                            errors.append("The model type <" + each["model_type"] + "> in sensitive info <" + str(
                                n) + "> is not supported.")
                        if response:
                            if not errors:
                                for r in response:
                                    inference_type = r['type']
                                    technique = r['technique']
                                    box = r['boxes']
                                    degree = r['degree']
                                    label_id = r['label_id']
                                    anonymization_name = inference_type + "_anonymization"
                                    anonymization_class = anonymization_name.title().replace("_", "")
                                    try:
                                        result = self.strategy_context.anonymize(
                                            getattr(__import__(anonymization_name), anonymization_class)(),
                                            technique=technique, image=img, response=box,
                                            degree=degree, label_id=label_id, mask=mask)
                                    except ApplicationError as e:
                                        raise e
                                result.save(path)
                            else:
                                return errors
                        else:
                            img.save(path)
                else:
                    break
            print("Processing ...")
            images = [img for img in os.listdir(os.getcwd() + "/frames") if img.endswith(".jpg")]
            sort = []
            for frame in images:
                name = frame.split(".")[0]
                image_number = int(name)
                sort.append(image_number)
            sort = sorted(sort)
            frame = cv2.imread(os.path.join(os.getcwd() + "/frames", str(sort[0]) + ".jpg"))
            height, width, layers = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
            output_video_dir = "Anonymized_" + video.filename.split(".")[0] + "_" + datetime.now().strftime(
                "%d_%m_%y_%H_%M_%S")
            video = cv2.VideoWriter('anonymized_video/' + output_video_dir + '.mp4', fourcc, fps, (width, height))
            for image in sort:
                video.write(cv2.imread(os.path.join(os.getcwd() + "/frames", str(image) + ".jpg")))
                os.remove(os.getcwd() + "/frames/" + str(image) + ".jpg")
            cv2.destroyAllWindows()
            video.release()
            anonymized_video = moviepy.editor.VideoFileClip('anonymized_video/' + output_video_dir + '.mp4')
            anonymized_video.audio = initial_video_audio
            os.remove('anonymized_video/' + output_video_dir + '.mp4')
            anonymized_video.write_videofile('anonymized_video/' + output_video_dir + '.mp4')
            os.remove(os.getcwd() + "/video.mp4")
            return "Done"
