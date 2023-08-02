import os
import argparse
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain import PromptTemplate, LLMChain
from collections import deque

load_dotenv()

TARGET_SOURCE_CHUNKS = os.environ["TARGET_SOURCE_CHUNKS"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PERSIST_DIRECTORY = os.environ["PERSIST_DIRECTORY"]

def ask_gpt(channel_id, question, user_id = "youbin"):
    # 디버깅
    print("ask_gpt 실행 ---------------------------------------")

    args = parse_arguments()
    persist_directory = f"./{user_id}/{PERSIST_DIRECTORY}"

    # 컬렉션 가져오기
    db = Chroma(persist_directory = persist_directory, embedding_function = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY), collection_name = channel_id)
    retriever = db.as_retriever(search_kwargs = {"k": TARGET_SOURCE_CHUNKS})

    # llm 정하고 컬렉션에 질문하기
    llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = "gpt-3.5-turbo", temperature = 0, streaming = True)
    qa = RetrievalQA.from_chain_type(llm = llm, chain_type = "stuff", retriever = retriever, return_source_documents = not args.hide_source)
    res = qa(question)

    # 응답
    answer, docs = res["result"], [] if args.hide_source else res["source_documents"]

    return answer

def summarize_gpt(messages: deque):
    # 디버깅
    print("summarize_gpt 실행 ---------------------------------------")

    template = """Question: {question}
    Answer: Let's think step by step."""

    names = ["박유빈", "이동근"]
    i = 0
    question = ""
    while messages:
        message = messages.popleft()
        question += f"{names[i % 2]}: {message['text']}\n"
        i += 1
    question += "여기까지의 내용을 요약해줘."

    print(question)

    prompt = PromptTemplate(template = template, input_variables = ["question"])
    llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = "gpt-3.5-turbo", temperature = 0)
    chain = LLMChain(prompt = prompt, llm = llm)

    return chain.run(question)

def parse_arguments():
    parser = argparse.ArgumentParser(description = 'privateGPT: Ask questions to your documents without an internet connection, '
                                                 'using the power of LLMs.')
    parser.add_argument("--hide-source", "-S", action = 'store_true',
                        help = 'Use this flag to disable printing of source documents used for answers.')

    parser.add_argument("--mute-stream", "-M",
                        action = 'store_true',
                        help = 'Use this flag to disable the streaming StdOut callback for LLMs.')

    return parser.parse_args()
