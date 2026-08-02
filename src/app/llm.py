from langchain_openai import ChatOpenAI

from .config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0 ,
    api_key=OPENAI_API_KEY
)
