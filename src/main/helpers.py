import io
import cv2
import json
import config
import requests
import jsonschema
import numpy as np
from PIL import Image
from APIClient import ApiClient
from labels import labels_methods
from exceptions import ApplicationError, InvalidModelConfiguration

# master_dict = labels_methods()
master_dict = config.master_dict


def get_user_models(configuration_path):
    """ Returns a list of json objects that represent the sensitive info given by the user in
    the configuration file
    :param configuration_path: The user configuration path
    :return: List of json objects
    """
    user_models = []
    with open(configuration_path) as f:
        try:
            data = json.load(f)
        except Exception:
            raise InvalidModelConfiguration("Json file corrupted")
    try:
        validate_json_configuration(data)
    except ApplicationError as e:
        raise e
    for info in data['sensitive_info']:
        url = info.get('url')
        models = {
            'url': url,
            'model_name': info['model_name'],
            'label_name': info['class_name'],
            'model_type': info['inference_type'].casefold(),
            'technique': info['anonymization_technique'].casefold(),
            'degree': info['anonymization_degree']
        }
        user_models.append(models)
    return user_models


def parse_inference_response(inference_type, user_config, im, i, errors):
    """ Either returns the response from the inference api or returns an array with the user's configuration file errors
    :param inference_type: i.e detection
    :param user_config: a json object that represent each sensitive info specified by the user
    :param im: the image object that we need to anonymize
    :param i: the index of the sensitive info that we are using
    :param errors: a list that will be filled in case any error in the user's configuration file is present
    :return: inference api response or the list of errors
    """
    master_dict = config.master_dict
    # getting all the supported labels
    labels = list(master_dict.keys())
    # checking if the user's requested label is present in the supported ones
    if user_config["label_name"] in labels:
        # checking if the user's label is supported by the user's specified model type
        if inference_type in master_dict[user_config["label_name"]].keys():
            # getting the urls and the models that supports the user's label and that are compatible with the user's specified model type at the same time
            urls = list(
                master_dict[user_config["label_name"]][inference_type].keys())
            models = list(
                master_dict[user_config["label_name"]][inference_type].values())
            # we check each possible case that can occur:
            # 1- the url is specified in the user's configuration file, this url is present in the matching urls, and the inference type is correct
            if user_config["url"] is not None and user_config["url"] in urls and user_config[
                "model_type"] == inference_type:
                # if all the conditions above are true, we now check if the label is supported by the user's specified url and if the anonymization technique is applicable to this label
                if user_config["model_name"] in master_dict[user_config["label_name"]][user_config["model_type"]][
                    user_config["url"]] and user_config["technique"] in master_dict[user_config["label_name"]][
                    "technique"]:
                    # in this case, we send a request to the inference api to get the response
                    response = getattr(ApiClient, "get_" + inference_type + "_response")(user_config['url'],
                                                                                         user_config['model_name'], im)
                    if inference_type == "segmentation":
                        labels_list = ApiClient.get_labels(user_config['url'], user_config["model_name"])
                        #palette = ApiClient.get_palette(user_config['url'], user_config['model_name'])
                        json_array = get_bbs(response, labels_list, user_config)
                        return response, json_array
                    else:
                        return response
                # here we are filling the errors list with all the errors that are present in the sensitive info and the index of this info in case one of the conditions above is false
                elif user_config["model_name"] not in master_dict[user_config["label_name"]][user_config["model_type"]][
                    user_config["url"]]:
                    errors.append("The model <" + user_config["model_name"] + "> in sensitive info <" + str(
                        i) + "> is not available in the " + inference_type + " url : <" + user_config[
                                      "url"] + "> for the label <" + user_config["label_name"] + ">.")
                elif user_config["technique"] not in master_dict[user_config["label_name"]]["technique"]:
                    errors.append("The technique <" + user_config["technique"] + "> is not supported for the label <" +
                                  user_config["label_name"] + "> in sensitive info <" + str(i) + ">.")
            # 2- the url is specified in the user's configuration file, this url is not between the matching urls, and the inference type is correct
            elif user_config["url"] is not None and user_config["url"] not in urls and user_config[
                "model_type"] == inference_type:
                errors.append("the url <" + user_config["url"] + "> does not belong to the list of urls supported")

            # 3- the user hasn't specified any url and the inference type is correct
            elif user_config["url"] is None and user_config["model_type"] == inference_type:
                model_not_found = True
                for val in models:
                    if user_config["model_name"] in val:
                        inde = models.index(val)
                        model_not_found = False

                # we check if the model specified is between the matching models and if the technique specified is applicable to this label
                if not model_not_found and user_config["model_name"] in models[inde] and user_config["technique"] in master_dict[user_config["label_name"]]["technique"]:
                    # we choose the first matching url
                    response = getattr(ApiClient, "get_" + inference_type + "_response")(urls[inde],
                                                                                         user_config['model_name'], im)
                    if inference_type == "segmentation":
                        labels_list = ApiClient.get_labels(urls[inde], user_config["model_name"])
                        #palette = ApiClient.get_palette(urls[inde], user_config['model_name'])
                        json_array = get_bbs(response, labels_list, user_config)
                        return response, json_array
                    else:
                        return response
                # here we are filling the errors list with all the errors that are present in the sensitive info and the index of this info in case one of the conditions above is false
                elif model_not_found:
                    errors.append("The model <" + user_config["model_name"] + "> in sensitive info <" + str(
                        i) + "> is not available in the " + inference_type + " for label  <" + user_config[
                                      "label_name"] + ">")
                elif user_config["technique"] not in master_dict[user_config["label_name"]]["technique"]:
                    errors.append("The technique <" + user_config["technique"] + "> is not supported for the label <" +
                                  user_config["label_name"] + "> in sensitive info <" + str(i) + ">.")
        else:
            errors.append("The label <" + user_config["label_name"] + "> in the sensitive info <" + str(
                i) + "> is not supported by a " + inference_type + " api.")
    else:
        errors.append("The label <" + user_config["label_name"] +
                      "> in the sensitive info <" + str(i) + "> is not supported.")
    return errors


