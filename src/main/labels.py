import os
import sys
import json
from APIClient import ApiClient

sys.path.append("supported_methods")


def labels_methods():
    """
    Returns a list of the available labels with their available anonymization methods, the urls
    that supports them, the type of each url and the model names
    :return: List of json objects
    """
    api_client = ApiClient()
    labels = []
    master_dict = {}
    types = []
    urls = []
    for model in api_client.configuration:
        types.append(model['type'])
        urls.append(model['url'])

        for label in model["labels"]:
            labels.append(label)

    master_dict = master_dict.fromkeys(labels)

    for label in labels:
        url_type = {}
        for type in types:
            #            models = []
            for url in urls:
                models = []
                for model in api_client.configuration:
                    if model["type"] == type and model["url"] == url and label in model["labels"]:
                        models.append(model['name'])
                        if model['type'] not in url_type.keys():
                            url_type[model['type']] = {}
                        url_type[model['type']][model['url']] = models
                        master_dict[label] = url_type

    special_labels = []
    for file in os.listdir(os.path.join(os.getcwd(), "supported_methods")):
        if file != 'common_labels.py' and file != '__init__.py' and file != '__pycache__':
            special_label = file.split(".")[0]
            special_labels.append(special_label)

    for user_label in labels:
        if user_label in special_labels:
            class_name = user_label.title()
            x = getattr(__import__(user_label), class_name)()
            attr = getattr(x, "get_labels")(class_name)
            master_dict[user_label]['technique'] = attr

        else:
            class_name = user_label.title()
            x = getattr(__import__('common_labels'), 'CommonLabels')()
            attr = getattr(x, "get_labels")(class_name)
            master_dict[user_label]['technique'] = attr
    return master_dict


'''

Old version
import os
import sys
import json
from APIClient import ApiClient

sys.path.append("supported_methods")


def labels_methods():
    """
    Returns a list of the available labels with their available anonymization methods, the urls
    that supports them, the type of each url and the model names
    :return: List of json objects
    """
    api_client = ApiClient()
    labels = []
    master_dict = {}
    types = []
    for model in api_client.configuration:
        types.append(model['type'])
        for label in model["labels"]:
            labels.append(label)

    master_dict = master_dict.fromkeys(labels)

    for label in labels:
        url_type = {}
        for type in types:
            models = []
            for model in api_client.configuration:
                if model["type"] == type and label in model["labels"]:
                    models.append(model['name'])
                    url_type[model['type']] = {model['url']: models}
                    master_dict[label] = url_type

    special_labels = []
    for file in os.listdir(os.path.join(os.getcwd(), "supported_methods")):
        if file != 'common_labels.py' and file != '__init__.py' and file != '__pycache__':
            special_label = file.split(".")[0]
            special_labels.append(special_label)

    for user_label in labels:
        if user_label in special_labels:
            class_name = user_label.title()
            x = getattr(__import__(user_label), class_name)()
            attr = getattr(x, "get_labels")(class_name)
            master_dict[user_label]['technique'] = attr

        else:
            class_name = user_label.title()
            x = getattr(__import__('common_labels'), 'CommonLabels')()
            attr = getattr(x, "get_labels")(class_name)
            master_dict[user_label]['technique'] = attr
    return master_dict

'''
