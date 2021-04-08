# Deploying the BMW-Anonymization-Api with docker compose

In this section, docker compose will build and run a network of containers including the Anonymization API alongside multiple inference APIs.

## Build and Run the network

In order to build and run all the APIs together, copy all APIs project repositories to the machine you wish to infer on and modify the following:

In the anonymization API directory go to "/docker-compose.yml"

In the docker-compose.yml file available in this repo, we configured three services: (1) the anonymization api, (2) the [tensorflow CPU detection API](https://github.com/BMW-InnovationLab/BMW-TensorFlow-Inference-API-CPU) and (3) the [semantic segmentation CPU/GPU](https://github.com/BMW-InnovationLab/BMW-Semantic-Segmentation-Inference-API-GPU-CPU).

If you wish to deploy other inference APIs:
- Modify the context in order to specify the base directory of each API
- Modify the dockerfile entry to match the path of the dockerfile in the API directory 
- Modify the ports and choose the ones you wish to use for each API
- In case you are setting up a GPU-based inference API, do not forget to set the runtime entry as "nvidia" 

After you configure your docker-compose.yml file, you can run the following command in the anonymization API directory:

```sh
docker-compose up
```

In the terminal, you should now see all the APIs running together.

In case an error related to URL not reachable appeared, old URLs in the jsonFiles/url_configuration.json file should be cleared and the json file should look like:
```json
{
  "urls": [
  ]
}
```

**Please refer to the Endpoints Summary section in the [initial readme](https://github.com/BMW-InnovationLab/BMW-Anonymization-API/)**

## Stop the running containers

Run the following command in the anonymization API directory:

```sh
docker-compose down
```

## Restart the network

Run the following command in the anonymization API directory:

```sh
docker-compose restart
```
