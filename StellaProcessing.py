# request, Blueprint,
from sanic import Blueprint, response

# env = Environment(loader=PackageLoader('SpeechProcessing', 'templates'))

# from flask_socketio import SocketIO
REQUEST_API = Blueprint('request_api', __name__)

from src.botFramework import BotFramework
from src.rest import Rest
from src.speechToText import SpeechToText
from src.slack import SlackBot
from socketProcessing import SocketIOInput
from src.workerJob import workerJob



botframeworkAPI = BotFramework()
restAPI = Rest()
speechToTextAPI = SpeechToText()
SlackBotAPI = SlackBot()
workerJobAPI = workerJob()


def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API


socketio = SocketIOInput()
def get_sockets():
    return socketio.blueprint()



@REQUEST_API.route('/', methods=['GET'])
async def root(request):
    # template = env.get_template('VUE.html')
    # html_content = template.render()
    # return html(html_content)
    return 'Hello Stella Bot'
    # return await response.file('templates/VUE.html')

# @REQUEST_API.route('/js/<path:path>', methods=['GET'])
# async def send_js(request, path):
#     return await response.file('templates/js/'+ path)

## stella webhook
@REQUEST_API.route('/rest/webhook', methods=['POST'])
async def stellaWebhook(request):
    if request.method == 'POST':
        # check if the post request has the file part
        return response.json(restAPI.sendMessageToBot(request.json))

## stella botframework webhook
@REQUEST_API.route('/botframework/webhook', methods=['POST'])
async def stellaWebhook(request):
    if request.method == 'POST':
        # check if the post request has the file part
        await botframeworkAPI.sendMessageToBot(request.json)
        return response.json({"message":"OK"})

## stella webhook
@REQUEST_API.route('/slack/webhook', methods=['POST'])
async def stellaSlackWebhook(request):
    if request.method == 'POST':
        # check if the post request has channel message structure
        if request.json.get("challenge", None) != None:
            return response.text(request.json.get("challenge", None))
        # send message request to slack
        return await SlackBotAPI.sendMessageToBot(request)
        # return response.text("OK")


## stella speech to text webhook
@REQUEST_API.route('/speechToText/webhook', methods=['POST'])
async def stellaSpeechToTextWebhook(request):
    if request.method == 'POST':
        # check if the post request has the file part
        return response.json(speechToTextAPI.sendMessageToSpeechBot(request.json))

## stella text to speech webhook
@REQUEST_API.route('/textToSpeech/webhook', methods=['POST'])
async def stellaTextToSpeechWebhook(request):
    if request.method == 'POST':
        # check if the post request has the file part
        return response.json(speechToTextAPI.sendMessageToTextBot(request.json))

## stella text to speech webhook
@REQUEST_API.route('/audio/<path:path>', methods=['GET'])
async def stellaAudioWebhook(request, path):
    if request.method == 'GET':
        # check if the post request has the file part
        return await speechToTextAPI.sendAudioToBot(path)


## worker jobs
@REQUEST_API.route('/worker/<path:path>', methods=['GET'])
async def chatbotWorkerJob(request, path):
    if request.method == 'GET':
        # check if the post request has the file part
        return await response.json(workerJobAPI.statusOfWorker(path))
    elif request.method == 'POST':
        return await response.json(workerJobAPI.trainOfWorker(path))

    # elif request.method == 'DELETE':




# @REQUEST_API.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response

