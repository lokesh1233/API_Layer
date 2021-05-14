import json
import logging
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Text

from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from slack import WebClient

logger = logging.getLogger(__name__)


class OutputChannel():
    """A Slack communication channel"""

    # @classmethod
    # def name(cls) -> Text:
    #     return "slack"

    def __init__(self, token: Text, slack_channel: Optional[Text] = None) -> None:

        self.slack_channel = slack_channel
        self.client = WebClient(token, run_async=True)

    @staticmethod
    def _get_text_from_slack_buttons(buttons: List[Dict]) -> Text:
        return "".join([b.get("title", "") for b in buttons])

    async def sendBotResponse(self, rasaResponse):
        for res in rasaResponse:
            await self.send_responseType(self.slack_channel, res)



    async def send_responseType(self, recipient_id: Text, message: Dict[Text, Any]) -> None:
        if message.get("buttons", None) != None:
            await self.send_text_with_buttons(recipient_id, message.pop("text"), message.pop("buttons"))
        elif message.get("text", None) != None:
            await self.send_text_message(recipient_id, message.pop("text"))

        if message.get("custom", None) != None:
            await  self.send_custom_json(recipient_id, message.pop("custom"))

        # if there is an image we handle it separately as an attachment
        if message.get("image", None) != None:
            await  self.send_image_url(recipient_id, message.pop("image"))

        if message.get("elements", None) != None:
            await self.send_elements(recipient_id, message.pop("elements"))

    async def send_text_message(self, recipient_id: Text, text: Text):
        recipient = self.slack_channel or recipient_id
        for message_part in text.strip().split("\n\n"):
            await self.client.chat_postMessage(
                channel=recipient, as_user=True, text=message_part, type="mrkdwn",
            )

    async def send_image_url(self, recipient_id: Text, image: Text):
        recipient = self.slack_channel or recipient_id
        image_block = {"type": "image", "image_url": image, "alt_text": image}
        await self.client.chat_postMessage(
            channel=recipient, as_user=True, text=image, blocks=[image_block],
        )

    async def send_attachment(self, recipient_id: Text, attachment: Dict[Text, Any]):
        recipient = self.slack_channel or recipient_id
        await self.client.chat_postMessage(
            channel=recipient, as_user=True, attachments=[attachment])

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]]):
        recipient = self.slack_channel or recipient_id

        text_block = {"type": "section", "text": {"type": "plain_text", "text": text}}

        if len(buttons) > 5:
            # raise_warning(
            #     "Slack API currently allows only up to 5 buttons. "
            #     "Since you added more than 5, slack will ignore all of them."
            # )
            return await self.send_text_message(recipient, text)

        button_block = {"type": "actions", "elements": []}
        for button in buttons:
            button_block["elements"].append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": button["title"]},
                    "value": button["payload"],
                }
            )
        await self.client.chat_postMessage(
            channel=recipient,
            as_user=True,
            text=text,
            blocks=[text_block, button_block],
        )

    async def send_custom_json(self, recipient_id: Text, json_message: Dict[Text, Any]):
        json_message.setdefault("channel", self.slack_channel or recipient_id)
        json_message.setdefault("as_user", True)
        await self.client.chat_postMessage(**json_message)
