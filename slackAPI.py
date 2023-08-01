from slack_sdk import WebClient
import time
import os
from dotenv import load_dotenv
from util import unix_to_utc

load_dotenv()

MY_NAME = os.environ["MY_NAME"]
client = WebClient(token = os.environ["SLACK_USER_TOKEN"])

def get_user_name(user_id):
    try:
        response = client.users_info(user = user_id)
    except Exception as e:
        print(f"Error: {str(e)}")

    user_name = response["user"]["real_name"]

    return user_name

def get_channel_name(channel_id):
    try:
        response = client.conversations_info(channel = channel_id)
    except Exception as e:
        print(f"Error: {str(e)}")
    
    channel_name = response["channel"]["name"]

    return channel_name

def get_replies(channel_id, ts):
    try:
        messages = []

        cursor = None
        while True:
            thread_replies = client.conversations_replies(channel = channel_id, ts = ts, cursor = cursor)

            for message in thread_replies["messages"]:
                if (message["type"] == "message"):
                    if message.get("user_profile"):
                        user_name = message["user_profile"]["real_name"]
                    else:
                        user_name = MY_NAME

                    messages.append((message["text"], message["client_msg_id"], user_name, message["user"], message["thread_ts"]))

            if bool(thread_replies["has_more"]):
                cursor = thread_replies["response_metadata"]["next_cursor"]
            else:
                cursor = None

            if cursor is None:
                break
            else:
                time.sleep(1.2)
        
        return messages
    
    except Exception as e:
        print(f"Error: {str(e)}")

def get_channel_messages(channel_id):
    try:
        message_list = []

        cursor = None
        while True:
            response = client.conversations_history(channel = channel_id, cursor = cursor)
            messages = response["messages"]
            
            for message in messages:
                if message.get("client_msg_id"):
                    if message.get("user_profile"):
                        user_name = message["user_profile"]["real_name"]
                    else:
                        user_name = MY_NAME

                    if message.get("thread_ts"):
                        for text_, msg_id_, user_name_, user_id_, ts_ in reversed(get_replies(channel_id, message["ts"])):
                            dto = {
                                "client_msg_id": msg_id_,
                                "user_id": user_id_,
                                "user_name": user_name_,
                                "text": text_.replace("\n", " "),
                                "ts": unix_to_utc(ts_),
                            }
                            message_list.append(dto)
                    else:
                        dto = {
                            "client_msg_id": message["client_msg_id"],
                            "user_id": message["user"],
                            "user_name": user_name,
                            "text": message["text"].replace("\n", " "),
                            "ts": unix_to_utc(message["ts"]),
                        }
                        message_list.append(dto)

            if bool(response["has_more"]):
                cursor = response["response_metadata"]["next_cursor"]
            else:
                cursor = None

            if cursor is None:
                break
            else:
                time.sleep(1.2)
        
        return reversed(message_list)

    except Exception as e:
        print(f"Error: {str(e)}")