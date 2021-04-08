import os
import time
import io
import sys
import json
import requests
import jsonschema
from exceptions import InvalidUrlConfiguration, ApplicationError


class ApiClient:
    def __init__(self):
        self.configuration = []
        self.url_list = self.get_url_configuration()
        self.get_api_configuration()

    def get_configuration(self):
        try:
            return self.configuration
        except ApplicationError as e:
            raise e

    @staticmethod
    def get_url_configuration():
        """
        :return: List of all the api urls provided in the url_configuration file
        """
        with open('../jsonFiles/url_configuration.json') as f:
            data = json.load(f)
            urls = data["urls"]
            try:
                validate_url_configuration(data)
            except Exception as e:
                raise InvalidUrlConfiguration
            return urls

    def get_api_configuration(self):
        for url in self.url_list:
            self.get_models(url)

    @staticmethod
    def get_model_names(url: str):
        time.sleep(5)
        response = requests.get(
            url=url + "models")
        models_list = response.json()["data"]["models"]
        return models_list

    def get_models(self, url: str):
        """
        Returns a list of json objects representing the configuration of each api
        corresponding to each url in the url_configuration file
        :param url: Each url in the url_configuration file
        :return: List of json objects
        """
        models_list = self.get_model_names(url)
        for model_name in models_list:
            labels_list = self.get_labels(url, model_name)
            model_type = self.get_model_configuration(url, model_name)
            palette = None
            if "segmentation" in model_type:
                palette = self.get_palette(url, model_name)
            self.configuration.append({
                "name": model_name,
                "labels": labels_list,
                "type": model_type,
                "url": url,
                "palette": palette
            })

    @staticmethod
    def get_palette(url: str, model_name: str):
        response = requests.get(
            url=url + "models/" + model_name + "/palette"
        )
        return response.json()["data"]

    @staticmethod
    def get_labels(url: str, model_name: str):
        response = requests.get(
            url=url + "models/" + model_name + "/labels"
        )
        return response.json()["data"]

    @staticmethod
    def get_model_configuration(url: str, model_name: str):
        response = requests.get(
            url=url + "models/" + model_name + "/config"
        )
        return response.json()["data"]["type"]

    @staticmethod
    def get_detection_response(url: str, model_name: str, im):
        response = requests.post(
            url=url + "models/" + model_name + "/predict",
            files={'input_data': io.BytesIO(im.tobytes())})
        return response.json()

    @staticmethod
    def get_segmentation_response(url: str, model_name: str, im):
        response = requests.post(
            url=url + "models/" + model_name + "/inference",
            files={'input_data': io.BytesIO(im.tobytes())}
        )
        return response


def validate_url_configuration(data):
    """
    Validate the url_configuration file by comparing it to the urlConfigurationSchema
    :param data: The data from the url_configuration file
    """
    with open('urlConfigurationSchema') as f:
        schema = json.load(f)
    try:
        jsonschema.validate(data, schema)
    except Exception as e:
        raise InvalidUrlConfiguration(e)
