import json
from typing import Text, Dict, Any, List, Iterable

from src.rest import Rest
from config import configuration

### Need to change the import
from .botFrameworkChannel.inputChannel import InputChannel
from .botFrameworkChannel.outputChannel import OutputChannel


class BotFramework():

    def __init__(self):
        self.botInputChannel = InputChannel()
        self.app_id = configuration.botapp_id
        self.app_password = configuration.botapp_password
        self.RestAPI = Rest()


    async def sendMessageToBot(self, message):
        validMessage = self.botInputChannel.receive(message)
        botResponse = self.RestAPI.sendMessageToBot(validMessage)
        out_channel = self.botOutputChannel(message)
        await out_channel.sendBotResponse(botResponse)

    def botOutputChannel(self, message):
        out_channel = OutputChannel(
            self.app_id,
            self.app_password,
            message["conversation"],
            message["recipient"],
            message["serviceUrl"],
        )

        return out_channel