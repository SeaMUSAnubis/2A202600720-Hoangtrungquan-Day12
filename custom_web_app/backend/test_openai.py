import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    llm = ChatOpenAI(
        temperature=0, 
        model="openrouter/free", 
        openai_api_key="sk-or-v1-fakekey", 
        openai_api_base="https://openrouter.ai/api/v1"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("human", "test")
    ])
    chain = prompt | llm
    try:
        print("Invoking...")
        response = await chain.ainvoke({"question": "test"})
        print(response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
