from config import configuration
import requests

class workerJob():

    def __init__(self):
        pass

    def statusOfWorker(self, path):
        return requests.get(configuration.workerHost+path).json()

    def trainOfWorker(self, path, data):
        return requests.post(configuration.workerHost + path, data=data).json()
