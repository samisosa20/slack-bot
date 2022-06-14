import json
import requests
from slack_sdk.errors import SlackApiError
from flask import Response

numbers = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]


def getChannelId(slack_client, channel_name):
    try:
        result = slack_client.usergroups_list()
        print(result)
    except SlackApiError as e:
        print(f"Error: {e}")
        return False


def sendMessage(slack_client, msg, blocks, channel):
    # ID of channel you want to post message to

    try:
        # Call the conversations.list method using the WebClient
        result = slack_client.chat_postMessage(
            channel=channel,
            text=msg,
            blocks=blocks["blocks"] if blocks is not None else None
            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)
        return Response("Data sended", 200)

    except SlackApiError as e:
        print(e)
        return Response("Data can't be send", 403)


def formRadioButton(slack_client, msg, channel, options):
    formTemplate = open('../templates/radioButton.json')
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
    return sendMessage(slack_client, msg, jsonTemplate, channel)


def formPoll(slack_client, msg, channel, options):
    formTemplate = open('templates/poll.json')
    jsonTemplate = json.load(formTemplate)
    jsonTemplate["blocks"][0]["text"]["text"] = msg
    for index, option in enumerate(options):
        jsonTemplate["blocks"].append({
            "type": "section",
            "text": {
                "type": option["type"] if "type" in option else "mrkdwn",
                "text": "{} {}".format(numbers[index + 1],option["text"]),
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": numbers[index + 1]
                },
                "value": option["value"] if "value" in option else option["text"]
            }
        },)
    return sendMessage(slack_client, msg, jsonTemplate, channel)


def setResponse(data):
    result = json.loads(data["payload"])["actions"]
    # Set Values
    resultUserName = json.loads(data["payload"])["user"]
    response_url = json.loads(data["payload"])["response_url"]

    # Get index for the answer
    getBlockId = json.loads(data["payload"])["actions"][0]["block_id"]
    blockId_index = next((index for (index, d) in enumerate(json.loads(
        data["payload"])["message"]["blocks"]) if d["block_id"] == getBlockId), None)

    # Create new Block
    auxBlock = json.loads(data["payload"])["message"]["blocks"]
    if (len(auxBlock) > blockId_index + 1):
        # If the block exited
        if ("elements" in auxBlock[blockId_index + 1]):
            userName_index = next((index for (index, d) in enumerate(
                auxBlock[blockId_index + 1]["elements"]) if d["text"] == "<@{}>,".format(resultUserName["id"])), None)
            if (userName_index == None):
                originalText = auxBlock[blockId_index]["text"]["text"].split("`")
                counter = int(originalText[1]) + 1
                auxBlock[blockId_index]["text"]["text"] = "{} `{}`".format(originalText[0], counter)
                auxBlock[blockId_index + 1]["elements"].append({
                    "type": "mrkdwn",
                    "text": "<@{}>,".format(resultUserName["id"]),
                })
            else:
                # Delete user
                if (userName_index == 0 and len(auxBlock[blockId_index + 1]["elements"]) == 1):
                    originalText = auxBlock[blockId_index]["text"]["text"].split("`")
                    auxBlock[blockId_index]["text"]["text"] = "{}".format(originalText[0])
                    auxBlock.pop(blockId_index + 1)
                else:
                    originalText = auxBlock[blockId_index]["text"]["text"].split("`")
                    counter = int(originalText[1]) - 1
                    auxBlock[blockId_index]["text"]["text"] = "{} `{}`".format(originalText[0], counter)
                    auxBlock[blockId_index + 1]["elements"].pop(userName_index)
        else:
            originalText = auxBlock[blockId_index]["text"]["text"].split("`")
            if (len(originalText) > 1):
                counter = int(originalText[1]) + 1
            else:
                counter = 1
            auxBlock[blockId_index]["text"]["text"] = "{} `{}`".format(originalText[0], counter)
            auxBlock.insert(blockId_index + 1, {
                "type": "context",
                "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "<@{}>,".format(resultUserName["id"]),
                        },
                ]
            })
    else:
        originalText = auxBlock[blockId_index]["text"]["text"].split("`")
        if (len(originalText) > 1):
            counter = int(originalText[1]) + 1
        else:
            counter = 1
        auxBlock[blockId_index]["text"]["text"] = "{} `{}`".format(originalText[0], counter)
        auxBlock.append({
        "type": "context",
        "elements": [
                {
                    "type": "mrkdwn",
                    "text": "<@{}>,".format(resultUserName["id"]),
                },
        ]
    })

    dataSendJson = {"blocks": auxBlock}
    return requests.post(response_url, json=dataSendJson)
