import json
from typing import Text, Dict, Any, List, Iterable

from src.rest import Rest
from config import configuration as cnfg

### Need to change the import
from .slackChannel.inputChannel import InputChannel
from .slackChannel.outputChannel import OutputChannel


class SlackBot():

    def __init__(self):
        self.slackInputChannel = InputChannel(cnfg.slack_token, "slack", "x-slack-retry-reason", "x-slack-retry-num", "http_timeout")
        # self.app_id = configuration.botapp_id
        # self.app_password = configuration.botapp_password
        self.RestAPI = Rest()
        self.validMessage = None
        self.senderId = None



    async def sendMessageToBot(self, message):
        return await self.slackInputChannel.receive(message, self.messagehandling)
        # validMessage, slackSenderId = self.validMessage(inpMessage)

        # if self.validMessage == None:
        #     return ""
        # botResponse = self.RestAPI.sendMessageToBot(self.validMessage)
        # out_channel = self.botOutputChannel(self.slackSenderId)
        # await out_channel.sendBotResponse(botResponse)

    def validMessageFn(self, inpMessage):
        self.validMessage, self.senderId = (None, None)
        if type(inpMessage) == tuple and len(inpMessage) == 2 and type(inpMessage[0]) == str:
            # return
            self.validMessage = {
                "message": inpMessage[0],
                "sender": "802983"
            }
            self.senderId = inpMessage[1]
            return self.validMessage, self.senderId
        else:
            return None, None

    async def messagehandling(self, message, sender_id):
        if message == None:
            return ""
        botResponse = self.RestAPI.sendMessageToBot(message)
        out_channel = self.botOutputChannel(sender_id)
        await out_channel.sendBotResponse(botResponse)



    def botOutputChannel(self, senderId):
        out_channel = OutputChannel(
            cnfg.slack_token,
            senderId
        )

        return out_channel