from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import os
import asyncio

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取 API 密钥
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 显式传入 API 密钥
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp", google_api_key=gemini_api_key
)


async def main():
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=llm,
    )
    result = await agent.run()
    print(result)


asyncio.run(main())
