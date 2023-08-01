from flask import Flask, request, make_response, Response
from flask_cors import CORS
from slackAPI import get_channel_messages, get_channel_name, get_user_name
from gpt import ask_gpt
import json
from mongo import delete_mongo
from embedding import ingest_channel, delete_chroma, check_db
from util import messages_to_csv, delete_channel_csv, unix_to_utc
from datetime import datetime
import time
from collections import deque

app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)

SLACK_EVENTS = deque()

@app.route("/api/uploadChannel", methods = ["POST"])
def upload_slack_channel():
  # 디버깅
  print("upload_slack_channel 실행 ---------------------------------------")

  # 전달받은 정보
  user_id = request.json.get("userId")  
  channel_id = request.json.get("channelId")

  # channel_id로 history 긁어와서 csv 파일 만들고 임베딩
  channel_name = get_channel_name(channel_id)
  messages = get_channel_messages(channel_id)
  file_path = messages_to_csv(channel_id, channel_name, messages, user_id)
  result = ingest_channel(channel_id, file_path, user_id)

  if result == True:
    return {"result": "success", "channelName": channel_name}
  else:
    return {"result": "fail"}
  
@app.route("/api/deleteChannel", methods = ["POST"])
def delete_slack_channel():
  # 디버깅
  print("delete_slack_channel 실행 ---------------------------------------")

  # 전달받은 정보
  user_id = request.json.get("userId")
  channel_id = request.json.get("channelId")

  # 모든 DB에서 삭제
  ids = delete_mongo(channel_id)
  result = True if delete_chroma(channel_id, ids, user_id) and delete_channel_csv(channel_id, get_channel_name(channel_id), user_id) else False

  if result == True:
    return {"result": "success", "channelName": get_channel_name(channel_id)}
  else:
    return {"result": "fail"}
  
@app.route("/api/chatChannel", methods = ["POST"])
def chat_in_channel():
  # 디버깅
  print("chat_in_channel 실행 ---------------------------------------")

  # 전달받은 정보
  user_id = request.json.get("userId")
  channel_id = request.json.get("channelId")
  question = request.json.get("question")

  # gpt에게 응답받기
  answer = ask_gpt(channel_id, question, user_id)

  if answer:
    return {"result": "success", "answer": answer}
  else:
    return {"result": "fail"}
  
@app.route("/api/checkChannel", methods = ["POST"])
def check_collection():
  # 디버깅
  print("check_collection 실행 ---------------------------------------")
  
  # 전달받은 정보
  user_id = request.json.get("userId")
  channel_id = request.json.get("channelId")

  answer = check_db(channel_id, user_id)

  if answer:
    return {"result": "success", "answer": answer}
  else:
    return {"result": "fail"}

@app.route("/slack/events", methods = ["POST"])
def slack_events():
  # 디버깅
  print("slack_events 실행 ---------------------------------------")

  slack_event = json.loads(request.data)
  if "challenge" in slack_event:
      return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

  if "event" in slack_event and slack_event["event"]["type"] == "message":
      return message_handler(slack_event["event"])
  
  return make_response("There are no slack request events", 404, {"X-Slack-No-Retry": 1})

def message_handler(event):
  # 디버깅
  print("message_handler 실행 ---------------------------------------")

  if event.get("subtype") == None:
    dto = {
      "client_msg_id": event["client_msg_id"],
      "user_id": event["user"],
      "user_name": get_user_name(event["user"]),
      "text": event["text"],
      "ts": unix_to_utc(event["ts"]),
    }
    SLACK_EVENTS.append(dto)

    return dto

    return make_response("ok", 200, )

@app.route("/stream")
def stream():

  def get_data():
    while True:
      if SLACK_EVENTS:
        dto = json.dumps(SLACK_EVENTS.popleft()).encode("utf-8")
        yield dto

  return Response(get_data(), mimetype = "text/event-stream")

# @app.route("/test", methods = ["POST"])
# def append_message():
#   dto = {
#       "client_msg_id": event["client_msg_id"],
#       "user_id": event["user"],
#       "user_name": get_user_name(event["user"]),
#       "text": event["text"],
#       "ts": unix_to_utc(event["ts"]),
#     }
#   user_id = request.json.get("userId")
#   channel_id = request.json.get("channelId")
#   question = request.json.get("question")
  
# def update_slack_channel(message):
#   dto = {
#     "client_msg_id": message["client_msg_id"],
#     "user_id": message["user"],
#     "user_name": get_user_name(message["user"]),
#     "text": message["text"],
#     "ts": unix_to_utc(message["ts"]),
#   }

#   # update_channel_csv(message["channel"], get_channel_name(message["channel"]), dto)

if __name__ == "__main__":
  app.run(host = "localhost", port = "5000", debug = True)