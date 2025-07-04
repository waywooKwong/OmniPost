from langchain_google_genai import ChatGoogleGenerativeAI
from LLM_Choose import init_environment
import os

 # 配置代理环境变量
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

llm = ChatGoogleGenerativeAI(
                api_key="AIzaSyC399S3ImK3BILm2WhVRQnTkIdDYv0Shd0",
                model="gemini-2.0-flash",
                temperature=0.7,
                convert_system_message_to_human=True
            )

response = llm.predict("你好，介绍一下你自己")
print(response)
