import io
import cv2
from models import ApiResponse
from labels import labels_methods
from exceptions import ApplicationError
from fastapi import UploadFile, File, FastAPI, Form
from fastapi.responses import StreamingResponse
from anonymization_service import AnonymizationService
import helpers
import config

app = FastAPI(version='2.0', title='BMW Anonymization API',
              description="<h3><b>API that localizes and obfuscates sensitive information in images/videos in order to preserve the individuals anonymity.</b></h3>"
						  "<b>Developers:</b></br>"
                          "<b>Ghenwa Aoun</b>"
                          "</br> "
						  "<b>Antoine Charbel</b></br>"
                          "<b>Jimmy Tekli</b>"
                          "</br>"
                          "<br><b>Contact us:</b></br>"
						  "<b>BMW Innovation Lab: <a href='mailto:innovation-lab@bmw.de'>innovation-lab@bmw.de</a></b>")
anonymizationservice = AnonymizationService()
config.master_dict = labels_methods()

url_config_path = "../jsonFiles/url_configuration.json"

@app.get('/list_urls', tags=["Configuration"])
def list_urls():
    """
    list all available urls in the url json file
    :return: ApiResponse
    """
    try:
        payload = helpers.parse_json(url_config_path)
    except Exception as e:
        return ApiResponse(success=False, error=e)
    return ApiResponse(data=payload)


@app.post('/set_url', tags=["Configuration"])
def set_url(url: str = Form(...)):
    """
    Add url to the url json file
    :param url: api url in the format: http://ip:port/
    :return: ApiResponse
    """
    try:
        payload = helpers.parse_json(url_config_path)
        response = helpers.check_api_availability(url)
    except Exception as e:
        return ApiResponse(success=False, error=e)
    if response.status_code == 200:
        if url not in payload['urls']:
            payload['urls'].append(url)
            helpers.write_json(payload, url_config_path)
            data = "url added successfully"
        else:
            data = "url already exist"
        return ApiResponse(data=data)
    else:
        return ApiResponse(success=False, error="url trying to add is not reachable")


@app.post('/remove_url', tags=["Configuration"])
def remove_url(url: str = Form(...)):
    """
        Remove url from the url json file
        :param url: api url in the format: http://ip:port/
        :return: ApiResponse
        """
    try:
        payload = helpers.parse_json(url_config_path)
    except Exception as e:
        return ApiResponse(success=False, error=e)
    if url in payload['urls']:
        payload['urls'].remove(url)
        helpers.write_json(payload, url_config_path)
        return ApiResponse(data={"url removed successfully"})
    else:
        return ApiResponse(success=False, error="url is not present in config file")


@app.post('/remove_all_urls', tags=["Configuration"])
def remove_all_urls():
    """
    Remove all available urls in the url json file
    :return: ApiResponse
    """
    payload = {"urls": []}
    helpers.write_json(payload, url_config_path)
    return ApiResponse(data="all urls removed successfully")


@app.get('/available_methods/', tags=["Configuration"])
def get_available_methods():
    """
    :return: A list that shows the model name, the urls and the model types that support each label in addition to the anonymization techniques that can be applied to each of them
    """
    try:
        config.master_dict = labels_methods()
        return config.master_dict
    except Exception:
        return ApiResponse(success=False, error='unexpected server error')


@app.post('/anonymize/', tags=["Anonymization"])
def anonymize(image: UploadFile = File(...), configuration: UploadFile = File(...)):
    """
    Anonymize the given image
    :param image: Image file
    :param configuration: Json file
    :return: The anonymized image
    """
    try:
        result, errors = anonymizationservice.anonymize(image, configuration)
        if not errors:
            _, im_png = cv2.imencode(".png", result)
            response = StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/jpeg")
            return response
        else:
            return ApiResponse(success=False,
                               error="Some data in your configuration file need to be modified. Check the /available_methods/ endpoint",
                               data=errors)
    except ApplicationError as e:
        return ApiResponse(success=False, error=e)
    except Exception:
        return ApiResponse(success=False, error='unexpected server error')


@app.post('/anonymize_video/', tags=["Anonymization"])
def anonymize_video(video: UploadFile = File(...), configuration: UploadFile = File(...)):
    """
    Anonymize the given video  and save it to src/main/anonymized_video as original_video_name_TIMESTAMP.mp4
    :param video: Video file
    :param configuration: Json file
    """
    try:
        return anonymizationservice.anonymize_video(video, configuration)
    except ApplicationError as e:
        return ApiResponse(success=False, error=e)
    except Exception:
        return ApiResponse(success=False, error='unexpected server error')
