class configuration:
    path = ""
    host="http://localhost:"
    port = 6002
    #for local hosts
    # port = 5005
    restAPI = "http://10.32.0.93:5002/webhooks/rest/webhook"
    speechToTextURL = "http://10.32.0.93:1070/rest/SpeechToText"
    textToSpeechURL = "http://10.32.0.93:1070/rest/TextToSpeech"
    audioPath="http://10.32.0.93:8888/TSAudio/"

    # msBotServiceURL="https://smba.trafficmanager.net/amer/v3/"
    botapp_id= "f45b7283-db48-4680-9e46-0dcaf919335d"
    botapp_password= "hQl-1z-tM3CT6FYVwl-3sFnY.kvK8~9V-."

    # botapp_id= "a317700c-b7e0-4033-896e-3e18f1a66aa6"
    # botapp_password= "rDaxs6X-_-8bUktZZc1e3LBGYp123-GMKs"

    slack_token= "xoxb-1292780501328-1292791921264-WvQTTSJPOsELzkfhnQYaDPwA"
    slack_channel = ""
    # slack_token= "xoxb-1307403564740-1286499986663-TlWJey7Ec1Sk9osLULJm33u5"
    # stella - su49916.slack.com

    workerHost = "http://rasa-worker:5005/"