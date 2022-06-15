import json, os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, Response, request, jsonify
from Hooks.auxiliar import sendMessage, formRadioButton, getChannelId, formPoll, setResponse

app = Flask(__name__)

# Set the token from the secret environment variables.
slack_client = WebClient(token="xoxb-14279150613-3581635289973-eH6kGVWPrPjzAgbyabIsGDmF")
#print(os.environ.get('SLACK_TOKEN') or "IbqJ6vQOe9lPT1zwwuWzcTjf")


@app.route('/author', methods=['GET'])
def author():
    return Response("Sammy Guttman.")

@app.route('/send/message', methods=['POST'])
def sendText():
    data = json.loads(request.data)
    if("message" in data):
        if("channel" in data):
            channel = data["channel"] if "channel" in data else None
            return sendMessage(slack_client, data["message"], None, channel)
        else:
            return Response("channel is missing", 403)
    else:
        return Response("message is missing", 403)

@app.route('/list/message/<channel>', methods=['GET'])
def listMessage(channel):
    result = slack_client.conversations_list()
    listUserFilter = list(filter(lambda x: x["name"] == channel, result["channels"]))
    resultConversations = slack_client.conversations_history(channel=listUserFilter[0]["id"])
    print(resultConversations)
    return Response("ok")

@app.route('/delete/message', methods=['POST'])
def deleteMessage():
    print(request.data)
    data = json.loads(request.data)
    if("ts" in data):
        if("channel" in data):
            channel = data["channel"] if "channel" in data else None
            slack_client.chat_delete(channel=channel, ts=data["ts"])
            return Response("Deleted!")
        else:
            return Response("channel is missing", 403)
    else:
        return Response("ts is missing", 403)

@app.route('/test/poll', methods=['POST'])
def testMessage():
    print(json.loads(request.data))

@app.route('/send/questions/radio', methods=['POST'])
def sendQuestionRadioButtons():
    data = json.loads(request.data)
    if("message" in data):
        if("channel" in data):
            if("options" in data):
                return formRadioButton(slack_client, data["message"], data["channel"], data["options"])
            else:
                return Response("options is missing", 403)
        else:
            return Response("channel is missing", 403)
    else:
        return Response("message is missing", 403)

@app.route('/send/poll', methods=['POST'])
def sendQuestionPoll():
    data = json.loads(request.data)
    if("message" in data):
        if("channel" in data):
            if("options" in data):
                return formPoll(slack_client, data["message"], data["channel"], data["options"])
            else:
                return Response("options is missing", 403)
        else:
            return Response("channel is missing", 403)
    else:
        return Response("message is missing", 403)

@app.route('/get/message', methods=['GET'])
def getMessageChannel():
    data = json.loads(request.data)
    if("channel" in data):
        channel_name = data["channel"]
        conversation_id = None
        try:
            getChannelId(slack_client, channel_name)
            result = slack_client.conversations_history(channel=channel_name)

            return Response(result["messages"])
        except SlackApiError as e:
            return Response(f"Error: {e}", 403)
    else:
        return Response("channel is missing", 403)

@app.route('/response/poll', methods=['POST'])
def responsePoll():
    data = request.form.to_dict()
    res = setResponse(data)
    print(res)
    return Response(res)

@app.route('/', methods=['GET', 'POST'])
def sayHello():
    return Response("To get started, remix this project and check out the README file!")


if __name__ == "__main__":
    app.run(debug=True)
