"""统一管理模型"""
import os
import requests
import yaml
import importlib
from google import genai
from google.genai import types
from PIL import Image
from langchain_community.chat_models import ChatZhipuAI
from langchain_google_genai import ChatGoogleGenerativeAI


def load_config():
    """
    加载配置文件
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        # 返回默认配置
        return {
            "default_model": "gemini-2.5-pro-exp-03-25",
            "backup_model": "glm-4-flash"
        }


def get_zhupuai_model():
    """
    获取智谱AI模型实例
    """
    # zhipuai model
    zhipuai_chat_model = ChatZhipuAI(model="glm-4-flash")
    return zhipuai_chat_model


def get_gemini_2_5_flash_preview():
    """
    获取Gemini 2.5 Flash Preview模型实例
    """
    # 初始化ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-04-17",
        temperature=0.7
    )
    return llm

def get_gemini_2_flash():
    """
    获取Gemini 2.0 Flash模型实例
    """
    # 初始化ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7
    )
    return llm

def get_gemini_2_5_pro():
    """
    获取Gemini 2.5 Pro模型实例
    """
    # 初始化ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro-exp-03-25",
        temperature=0.7
    )
    return llm

def get_model_by_name(model_name):
    """
    根据模型名称获取对应的模型实例
    """
   
    # 如果动态加载失败，使用硬编码的映射
    model_mapping = {
        "glm-4-flash": get_zhupuai_model,
        "gemini-2.0-flash": get_gemini_2_flash,
        "gemini-2.5-flash-preview-04-17": get_gemini_2_5_flash_preview,
        "gemini-2.5-pro-exp-03-25": get_gemini_2_5_pro
    }
    
    if model_name in model_mapping:
        return model_mapping[model_name]()
    else:
        print(f"未知的模型名称: {model_name}，使用默认模型 gemini-2.0-flash")
        return get_gemini_2_flash()



def get_default_llm():
    """
    从congfig.yaml中读取默认模型后返回
    """
    config = load_config()
    default_model = config.get("default_model", "gemini-2.0-flash")
    return get_model_by_name(default_model)

def get_backup_llm():
    """
    获取备用模型后返回
    """
    config = load_config()
    backup_model = config.get("backup_model", "glm-4-flash")
    return get_model_by_name(backup_model)

def init_environment():
    """
    初始化环境，从配置文件加载API密钥并设置环境变量
    """
    config = load_config()
    api_keys = config.get("api_keys", {})
    providers = config.get("providers", {})
    
    # 设置代理
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
    
    # 设置各个提供商的API密钥
    for provider_name, provider_config in providers.items():
        env_var = provider_config.get("env_var")
        if env_var and provider_name in api_keys:
            os.environ[env_var] = api_keys[provider_name]
    
    return True


