from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.ChatWorkspace

def insert_mongo(data):
    # 디버깅
    print("insert_mongo 실행 ---------------------------------------")

    for i in range(len(data["elem_ids"])):
        db.ChanelVdbNav.insert_one({"_channel_id": data["channel_id"], "_elem_id": data["elem_ids"][i]})

def delete_mongo(channel_id):
    # 디버깅
    print("delete_mongo 실행 ---------------------------------------")

    try:
        query = {"_channel_id": channel_id}

        # 해당 채널의 row를 정보를 먼저 가져오고 나서 삭제
        rows = db.ChanelVdbNav.find(query)
        db.ChanelVdbNav.delete_many(query)

        # 임베딩 위치정보를 리스트 형태로 가공
        ids = []
        for row in rows:
            ids.append(row["_elem_id"])

        return ids
    
    except Exception as e:
        print(f"Error: {str(e)}")

# if __name__ == "__main__":
#     deleteTest("C050RN1M2R0")