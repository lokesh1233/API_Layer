import datetime
import json
import logging
import requests
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, List, Iterable, Callable, Awaitable, Optional

from sanic.response import HTTPResponse


class OutputChannelStructure():
    def __init__(self) -> None:
        self.messages = []

    def getdates(self, formType):
        datesJson = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "color": "accent",
                        "text": "Please specify the dates?",
                        "weight": "Bolder",
                        "size": "large"
                    },
                    {
                        "type": "TextBlock",
                        "color": "attention",
                        "text": "From",
                        "size": "large",
                        "weight": "Bolder"
                    },
                    {
                        "type": "Input.Date",
                        "id": "from",
                        "title": "New Input.Toggle",
                        "placeholder": "Enter a date",
                        "value": datetime.datetime.today().strftime('%Y-%m-%d')
                    },
                    {
                        "type": "TextBlock",
                        "color": "attention",
                        "text": "To",
                        "size": "large",
                        "weight": "Bolder"
                    },
                    {
                        "type": "Input.Date",
                        "id": "to",
                        "title": "New Input.Toggle",
                        "placeholder": "Enter a date",
                        "value": datetime.datetime.today().strftime('%Y-%m-%d')
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Submit",
                        "style": "positive",
                        "data": {"form": formType}
                    }
                ]
            }
        }
        return datesJson

    def noLeaveList(self, json_message):
        final_json = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": json_message['json'],
                        "weight": "bolder"
                    }
                ]
            }
        }
        return final_json

        # def getButtonsInbotFramework(self,button_json):
        #     bot_buttons = []
        #     for button in button_json:
        #         if "payload" in button:
        #             bot = {}
        #             bot["type"] = "messageBack"
        #             bot["title"] = button["title"]
        #             bot["displayText"] = button["title"]
        #             bot["text"] = button["title"]
        #             bot["value"] = button["payload"]
        #             bot_buttons.append(bot)
        #     return bot_buttons

    def getButtonsInbotFramework(self, button_json):
        bot_buttons = []
        for button in button_json:
            if "payload" in button:
                bot = {}
                bot["type"] = "imBack"
                bot["title"] = button["title"]
                bot["displayText"] = button["title"]
                bot["text"] = button["title"]
                bot["value"] = button["payload"]
                bot_buttons.append(bot)
        return bot_buttons

    def getTabularData(self, rasa_output_json):
        rasa_json = rasa_output_json['json']
        text_json = rasa_output_json['text']
        items_list_col1 = [{"type": "TextBlock", "weight": "bolder", "text": "Date"}]
        json_1 = {}
        for r in rasa_json:
            for key in r:
                x = {"type": "TextBlock", "separator": "true"}
                json_1["text"] = key
                x.update(json_1)
                items_list_col1.append(x)
        items_list_col2 = [{"type": "TextBlock", "weight": "bolder", "text": "Name"}]
        json_2 = {}
        for r in rasa_json:
            for key in r:
                x = {"type": "TextBlock", "separator": "true"}
                json_2["text"] = r[key]
                x.update(json_2)
                items_list_col2.append(x)
        columns_dict_1 = {}
        columns_dict_1["type"] = "Column"
        columns_dict_1["items"] = items_list_col1
        columns_dict_2 = {}
        columns_dict_2["type"] = "Column"
        columns_dict_2["items"] = items_list_col2
        columns_list = []
        columns_list.append(columns_dict_1)
        columns_list.append(columns_dict_2)
        column_set_dict = {}
        column_set_dict["type"] = "ColumnSet"
        column_set_dict["columns"] = columns_list
        card_name_dict = {}
        card_name_dict["type"] = "TextBlock"
        card_name_dict["text"] = rasa_output_json['text']
        card_name_dict["weight"] = "Bolder"
        card_name_dict["color"] = "accent"
        card_name_dict["size"] = "large"
        body_list = []
        body_list.append(card_name_dict)
        body_list.append(column_set_dict)
        content_dict = {}
        content_dict["type"] = "AdaptiveCard"
        content_dict["body"] = body_list
        attachments_dict = {}
        attachments_dict["contentType"] = "application/vnd.microsoft.card.adaptive"
        attachments_dict["content"] = content_dict
        attachments_list = []
        attachments_list.append(attachments_dict)
        return attachments_list

    def getLeaveList(self, rasa_output_json):
        rasa_output = rasa_output_json['json']
        final_leave_list = []
        count=0
        for leave in rasa_output:
            if leave["Status"] == "PENDING":
                style = "attention"
            elif leave["Status"] == "REJECTED":
                style = "warning"
            else:
                style = "accent"

            leave = {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": rasa_output_json['text'],
                                    "color": "accent",
                                    "weight": "bolder",
                                    "size": "extralarge"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "From Date",
                                    "color": "warning",
                                    "weight": "bolder",
                                    "size": "large"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": leave["Date"],
                                    "horizontalAlignment": "center",
                                    "color": "accent",
                                    "weight": "bolder",
                                    "size": "large"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "To date",
                                    "color": "warning",
                                    "weight": "bolder",
                                    "size": "large"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": leave["To date"],
                                    "horizontalAlignment": "center",
                                    "color": "accent",
                                    "weight": "bolder",
                                    "size": "large"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "style": "default",
                            "items": [
                                {
                                    "type": "Container",
                                    "style": style,
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": leave["Status"],
                                            "weight": "bolder",
                                            "size": "large",
                                            "color": "accent",
                                            "horizontalAlignment": "center"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
            final_leave_list.append(leave)
            count = count + 1
            if count == 3:
                break
        return final_leave_list

    def getCovidData(self, rasa_output_json):
        rasa_json = rasa_output_json['json']
        return [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "COVID-19 statistics",
                        "weight": "Bolder",
                        "color": "accent",
                        "size": "extralarge"
                    },
                    {
                        "type": "TextBlock",
                        "text": rasa_output_json["text"],
                        "weight": "Bolder",
                        "color": "warning",
                        "size": "large"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_json[1]["Case"],
                                        "size": "large",
                                        "color": "accent"
                                    },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            {
                                                "title": "Existing ",
                                                "value": rasa_json[1]["ActiveValue"],
                                                "size": "large"
                                            },
                                            {
                                                "title": "New ",
                                                "value": rasa_json[1]["NewValue"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_json[0]["Case"],
                                        "size": "large",
                                        "color": "attention"
                                    },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            {
                                                "title": "Existing ",
                                                "value": rasa_json[0]["ActiveValue"],
                                                "size": "large"
                                            },
                                            {
                                                "title": "New ",
                                                "value": rasa_json[0]["NewValue"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_json[2]["Case"],
                                        "size": "large",
                                        "color": "good"
                                    },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            {
                                                "title": "Existing ",
                                                "value": rasa_json[2]["ActiveValue"],
                                                "size": "large"
                                            },
                                            {
                                                "title": "New ",
                                                "value": rasa_json[2]["NewValue"]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_json[2]["Case"],
                                        "size": "large",
                                        "color": "warning"
                                    },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            {
                                                "title": "Existing ",
                                                "value": rasa_json[3]["ActiveValue"],
                                                "size": "large"
                                            },
                                            {
                                                "title": "New ",
                                                "value": rasa_json[3]["NewValue"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "COVID -19 Portal",
                        "style": "positive",
                        "url": "https://api.covid19india.org/data.json"
                    }
                ]
            }
        }]

    def getLerningFormat(self, rasa_output_json):
        learning_json = rasa_output_json['json']
        json_array_1 = []
        json_array_2 = []
        json_Array_3 = []
        json_Array_4 = []
        json_Array_5 = []
        count = 0
        for r in learning_json:
            items_list_col1 = []
            json_1 = {}
            for key in r:
                x = {"type": "TextBlock", "separator": "true", "color": "accent"}
                if key == "forms_type":
                    continue
                else:
                    json_1["text"] = str(key) + " : " + str(r[key])
                    x.update(json_1)
                    items_list_col1.append(x)
            json_array_1.append(items_list_col1)
            count = count + 1
            if count == 3:
                break

        for element in json_array_1:
            columns_dict_1 = {}
            columns_dict_1["type"] = "Column"
            columns_dict_1["items"] = element
            json_array_2.append(columns_dict_1)

        for j in json_array_2:
            json_3 = {}
            json_3["type"] = "ColumnSet"
            json_array = []
            json_array.append(j)
            json_3["columns"] = json_array
            json_Array_3.append(json_3)

        for j in json_Array_3:
            json_4 = {}
            json_4["type"] = "AdaptiveCard"
            json_array = []
            json_array.append(j)
            json_4["body"] = json_array
            json_Array_4.append(json_4)

        for j in json_Array_4:
            json_5 = {}
            json_5["contentType"] = 'application/vnd.microsoft.card.adaptive'
            json_5["content"] = j
            json_Array_5.append(json_5)
        return json_Array_5

    def travelBooking(self, rasa_output_json):

        return [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Travel Summary",
                        "weight": "Bolder",
                        "color": "accent",
                        "size": "large",
                        "spacing": "extraLarge"
                    },
                    {
                        "type": "TextBlock",
                        "text": rasa_output_json["json"][0]["fromDate"],
                        "color": "warning",
                        "size": "large",
                        "weight": "Bolder",
                        "spacing": "None"
                    },
                    {
                        "type": "ColumnSet",
                        "separator": "True",
                        "columns": [
                            {
                                "type": "Column",
                                "width": 1,
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_output_json["json"][0]["Origion"],
                                        "weight": "Bolder",
                                        "size": "large",
                                        "isSubtle": "True"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "Image",
                                        "url": "https://adaptivecards.io/content/airplane.png",
                                        "size": "Small",
                                        "spacing": "None"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": 1,
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_output_json["json"][0]["Destination"],
                                        "weight": "Bolder",
                                        "size": "large",
                                        "horizontalAlignment": "Right",
                                        "isSubtle": "True"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": rasa_output_json["json"][0]["fromDate"],
                        "size": "large",
                        "color": "warning",
                        "weight": "Bolder",
                        "spacing": "None"
                    },
                    {
                        "type": "ColumnSet",
                        "separator": "True",
                        "columns": [
                            {
                                "type": "Column",
                                "width": 1,
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_output_json["json"][0]["Destination"],
                                        "size": "large",
                                        "weight": "Bolder",
                                        "isSubtle": "True"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "Image",
                                        "url": "https://adaptivecards.io/content/airplane.png",
                                        "size": "Small",
                                        "spacing": "None"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": 1,
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": rasa_output_json["json"][0]["Origion"],
                                        "size": "large",
                                        "weight": "Bolder",
                                        "horizontalAlignment": "Right",
                                        "isSubtle": "True"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": rasa_output_json['json'][0]['buttons'][0]['title'],
                        "style": "positive",
                        "data": {
                            "msteams": {
                                "type": "imBack",
                                "value": rasa_output_json['json'][0]['buttons'][0]['payload']
                            }
                        }
                    },
                    {
                        "type": "Action.Submit",
                        "title": rasa_output_json['json'][0]['buttons'][1]['title'],
                        "style": "destructive",
                        "data": {
                            "msteams": {
                                "type": "imBack",
                                "value": rasa_output_json['json'][0]['buttons'][1]['payload']
                            }
                        }
                    }
                ]
            }
        }]

    def getApprovalsList(self, rasa_output_json):
        Approvals_list = []
        approval_json = rasa_output_json['json']
        count = 0
        for r in approval_json:
            x = {"contentType": "application/vnd.microsoft.card.adaptive",
                 "content": {
                     "type": "AdaptiveCard",
                     "body": [{
                         "type": "Container",
                         "style": "default",
                         "items": [
                             {
                                 "type": "Container",
                                 "style": "default",
                                 "items": [
                                     {
                                         "type": "TextBlock",
                                         "text": r['Name'],
                                         "color": "accent",
                                         "weight": "bolder",
                                         "size": "extraLarge"
                                     }
                                 ]
                             },
                             {
                                 "type": "Container",
                                 "style": "default",
                                 "items": [
                                     {
                                         "type": "TextBlock",
                                         "text": "From :",
                                         "color": "warning",
                                         "weight": "bolder",
                                         "size": "large"
                                     }
                                 ]
                             },
                             {
                                 "type": "Container",
                                 "style": "default",
                                 "items": [
                                     {
                                         "type": "TextBlock",
                                         "text": r['Date'],
                                         "horizontalAlignment": "center",
                                         "color": "accent",
                                         "weight": "bolder",
                                         "size": "large"
                                     }
                                 ]
                             },
                             {
                                 "type": "Container",
                                 "style": "default",
                                 "items": [
                                     {
                                         "type": "TextBlock",
                                         "text": "To :",
                                         "color": "warning",
                                         "weight": "bolder",
                                         "size": "large"
                                     }
                                 ]
                             },
                             {
                                 "type": "Container",
                                 "style": "default",
                                 "items": [
                                     {
                                         "type": "TextBlock",
                                         "text": r['toDate'],
                                         "horizontalAlignment": "center",
                                         "color": "accent",
                                         "weight": "bolder",
                                         "size": "large"
                                     }
                                 ]
                             }
                         ]
                     },
                         {
                             "type": "ActionSet",
                             "actions": [
                                 {
                                     "type": "Action.Submit",
                                     "title": r['buttons'][0]['title'],
                                     "style": "positive",
                                     "data": {
                                         "msteams": {
                                             "type": "imBack",
                                             "title": r['buttons'][0]['title'],
                                             "value": r['buttons'][0]['payload']
                                         }
                                     }
                                 },
                                 {
                                     "type": "Action.Submit",
                                     "title": r['buttons'][1]['title'],
                                     "style": "destructive",
                                     "size": "small",
                                     "data": {
                                         "msteams": {
                                             "type": "imBack",
                                             "title": r['buttons'][1]['title'],
                                             "value": r['buttons'][1]['payload']
                                         }
                                     }
                                 }
                             ]
                         }
                     ]
                 }
                 }
            Approvals_list.append(x)
            count = count + 1
            if count == 3:
                break
        return Approvals_list
