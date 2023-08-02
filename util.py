import datetime
import csv
import os

def unix_to_utc(ts):
    # 예를들어 1688391782.799519를 변환하게 되면 나중에 역변환 할때 .0799519 부분이 누락됨. 
    utc_time = datetime.datetime.fromtimestamp(float(ts))
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")

def utc_to_unix(ts):
    utc_time = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    unix_time = (utc_time - datetime.datetime(1970, 1, 1)).total_seconds()
    return unix_time

def messages_to_csv(channel_id, channel_name, messages, user_id = "youbin"):
    # 디버깅
    print("messages_to_csv 실행 ---------------------------------------")

    file_path = f"./{user_id}/{channel_id}/{channel_name} 채널 메시지 기록.csv"
    if not os.path.exists(f"./{user_id}/{channel_id}"):
        os.makedirs(f"./{user_id}/{channel_id}")

    datas = []
    for message in messages:
        data = {
            "메시지 ID": message["client_msg_id"],
            "채널 ID": channel_id,
            "채널 이름": channel_name,
            "작성자 ID": message["user_id"],
            "작성자 이름": message["user_name"],
            "메시지 내용": message["text"],
            "작성 시간": message["ts"]
        }
        datas.append(data)

    try:
        with open(file_path, "w", newline = "", encoding = "utf-8") as file:
            field_names = ["메시지 ID", "채널 ID", "채널 이름", "작성자 ID", "작성자 이름", "메시지 내용", "작성 시간"]
            
            writer = csv.DictWriter(file, fieldnames = field_names)
            writer.writeheader()

            for data in datas:
                writer.writerow(data)

        return file_path
    
    except Exception as e:
        print(f"Error: {str(e)}")

def delete_channel_csv(channel_id, channel_name, user_id = "youbin"):
    # 디버깅
    print("delete_channel_csv 실행 ---------------------------------------")

    file_path = f"./{user_id}/{channel_id}/{channel_name} 채널 메시지 기록.csv"

    try:
        os.remove(file_path)
        os.rmdir(f"./{user_id}/{channel_id}")
        print(f"File has been deleted successfully.")

        return True
    
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")

        return False
    
    except Exception as e:
        print(f"Error occurred while deleting the file: {str(e)}")

        return False


# def update_channel_csv(channel_id, channel_name, message):
#     exist_file = f"./{SOURCE_DIRECTORY}/{channel_name} 채널 메시지 내역.csv"

#     new_data = {
#         "메시지 ID": message["client_msg_id"],
#         "채널 ID": channel_id,
#         "채널 이름": channel_name,
#         "작성자 ID": message["user_id"],
#         "작성자 이름": message["user_name"],
#         "메시지 내용": message["text"],
#         "작성 시간": message["ts"]
#     }

#     with open(exist_file, "a", newline = "", encoding = "utf-8") as file:
#         fieldnames = ["메시지 ID", "채널 ID", "채널 이름", "작성자 ID", "작성자 이름", "메시지 내용", "작성 시간"]

#         writer = csv.DictWriter(file, fieldnames = fieldnames)
#         writer.writerow(new_data)
    
#     ingest_one_document(channel_id, exist_file)