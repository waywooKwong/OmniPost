"""统一管理模型"""
import os
import requests
from google import genai
from google.genai import types
from PIL import Image
from langchain_community.chat_models import ChatZhipuAI
from langchain_google_genai import ChatGoogleGenerativeAI
# 配置环境
def os_setenv():
    # 设置代理
    proxies = {
        "http": "http://127.0.0.1:7890",  
        "https": "http://127.0.0.1:7890"  
    }
    # 配置代理环境变量
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

    # 智普
    os.environ["ZHIPUAI_API_KEY"] = "60bbabbbfb654cfabea1ee3be31dd103.ZO16tosFmkQihzlY"

    #gemini
    # 设置Google API密钥
    os.environ["GOOGLE_API_KEY"] = "AIzaSyC93MxOUrGCH-VOMTM5JVW6tRvgGQy1XcE"


def get_zhupuai_model():
    # zhipuai model
    zhipuai_chat_model = ChatZhipuAI(model="glm-4-flash")
    return zhipuai_chat_model


def get_gemini_2_flash():
    # 初始化ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro-exp-03-25",
        temperature=0.7
    )
    return llm


#gemini绘图：
def get_gemini_photo(contents):
    client = genai.Client(api_key="AIzaSyC93MxOUrGCH-VOMTM5JVW6tRvgGQy1XcE")

    img_response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
    return img_response