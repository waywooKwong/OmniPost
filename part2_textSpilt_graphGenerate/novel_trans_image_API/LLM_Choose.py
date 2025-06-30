"""统一管理模型"""
import os
import requests
from requests.adapters import DEFAULT_POOL_TIMEOUT
import yaml
import sys
from google import genai
from google.genai import types
from PIL import Image
from langchain_community.chat_models import ChatZhipuAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
# 如果需要其他模型，在这里导入
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic


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


def get_model_by_name(model_name):
    """
    根据模型名称获取对应的模型实例
    
    Args:
        model_name: 模型名称
    
    Returns:
        模型实例
    """
    config = load_config()
    
    # 确定模型所属的提供商
    provider = None
    for provider_name, provider_config in config.get("providers", {}).items():
        if model_name in provider_config.get("models", []):
            provider = provider_name
            break
    
    if not provider:
        print(f"未知的模型名称: {model_name}，使用默认模型 gemini-2.0-flash")
        return get_model_by_name("gemini-2.0-flash")
    
    # 获取厂家模板
    provider_template = config.get("provider_templates", {}).get(provider)
    if not provider_template:
        print(f"未知的提供商模板: {provider}，使用默认模型 gemini-2.0-flash")
        return get_model_by_name("gemini-2.0-flash")
    
    # 获取模型参数
    temperature = provider_template.get("temperature", 0.7)
    
    try:
        # 设置requests超时
        # 不直接修改DEFAULT_TIMEOUT，而是在创建模型实例时传递timeout参数
        
        # 根据提供商和模型名称创建相应的模型实例
        if provider == "google":
            # 确保Google API密钥已设置
            os.environ["GOOGLE_API_KEY"] = config.get("api_keys", {}).get("google", "")
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                convert_system_message_to_human=True,
                request_timeout=60
            )
        elif provider == "zhipu":
            # 确保智谱API密钥已设置
            os.environ["ZHIPUAI_API_KEY"] = config.get("api_keys", {}).get("zhipu", "")
            return ChatZhipuAI(
                model=model_name,
                temperature=temperature,
                request_timeout=60
            )
        elif provider == "deepseek":
            # 确保DeepSeek API密钥已设置
            os.environ["DEEPSEEK_API_KEY"] = config.get("api_keys", {}).get("deepseek", "")
            return ChatDeepSeek(
                model=model_name,
                temperature=temperature,
                request_timeout=60
            )
        # 可以继续添加其他提供商的处理逻辑
        # elif provider == "openai":
        #     os.environ["OPENAI_API_KEY"] = config.get("api_keys", {}).get("openai", "")
        #     return ChatOpenAI(
        #         model=model_name,
        #         temperature=temperature
        #     )
        # elif provider == "anthropic":
        #     os.environ["ANTHROPIC_API_KEY"] = config.get("api_keys", {}).get("anthropic", "")
        #     return ChatAnthropic(
        #         model=model_name,
        #         temperature=temperature
        #     )
        else:
            print(f"不支持的提供商: {provider}")
            # 尝试使用备用模型
            backup_model = config.get("backup_model")
            if backup_model and backup_model != model_name:
                print(f"尝试使用备用模型: {backup_model}")
                return get_model_by_name(backup_model)
            else:
                raise ValueError(f"不支持的提供商: {provider}，且没有可用的备用模型")
    except Exception as e:
        print(f"创建模型实例失败: {e}")
        # 尝试备用模型
        backup_model = config.get("backup_model")
        if backup_model and backup_model != model_name:
            print(f"尝试使用备用模型: {backup_model}")
            return get_model_by_name(backup_model)
        else:
            raise Exception(f"创建模型实例失败且没有可用的备用模型: {e}")


def get_default_llm():
    """
    从config.yaml中读取默认模型后返回
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
    provider_templates = config.get("provider_templates", {})
    
    # 设置代理
    proxy = config.get("proxy", {})
    http_proxy = proxy.get("http", "")
    https_proxy = proxy.get("https", "")
    
    # 只在代理不为空时设置环境变量
    if http_proxy:
        os.environ["HTTP_PROXY"] = http_proxy
    if https_proxy:
        os.environ["HTTPS_PROXY"] = https_proxy
    
    # 为requests库设置代理
    if http_proxy:
        os.environ["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"
    
    # 设置各个提供商的API密钥
    for provider_name, provider_config in provider_templates.items():
        env_var = provider_config.get("env_var")
        if env_var and provider_name in api_keys:
            os.environ[env_var] = api_keys[provider_name]
    
    return True