def get_bbs(image, labels_list, user_config):
    image = Image.open(io.BytesIO(image.content))
    palette=image.getpalette()
    label_id = labels_list.index(user_config['label_name'])
    rgb_image = np.array(image.convert(mode="RGB"))
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    response = []

    lower = np.array([palette[(int(label_id) * 3) + 2], palette[(int(label_id) * 3) + 1], palette[(int(label_id) * 3)]])
    mask1 = cv2.inRange(bgr_image, lower, lower)
    contours, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    boxes = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if (len(np.array(c).flatten()) > 3):
            boxes.append([x, y, x + w, y + h])
    for b in boxes:
        response.append({"ObjectClassId": label_id, "class_name": user_config["label_name"], "bbox": b})
    return response


def parse_detection_response(user_config, im, i, errors):
    """ Parse the object detection api response and returns a list of json objects
    representing the parsed response in addition to some useful user sensitive info
    :param user_config: a json object that represent each sensitive info specified by the user
    :param im: the image we need to anonymize
    :param i: index of the sensitive info
    :param errors: list of errors that will be filled in case any error is the user's configuration file is present
    :return: List of json objects
    """
    boxes = []
    bounding_boxes = []
    response = parse_inference_response("detection", user_config, im, i, errors)
    if not errors:
        for bbox in response['data']['bounding-boxes']:
            if bbox['ObjectClassName'] == user_config['label_name']:
                bounds = [bbox['coordinates']['left'],
                          bbox['coordinates']['top'],
                          bbox['coordinates']['right'],
                          bbox['coordinates']['bottom']]
                boxes.append(bounds)
                bounding_boxes.append({'type': user_config['model_type'],
                                       'technique': user_config['technique'],
                                       'boxes': boxes,
                                       'degree': user_config['degree'],
                                       'label_id': None})
        return bounding_boxes, None
    else:
        return response, None


def parse_segmentation_response(user_config, im, i, errors):
    """ Parse the semantic segmentation api response and returns a list of json objects
    representing the parsed response in addition to some useful user sensitive info
    :param user_config: a json object that represent each sensitive info specified by the user
    :param im: the image we need to anonymize
    :param i: index of the sensitive info
    :param errors: list of errors that will be filled in case any error is the user's configuration file is present
    :return: List of json objects
    """
    bounding_boxes = []
    r = parse_inference_response("segmentation", user_config, im, i, errors)
    try:
        mask, response = r
    except Exception as e:
        response = r
    if not errors:
        for data in response:
            if data['class_name'] == user_config['label_name']:
                result = {
                    'boxes': data['bbox'],
                    'type': user_config['model_type'],
                    'technique': user_config['technique'],
                    'degree': user_config['degree'],
                    'label_id': data['ObjectClassId']
                }
                bounding_boxes.append(result)
        return bounding_boxes, mask
    else:
        return response, None


def validate_json_configuration(data):
    """Validate the user configuration file by comparing it to the ConfigurationSchema
    :param data: The data from the user configuration file
    """
    with open('ConfigurationSchema.json') as f:
        schema = json.load(f)
    try:
        jsonschema.validate(data, schema)
    except Exception as e:
        raise InvalidModelConfiguration(e)


def check_api_availability(url: str):
    try:
        response = requests.get(url + "models")
    except Exception:
        raise Exception("wrong url format. expected format: http://ip:port/")
    return response


def parse_json(json_path):
    with open(json_path, 'r') as f:
        try:
            payload = json.load(f)
        except Exception:
            raise Exception("Json file corrupted")
    return payload


def write_json(payload, json_path):
    with open(json_path, 'w') as outfile:
        json.dump(payload, outfile)
