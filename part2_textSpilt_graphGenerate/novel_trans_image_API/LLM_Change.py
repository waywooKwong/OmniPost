"""
fastapi 接口，用于更换大模型
 前端传入供应商名称，模型名称与api_key
 后端更新config.yaml文件
 返回成功信息
 接口一：选择默认模型，接收前端信息，更新config.yaml文件，然后发送简单测试，返回模型是否正常工作
 接口二：选择备用模型，接收前端信息，更新config.yaml文件，然后发送简单测试，返回模型是否正常工作
"""

import os
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from LLM_Choose import get_model_by_name, init_environment

app = FastAPI(title="LLM模型管理API", description="用于切换和测试大语言模型")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 定义请求模型
class ModelChangeRequest(BaseModel):
    provider: str  # 供应商名称，如 "google" 或 "zhipu"
    model_name: str  # 模型名称，如 "gemini-2.5-pro-exp-03-25"
    api_key: str  # API密钥

def get_config_path():
    """获取配置文件路径"""
    return os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
    """加载配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置文件失败: {str(e)}")

def save_config(config):
    """保存配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置文件失败: {str(e)}")

def test_model(model_name):
    """测试模型是否正常工作"""
    try:
        # 初始化环境
        init_environment()
        
        # 获取模型实例
        model = get_model_by_name(model_name)
        
        # 发送简单测试消息
        response = model.invoke("你好，请用一句话回应我")
        
        # 检查响应
        content = response.content if hasattr(response, 'content') else str(response)
        return {"success": True, "message": f"模型测试成功", "response": content}
    except Exception as e:
        return {"success": False, "message": f"模型测试失败: {str(e)}"}

@app.post("/set_default_model")
async def set_default_model(request: ModelChangeRequest):
    """设置默认模型"""
    config = load_config()
    
    # 检查提供的模型是否在可用模型列表中
    if request.model_name not in config.get("available_models", []):
        raise HTTPException(status_code=400, detail=f"模型 {request.model_name} 不在可用模型列表中")
    
    # 更新API密钥
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][request.provider] = request.api_key
    
    # 更新默认模型
    config["default_model"] = request.model_name
    
    # 保存配置
    save_config(config)
    
    # 测试模型
    test_result = test_model(request.model_name)
    
    return {
        "success": test_result["success"],
        "message": f"默认模型已更新为 {request.model_name}",
        "test_result": test_result
    }

@app.post("/set_backup_model")
async def set_backup_model(request: ModelChangeRequest):
    """设置备用模型"""
    config = load_config()
    
    # 检查提供的模型是否在可用模型列表中
    if request.model_name not in config.get("available_models", []):
        raise HTTPException(status_code=400, detail=f"模型 {request.model_name} 不在可用模型列表中")
    
    # 更新API密钥
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][request.provider] = request.api_key
    
    # 更新备用模型
    config["backup_model"] = request.model_name
    
    # 保存配置
    save_config(config)
    
    # 测试模型
    test_result = test_model(request.model_name)
    
    return {
        "success": test_result["success"],
        "message": f"备用模型已更新为 {request.model_name}",
        "test_result": test_result
    }

@app.get("/get_model_config")
async def get_model_config():
    """获取当前模型配置"""
    config = load_config()
    
    return {
        "default_model": config.get("default_model"),
        "backup_model": config.get("backup_model"),
        "available_models": config.get("available_models", [])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)