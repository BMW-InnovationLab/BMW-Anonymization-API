# Deploying the BMW-Anonymization-Api with docker compose

In this section, docker compose will build and run a network of containers including the Anonymization API alongside multiple inference APIs.

In the following section, we encapsulate the [BMW-IntelOpenVINO-Inference-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Inference-API) and the [BMW-IntelOpenVINO-Segmentation-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Segmentation-API) with our anonymization API. 

These two inference APIs contain example models optimzed via OpenVINO. Other OpenVINO models in Intermediate Representation(IR) format, converted via the [Intel&reg; OpenVINO&trade; toolkit v2021.1](https://docs.openvinotoolkit.org/latest/index.html), can be deployed with our APIs. Currently, OpenVINO supports conversion for DL-based models trained via several Machine Learning frameworks including Caffe, Tensorflow etc. Please refer to [the OpenVINO documentation](https://docs.openvinotoolkit.org/2021.1/openvino_docs_MO_DG_prepare_model_convert_model_Converting_Model.html) for further details on converting your Model.


## Build and Run the network

In this section, docker compose will build and run a network of containers including the Anonymization API alongside the OpenVINO inference APIs for detection and segmentation. The instructions are provided below. 

To run the APIs together, clone the [BMW-Anonymization-API](https://github.com/BMW-InnovationLab/BMW-Anonymization-API), the [BMW-IntelOpenVINO-Inference-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Inference-API) and the [BMW-IntelOpenVINO-Segmentation-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Segmentation-API) into the same directory.

The folder structure should be similar to as shown below:

```shell
│──BMW-Anonymization-API
  │──docker 
  |──jsonFiles  
  │──...
  |──docker-compose.yml  
  │──Readme.md  
│──BMW-IntelOpenVINO-Segmentation-API 
  │──docker 
  |──...
  │──docs  
  │──Readme.md
│──BMW-IntelOpenVINO-Detection-Inference-API
  │──docker 
  |──...
  │──docs  
  │──Readme.md
  
```

In the BMW-Anonymization API replace the `./BMW-Anonymization-API/jsonFiles/url_configuration.json` with the provided `./url_for_openvino_compose/url_configuration.json`.

Three services are configured in the `docker-compose.yml` file in this repository: the [BMW-Anonymization-API](https://github.com/BMW-InnovationLab/BMW-Anonymization-API), the [BMW-IntelOpenVINO-Inference-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Inference-API) and the [BMW-IntelOpenVINO-Segmentation-API](https://github.com/BMW-InnovationLab/BMW-IntelOpenVINO-Segmentation-API). You can modify the build context to specify the base directories of the APIs (ensure the correct path is also given for the mounted volumes). You can also modify the host ports you wish to use for the APIs. 

After you configure your docker-compose.yml file, you can run the following command in the anonymization API directory:

### Build the images
To build the images, run the following command in this directory:
```sh
docker-compose build
```

### Run the network
To run the network, use the following command in this directory:
```sh
docker-compose up
```

### Stop the running containers
To stop the network, run the following command in this directory:
```sh
docker-compose down
```

### Restart the network
To restart the network, run the following command in this directory:
```sh
docker-compose restart
```

## API Endpoints

To see all available endpoints, open your favorite browser and navigate to:
```
http://<machine_IP>:<docker_host_port>/docs
```
If you use the standard configuration of the `docker-compose.yml` the folllowing endpoints are available:
| API | Endpoint |
| ------------------ | ------------------ |
| BMW-Anonymization-API | http://localhost:8070/docs |
| RCV-IntelOpenVINO-Detection-API | http://localhost:8081/docs |
| BMW-IntelOpenVINO-Segmentation-API | http://localhost:8090/docs |

**Please refer to the Endpoints Summary section in the [initial readme](https://github.com/BMW-InnovationLab/Anonymization_API/tree/priority-3)**

## Using other inference APIs

Other inference APIs can also be configured within the docker-compose.yml such as our [tensorflow CPU detection API](https://github.com/BMW-InnovationLab/BMW-TensorFlow-Inference-API-CPU) and [semantic segmentation CPU/GPU](https://github.com/BMW-InnovationLab/BMW-Semantic-Segmentation-Inference-API-GPU-CPU))
If you wish to deploy other inference APIs, please make sure to the docker-compose.yml accordingly:
- Modify the context in order to specify the base directory of each API
- Modify the dockerfile entry to match the path of the dockerfile in the API directory 
- Modify the ports and choose the ones you wish to use for each API
- In case you are setting up a GPU-based inference API, do not forget to set the runtime entry as "nvidia" 

We provided a sample docker-compose file  `./BMW-Anonymization-API/docker-compose_tf_gluoncv.yml`

