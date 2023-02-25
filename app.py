# https://www.serverless.com/plugins/serverless-python-requirements
try:
    import unzip_requirements  # pyright: reportMissingImports=false
except ImportError:
    pass

import os
from slack_bolt import App

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
    process_before_response=True,
)

WORKSPACE_NAME = os.environ["WORKSPACE_NAME"]
DESTINATION_CHANNEL_ID = os.environ["DESTINATION_CHANNEL_ID"]


def build_message_url(message) -> str:
    message_id = f"p{message['ts'].replace('.', '')}"
    return (
        f"https://{WORKSPACE_NAME}.slack.com/archives/{message['channel']}/{message_id}"
    )


@app.event("message")
def transfer_message(message, say):
    # exclude bot
    if "bot_id" in message:
        return

    print(message)
    message_url = build_message_url(message)
    say(message_url, channel=DESTINATION_CHANNEL_ID)


# AWS Lambda handler
def handler(event, context):
    from slack_bolt.adapter.aws_lambda import SlackRequestHandler

    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


# run locally
if __name__ == "__main__":
    from slack_bolt.adapter.socket_mode import SocketModeHandler

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
