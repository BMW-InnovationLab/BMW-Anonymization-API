import os
import sys
import time
import requests

start_time = time.time()

url = "http://ip:port/anonymize/"
j = 0
list_of_images = os.listdir("large")

for i in list_of_images:
    j = j + 1
    files = {"image": open("large/" + i, 'rb'),
             "configuration": open('user_configuration.json', 'rb')}
    response = requests.post(url, files=files)
    print("Total time: " + str(time.time() - start_time))
    with open("results/anonymized_" + i, 'wb') as f:
        f.write(response.content)
    if response.status_code != 200:
        print(time.time() - start_time)
        sys.exit("error")
