import json, os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, Response, request


app = Flask(__name__, template_folder='')

# Set the token from the secret environment variables.
slack_client = WebClient(token="xoxb-14279150613-3581635289973-iX250ygE4ZzmuL1A8aBXXuew")
#print(os.environ.get('SLACK_TOKEN') or "IbqJ6vQOe9lPT1zwwuWzcTjf")

def getChannelId(channel_name):
    try:
        result = slack_client.usergroups_list()
        print(result)
    except SlackApiError as e:
        print(f"Error: {e}")
        return False


def sendMessage(msg, blocks, channel):
    # ID of channel you want to post message to

    try:
        # Call the conversations.list method using the WebClient
        result = slack_client.chat_postMessage(
            channel=channel,
            text=msg,
            blocks= blocks["blocks"] if blocks is not None else None
            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)
        return Response("Data sended", 200)

    except SlackApiError as e:
        print(e)
        return Response("Data can't be send", 403)

def formRadioButton(msg, channel, options):
    formTemplate = open('templates/radioButton.json')
    jsonTemplate = json.load(formTemplate)
    jsonTemplate["blocks"][0]["text"]["text"] = msg
    listOption = []
    for option in options:
        listOption.append({
						"text": {
							"type": option["type"] if "type" in option else "plain_text",
							"text": option["text"],
							"emoji": True
						},
						"value": option["value"] if "value" in option else option["text"]
					})
    jsonTemplate["blocks"][0]["accessory"]["options"] = listOption
    print(jsonTemplate)
    return sendMessage(msg, jsonTemplate, channel)

@app.route('/author', methods=['GET'])
def author():
    return Response("Sammy Guttman.")

@app.route('/send/message', methods=['POST'])
def sendText():
    data = json.loads(request.data)
    if("message" in data):
        if("channel" in data):
            channel = data["channel"] if "channel" in data else None
            return sendMessage(data["message"], None, channel)
        else:
            return Response("channel is missing", 403)
    else:
        return Response("message is missing", 403)

@app.route('/send/questions/radio', methods=['POST'])
def sendQuestionRadioButtons():
    data = json.loads(request.data)
    if("message" in data):
        if("channel" in data):
            if("options" in data):
                return formRadioButton(data["message"], data["channel"], data["options"])
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
            getChannelId(channel_name)
            result = slack_client.conversations_history(channel=channel_name)

            return Response(result["messages"])
        except SlackApiError as e:
            return Response(f"Error: {e}", 403)
    else:
        return Response("channel is missing", 403)

@app.route('/', methods=['GET', 'POST'])
def main():
    return Response("To get started, remix this project and check out the README file!")


if __name__ == "__main__":
    app.run(debug=True)
