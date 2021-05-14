import requests
import json
import uuid
import urllib
import os
from os import path
from config  import configuration
from sanic.response import StreamingHTTPResponse, guess_type, HTTPResponse
from sanic.compat import Header, open_async
import logging
import urllib.request


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SpeechToText():

    def __init__(self):
        self.speechToTextURL = configuration.speechToTextURL
        self.textToSpeechURL = configuration.textToSpeechURL
        self.audioPath = configuration.audioPath
        self.audioHostPath = configuration.host + str(configuration.port)

    def sendMessageToSpeechBot(self, message):
        res = requests.post(self.speechToTextURL, json.dumps(message))
        return res.json()

    def sendMessageToTextBot(self, message):
        res = requests.post(self.textToSpeechURL, json.dumps(message))
        jsonRes = res.json()
        jsonRes['link'] = self.audioHostPath + "/webhooks/audio/"+jsonRes['link']
        return jsonRes

    def sendAudioToBot(self, audioFile):
        location = self.audioPath + audioFile
        # return self.sendAudioFiles(location)
        return self.audioFile(location, filename=location)


    def sendAudioFiles(self, location):

        status = 200
        chunk_size = 4096
        mime_type = None
        headers = None
        filename = None
        chunked = True
        _range = None

        """Return a streaming response object with file data.
    
        :param location: Location of file on system.
        :param chunk_size: The size of each chunk in the stream (in bytes)
        :param mime_type: Specific mime_type.
        :param headers: Custom Headers.
        :param filename: Override filename.
        :param chunked: Enable or disable chunked transfer-encoding
        :param _range:
        """
        headers = headers or {}
        if filename:
            headers.setdefault("Content-Disposition", f'attachment; filename="{filename}"')
        filename = filename or path.split(location)[-1]
        mime_type = mime_type or guess_type(filename)[0] or "text/plain"
        if _range:
            start = _range.start
        end = _range.end
        total = _range.total

        headers["Content-Range"] = f"bytes {start}-{end}/{total}"
        status = 206

        async def _streaming_fn(response):
            async with await open_async(location, mode="rb") as f:
                if _range:
                    await f.seek(_range.start)
                    to_send = _range.size
                    while to_send > 0:
                        content = await f.read(min((_range.size, chunk_size)))
                        if len(content) < 1:
                            break
                        to_send -= len(content)
                        await response.write(content)
                else:
                    while True:
                        content = await f.read(chunk_size)
                        if len(content) < 1:
                            break
                        await response.write(content)


        return StreamingHTTPResponse(
            streaming_fn=_streaming_fn,
            status=status,
            headers=headers,
            content_type=mime_type,
            chunked=chunked,
        )

    async def audioFile( self,
            location,
            status=200,
            mime_type=None,
            headers=None,
            filename=None,
            _range=None,
    ):
        """Return a response object with file data.

        :param location: Location of file on system.
        :param mime_type: Specific mime_type.
        :param headers: Custom Headers.
        :param filename: Override filename.
        :param _range:
        """
        headers = headers or {}
        # if filename:
        #     headers.setdefault(
        #         "Content-Disposition", f'attachment; filename="{filename}"'
        #     )
        filename = filename or path.split(location)[-1]

        with urllib.request.urlopen(location) as f:
            out_stream = f.read()



        # async with await open_async(location, mode="rb") as f:
        #     if _range:
        #         await f.seek(_range.start)
        #         out_stream = await f.read(_range.size)
        #         headers[
        #             "Content-Range"
        #         ] = f"bytes {_range.start}-{_range.end}/{_range.total}"
        #         status = 206
        #     else:
        #         out_stream = await f.read()

        mime_type = mime_type or guess_type(filename)[0] or "text/plain"
        return HTTPResponse(
            body=out_stream,
            status=status,
            headers=headers,
            content_type=mime_type,
        )





