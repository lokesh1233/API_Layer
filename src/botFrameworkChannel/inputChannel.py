

class InputChannel():
    def __init__(self) -> None:
        pass

    def receive(self, postdata):
        if "value" in postdata:
            value = postdata["value"]
            if "form" in value and value["form"] == "Travel" or 'Apply leave':
                postdata["text"] = "from " + value["from"] + " to " + value["to"]
                # postdata["textFormat"] = "plain"
                # postdata["channelData"].pop("legacy")
                # postdata["channelData"].pop("source")
                # postdata.pop("replyToId")
                # postdata.pop("value")

        return {
            "message": postdata.get("text", ""),
            "sender": "802983"
        }