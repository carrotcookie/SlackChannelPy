import uuid
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from dotenv import load_dotenv
from mongo import insert_mongo

load_dotenv()

# .env에서는 무조건 문자열로 받아오는 듯....
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LOADER_MAPPING = {
    ".csv": (CSVLoader, {"encoding": "utf-8"}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf-8"}),
}

def load_single_file(file_path: str):
    # 디버깅
    print("load_single_file 실행 ---------------------------------------")

    # 확장자 판단
    ext = "." + file_path.rsplit(".", 1)[-1]

    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()

    raise ValueError(f"Unsupported file extension '{ext}'")

def make_id(texts, channel_id):
    # 디버깅
    print("make_id 실행 ---------------------------------------")

    data = {
        "channel_id": channel_id,
        "elem_ids": [],
    }
        
    for _ in range(len(texts)):
        data["elem_ids"].append(str(uuid.uuid1()))
    
    return data

def ingest_channel(channel_id, file_path, user_id = "youbin"):
    # 디버깅
    print("ingest_channel 실행 ---------------------------------------")

    try:
        print(f"Create vectorstore at {user_id}/db")
        persist_directory = f"{user_id}/db"

        db = Chroma(persist_directory = persist_directory, embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY), collection_name = channel_id)

        documents = load_single_file(file_path = file_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = CHUNK_SIZE, chunk_overlap = CHUNK_OVERLAP)
        texts = text_splitter.split_documents(documents)

        data = make_id(texts, channel_id)
        db.add_documents(documents = texts, ids = data["elem_ids"])
        insert_mongo(data) # mongoDB에 넣기

        db.persist()
        db = None

        print("Ingestion complete! You can now run privateGPT.py to query your documents")

        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")

        return False
    
def delete_chroma(channel_id, ids, user_id = "youbin"):
    # 디버깅
    print("delete_chroma 실행 ---------------------------------------")

    try:
        persist_directory = f"{user_id}/db"

        # 전달받은 id에 해당하는 임베딩 정보를 해당 컬렉션에서 삭제 후 적용
        vdb = Chroma(persist_directory = persist_directory, embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY), collection_name = channel_id)
        print(111111111111111111)
        vdb.delete(ids = ids)
        print(222222222222222222)
        vdb.persist()
        print(333333333333333333)

        return True
    
    except Exception as e:
        print(f"Error: {e}")

        return False
    
def check_db(channel_id, user_id = "youbin"):
    # 디버깅
    print("check_db 실행 ---------------------------------------")

    persist_directory = f"{user_id}/db"

    db = Chroma(persist_directory = persist_directory, embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY), collection_name = channel_id)
    collection = db.get()

    return collection
    
# def ingest_one_document(slackChannel, file_path):
#     try:
#         print(f"Create vectorstore at {PERSIST_DIRECTORY}")

#         db = Chroma(persist_directory = PERSIST_DIRECTORY, embedding_function = OpenAIEmbeddings(), collection_name = slackChannel)

#         documents = load_single_file(file_path = file_path)
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size = CHUNK_SIZE, chunk_overlap = CHUNK_OVERLAP)
#         texts = text_splitter.split_documents([documents[-1]])

#         data = make_id([texts[-1]], slackChannel)

#         # print("----------------------------------------------------------------")
#         # print(data)
#         # print("----------------------------------------------------------------")

#         db.add_documents(documents = texts, ids = data["elem_ids"])
#         insertTest(data) # mongoDB에 넣기

#         db.persist()


#         print(db.get())

#         db = None

#         print(f"Ingestion complete! You can now run privateGPT.py to query your documents")

#         return True
    
#     except Exception as e:
#         print(e)

#         return False