# import scipy.io.wavfile as wav

from typing import Optional, Text, Any, List, Dict, Iterable
import json
import uuid
from config import configuration
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Rest():
    def __init__(self):
        self.restURL = configuration.restAPI

    def sendMessageToBot(self, message):
        res = requests.post(self.restURL, json.dumps(message))
        # res = requests.post(self.restURL, data=message)
        return res.json()

