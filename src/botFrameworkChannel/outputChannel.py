import logging
import requests
import json
import datetime
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, List, Iterable, Callable, Awaitable, Optional

from .outputChannelStructure import OutputChannelStructure
from sanic.response import HTTPResponse
logger = logging.getLogger(__name__)

MICROSOFT_OAUTH2_URL = "https://login.microsoftonline.com"

MICROSOFT_OAUTH2_PATH = "botframework.com/oauth2/v2.0/token"

class OutputChannel():

    token_expiration_date = datetime.datetime.now()
    headers = None
    botOutputStructure = OutputChannelStructure()

    # @classmethod
    # def name(cls) -> Text:
    #     return "botframework"

    def __init__(
            self,
            app_id: Text,
            app_password: Text,
            conversation: Dict[Text, Any],
            bot: Text,
            service_url: Text,
    ) -> None:

        service_url = (
            f"{service_url}/" if not service_url.endswith("/") else service_url
        )

        self.app_id = app_id
        self.app_password = app_password
        self.conversation = conversation
        self.global_uri = f"{service_url}v3/"
        self.bot = bot

    async def _get_headers(self) -> Optional[Dict[Text, Any]]:
        if OutPutChannel.token_expiration_date < datetime.datetime.now():
            uri = f"{MICROSOFT_OAUTH2_URL}/{MICROSOFT_OAUTH2_PATH}"
            grant_type = "client_credentials"
            scope = "https://api.botframework.com/.default"
            payload = {
                "client_id": self.app_id,
                "client_secret": self.app_password,
                "grant_type": grant_type,
                "scope": scope,
            }

            token_response = requests.post(uri, data=payload)

            if token_response.ok:
                token_data = token_response.json()
                access_token = token_data["access_token"]
                token_expiration = token_data["expires_in"]

                delta = datetime.timedelta(seconds=int(token_expiration))
                OutPutChannel.token_expiration_date = datetime.datetime.now() + delta

                OutPutChannel.headers = {
                    "content-type": "application/json",
                    "Authorization": "Bearer %s" % access_token,
                }
                return OutPutChannel.headers
            else:
                logger.error("Could not get BotFramework token")
        else:
            return OutPutChannel.headers

    def prepare_message(
            self, recipient_id: Text, message_data: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        data = {
            "type": "message",
            "recipient": {"id": recipient_id},
            "from": self.bot,
            "channelData": {"notification": {"alert": "true"}},
            "text": "",
        }
        data.update(message_data)
        return data

    async def send(self, message_data):
        post_message_uri = "{}conversations/{}/activities".format(
            self.global_uri, self.conversation["id"]
        )
        headers = await self._get_headers()
        send_response = requests.post(
            post_message_uri, headers=headers, data=json.dumps(message_data)
        )

        if not send_response.ok:
            logger.error(
                "Error trying to send botframework messge. Response: %s",
                send_response.text,
            )

    async def sendBotResponse(self, rasaResponse):
        for res in rasaResponse:
            botRes = self.send_responseType(res['recipient_id'], res)
            await self.send(botRes)


    def send_responseType(self, recipient_id: Text, message: Dict[Text, Any]) -> None:
        if message.get("quick_replies", None) != None:
            return self.send_quick_replies(
                recipient_id,
                message.pop("text"),
                message.pop("quick_replies"))
        elif message.get("buttons", None) != None:
            return self.send_text_with_buttons(recipient_id, message.pop("text"), message.pop("buttons"))
        elif message.get("text", None) != None:
            return self.send_text_message(recipient_id, message.pop("text"))

        if message.get("custom", None) != None:
            return  self.send_custom_json(recipient_id, message.pop("custom"))

        # if there is an image we handle it separately as an attachment
        if message.get("image", None) != None:
            return  self.send_image_url(recipient_id, message.pop("image"))

        if message.get("elements", None) != None:
            return self.send_elements(recipient_id, message.pop("elements"))


    def prepare_message(
            self, recipient_id: Text, message_data: Dict[Text, Any]
    ) -> Dict[Text, Any]:

        data = {
            "type": "message",
            "recipient": {"id": recipient_id},
            "from": self.bot,
            "channelData": {"notification": {"alert": "true"}},
            "text": "",
        }
        data.update(message_data)
        return data


    def send_text_message(self, recipient_id, text):
        for message_part in text.split("\n\n"):
            text_message = {"text": message_part}
            message = self.prepare_message(recipient_id, text_message)
            return message


    def send_elements(
            self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        for e in elements:
            message = self.prepare_message(recipient_id, e)
            return message


    def send_image_url(self, recipient_id, image):
        hero_content = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {"images": [{"url": image}]},
        }

        image_message = {"attachments": [hero_content]}
        message = self.prepare_message(recipient_id, image_message)
        return message


    def send_text_with_buttons(
            self,
            recipient_id: Text,
            text: Text,
            buttons: List[Dict[Text, Any]]):
        buttons = self.botOutputStructure.getButtonsInbotFramework(buttons)

        if "Please specify the dates?" in text:
            date_buttons = self.botOutputStructure.getdates("Travel")
            buttons_message = {"attachments": [date_buttons]}
        else:
            # if "I’m sorry" in text:
            #     buttons = self.getHomeButton()
            hero_content = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {"subtitle": text, "buttons": buttons},
            }
            buttons_message = {"attachments": [hero_content]}

        message = self.prepare_message(recipient_id, buttons_message)
        return message


    def send_custom_json(self, recipient_id, json_message):
        # pytype: disable=attribute-error

        custom_table_list = ['HolidayList', 'Leave details of your peers for the same duration', 'Leave Balance',
                             'Upcoming events']
        learning_json = ['Learning History', 'Learning Assignment']

        if 'text' in json_message:
            if json_message['text'] in custom_table_list:
                final_json = self.botOutputStructure.getTabularData(json_message)
                json_message = {}
                json_message.setdefault("attachments", final_json)
            elif json_message['text'] in learning_json:
                final_json = self.botOutputStructure.getLerningFormat(json_message)
                json_message = {}
                json_message.setdefault("attachments", json.loads(json.dumps(final_json)))
                json_message.setdefault("attachmentLayout", "carousel")
            elif json_message['text'] == 'Leave list':
                if isinstance(json_message['json'], str):
                    final_json = self.botOutputStructure.noLeaveList(json_message)
                    json_message.setdefault("attachments", final_json)
                else:
                    final_json = self.botOutputStructure.getLeaveList(json_message)
                    json_message = {}
                    json_message.setdefault("attachments", final_json)
                    json_message.setdefault("attachmentLayout", "carousel")
            elif "As of " in json_message['text']:
                final_json = self.botOutputStructure.getCovidData(json_message)
                json_message = {}
                json_message.setdefault("attachments", final_json)
            elif json_message['text'] == "Pending Approvals":
                final_json = self.botOutputStructure.getApprovalsList(json_message)
                json_message = {}
                json_message.setdefault("attachmentLayout", "carousel")
                json_message.setdefault("attachments", json.loads(json.dumps(final_json)))

            # elif json_message['json'][0]['forms_type']:
            #     if json_message['json'][0]['forms_type'] == "travelSummary":
            elif json_message['json'][0].get('forms_type', None) == 'travelSummary':
                    final_json = self.botOutputStructure.travelBooking(json_message)
                    json_message = {}
                    json_message.setdefault("attachments", final_json)

            json_message.setdefault("type", "message")
            json_message.setdefault("recipient", {}).setdefault("id", recipient_id)
            json_message.setdefault("from", self.bot)
            json_message.setdefault("channelData", {}).setdefault(
                "notification", {}
            ).setdefault("alert", "true")

            json_message.setdefault("text", "")

        elif json_message['json']['isDatePickerLeaves']:
            date_buttons = self.botOutputStructure.getdates("Apply leave")
            buttons_message = {"attachments": [date_buttons]}
            json_message = {}
            json_message = self.prepare_message(recipient_id, buttons_message)

        return json_message