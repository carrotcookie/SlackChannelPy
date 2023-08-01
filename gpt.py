import os
import argparse
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

TARGET_SOURCE_CHUNKS = os.environ["TARGET_SOURCE_CHUNKS"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def ask_gpt(channel_id, question, user_id = "youbin"):
    # 디버깅
    print("ask_gpt 실행 ---------------------------------------")

    args = parse_arguments()
    persist_directory = f"{user_id}/db"

    # 컬렉션 가져오기
    db = Chroma(persist_directory = persist_directory, embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY), collection_name = channel_id)
    retriever = db.as_retriever(search_kwargs = {"k": TARGET_SOURCE_CHUNKS})

    # llm 정하고 컬렉션에 질문하기
    llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model_name = "gpt-3.5-turbo", temperature = 0, streaming = True)
    qa = RetrievalQA.from_chain_type(llm = llm, chain_type = "stuff", retriever = retriever, return_source_documents = not args.hide_source)
    res = qa(question)

    # 응답
    answer, docs = res["result"], [] if args.hide_source else res["source_documents"]

    return answer

def parse_arguments():
    parser = argparse.ArgumentParser(description = 'privateGPT: Ask questions to your documents without an internet connection, '
                                                 'using the power of LLMs.')
    parser.add_argument("--hide-source", "-S", action = 'store_true',
                        help = 'Use this flag to disable printing of source documents used for answers.')

    parser.add_argument("--mute-stream", "-M",
                        action = 'store_true',
                        help = 'Use this flag to disable the streaming StdOut callback for LLMs.')

    return parser.parse_args()