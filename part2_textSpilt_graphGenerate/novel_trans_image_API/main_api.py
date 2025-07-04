"""
主API文件，整合所有接口到一个FastAPI应用中
启动此文件即可启动所有API服务
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# 导入各模块
from LLM_Choose import get_model_by_name, init_environment, get_default_llm, get_backup_llm
from LLM_Change import ModelChangeRequest, load_config, save_config, test_model
from Role_Extract_API import RoleExtractor
from Novel_Handel_Api import NovelSceneGenerator
from Scene_Excrat import SceneMemoryAgent, extract_json_from_text
from SD_Image import SD_Generate

# 创建FastAPI应用
app = FastAPI(
    title="小说转画像系统API",
    description="整合系统的所有API接口，包括模型切换、角色提取、场景分镜和图像生成等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 初始化环境
init_environment()

# 创建场景记忆代理实例
scene_memory_agent = SceneMemoryAgent()

# ===== 模型管理API =====
@app.post("/set_default_model")
async def set_default_model(request: ModelChangeRequest):
    """设置默认模型"""
    config = load_config()
    
    # 更新API密钥
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][request.provider] = request.api_key
    
    # 确保providers中有该模型
    if "providers" not in config:
        config["providers"] = {}
    
    if request.provider not in config["providers"]:
        # 如果供应商不存在，添加供应商配置
        config["providers"][request.provider] = {"models": []}
    
    # 确保providers.models列表中有该模型
    if "models" not in config["providers"][request.provider]:
        config["providers"][request.provider]["models"] = []
        
    if request.model_name not in config["providers"][request.provider]["models"]:
        config["providers"][request.provider]["models"].append(request.model_name)
    
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
    
    # 更新API密钥
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][request.provider] = request.api_key
    
    # 确保providers中有该模型
    if "providers" not in config:
        config["providers"] = {}
    
    if request.provider not in config["providers"]:
        # 如果供应商不存在，添加供应商配置
        config["providers"][request.provider] = {"models": []}
    
    # 确保providers.models列表中有该模型
    if "models" not in config["providers"][request.provider]:
        config["providers"][request.provider]["models"] = []
        
    if request.model_name not in config["providers"][request.provider]["models"]:
        config["providers"][request.provider]["models"].append(request.model_name)
    
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
        "providers": config.get("providers", {}),
        "provider_templates": config.get("provider_templates", {})
    }

# ===== 角色提取API =====
class TextContentRequest(BaseModel):
    content: str
    use_backup_model: bool = False
    project_id: str

@app.post("/role-extract")
async def extract_roles(
    file: UploadFile = File(...),
    use_backup_model: bool = Form(False),
    project_id: str = Form(...)
):
    """
    提取小说中的角色并生成角色画像提示词
    
    - **file**: 上传的小说文本文件
    - **use_backup_model**: 是否使用备用模型(默认为False，使用默认模型)
    - **project_id**: 工程编号，用于创建对应的工程文件夹
    
    返回:
        提取的角色信息JSON数据
    """
    # 初始化环境
    init_environment()
    
    # 保存上传的文件到项目目录
    project_files_dir = os.path.join("part2_textSpilt_graphGenerate/Projects", project_id, "files")
    os.makedirs(project_files_dir, exist_ok=True)
    
    temp_file_path = os.path.join(project_files_dir, file.filename)
    
    # 读取文件内容并保存
    content = await file.read()
    with open(temp_file_path, "wb") as f:
        f.write(content)
    
    try:
        # 处理小说
        extractor = RoleExtractor(
            novel_path=temp_file_path,
            use_backup_model=use_backup_model,
            project_id=project_id
        )
        result = extractor.process_novel()
        
        # 返回处理结果
        return {
            "success": True,
            "message": f"成功从 {file.filename} 中提取了 {len(result)} 个角色",
            "data": result,
            "project_id": project_id
        }
    except Exception as e:
        # 发生错误时返回错误信息
        raise HTTPException(status_code=500, detail=f"角色提取失败: {str(e)}")

@app.post("/role-extract-text")
async def extract_roles_from_text(request: TextContentRequest):
    """
    从纯文本内容中提取角色并生成角色画像提示词
    
    - **content**: 小说文本内容
    - **use_backup_model**: 是否使用备用模型(默认为False，使用默认模型)
    - **project_id**: 工程编号，用于创建对应的工程文件夹
    
    返回:
        提取的角色信息JSON数据
    """
    # 初始化环境
    init_environment()
    
    try:
        # 处理小说，直接传递文本内容
        extractor = RoleExtractor(
            text_content=request.content,
            use_backup_model=request.use_backup_model,
            project_id=request.project_id
        )
        result = extractor.process_novel()
        
        # 返回处理结果
        return {
            "success": True,
            "message": f"成功从文本内容中提取了 {len(result)} 个角色",
            "data": result,
            "project_id": request.project_id
        }
    except Exception as e:
        # 发生错误时返回错误信息
        raise HTTPException(status_code=500, detail=f"角色提取失败: {str(e)}")

# ===== 场景分镜API =====
class SceneGenerateRequest(BaseModel):
    project_id: str
    role_info: Dict[str, Dict[str, str]]

@app.post("/generate-scenes")
async def generate_scenes(request: SceneGenerateRequest):
    """
    根据项目ID和角色信息，生成小说场景分镜描述
    
    - **project_id**: 项目ID
    - **role_info**: 角色信息JSON对象
    """
    try:
        # 初始化场景生成器
        generator = NovelSceneGenerator(
            project_id=request.project_id,
            role_info=request.role_info
        )
        
        # 处理小说并生成场景
        scenes = generator.process_novel()
        
        # 保存场景到JSON文件
        output_path = generator.save_scenes_to_json()
        
        # 读取保存的JSON文件内容
        with open(output_path, 'r', encoding='utf-8') as f:
            scenes_data = json.load(f)
            
        # 检查是否有单个场景带有错误消息
        is_error = False
        if len(scenes) == 1 and "错误" in scenes[0].get("description", ""):
            is_error = True
            
        # 返回场景数据和元信息
        return {
            "status": "success" if not is_error else "partial_success",
            "message": f"成功生成 {len(scenes)} 个场景" if not is_error else "生成过程中遇到错误，但返回了部分结果",
            "scenes_count": len(scenes),
            "data": scenes_data  # 返回完整的场景数据
        }
    except Exception as e:
        import time
        error_message = str(e)
        print(f"API错误: {error_message}")
        # 创建一个最小可用响应
        error_data = {
            "metadata": {
                "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": error_message
            },
            "scenes": [{
                "description": f"处理失败，请重试。错误: {error_message[:100]}...",
                "original_text": "API错误",
                "roles": []
            }]
        }
        # 返回错误但提供基本结构
        return {
            "status": "error",
            "message": f"场景生成失败: {error_message[:200]}...",
            "scenes_count": 1,
            "data": error_data
        }

# ===== 场景提示词生成API =====
class SceneRequest(BaseModel):
    project_id: str
    description: str
    original_text: str
    use_backup_model: bool = False

class SceneResponse(BaseModel):
    prompt: str
    status: str = "success"
    message: str = "提示词生成成功"

# 修改：同时提供两个路径，确保兼容性
# @app.post("/generate_scene_prompt", response_model=SceneResponse)
@app.post("/generate-scene-prompt", response_model=SceneResponse)
async def generate_scene_prompt(request: SceneRequest):
    """生成场景提示词API接口"""
    try:
        # 初始化环境
        init_environment()
        # 使用场景记忆代理生成提示词
        prompt = scene_memory_agent.generate_scene_prompt(
            description=request.description,
            original_text=request.original_text,
            project_id=request.project_id,
            use_backup_model=request.use_backup_model
        )
        
        return SceneResponse(
            prompt=prompt,
            status="success", 
            message="提示词生成成功"
        )
    except Exception as e:
        # 发生异常，返回错误响应
        raise HTTPException(
            status_code=500,
            detail=f"生成提示词失败: {str(e)}"
        )

# ===== StableDiffusion图像生成API =====
class SDGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    batch_size: int = Field(default=1, ge=1, le=4)
    seed: int = Field(default=-1)
    sampler_name: str = "Euler a"
    use_regional_prompter: bool = False
    regional_prompt_mode: str = "Columns"
    regional_prompt_ratios: str = "1,1"
    enable_hr: bool = False
    model_name: str = "wolfboys2D_v10.safetensors [62d679b7a0]"
    save_dir: Optional[str] = None

class SDGenerateResponse(BaseModel):
    images: List[str]
    seeds: List[int]
    info: Dict[str, Any]
    save_paths: Optional[List[str]] = None

# 修改：提供两个端点，一个用下划线，一个用连字符
# @app.post("/generate", response_model=SDGenerateResponse)
@app.post("/sd-generate", response_model=SDGenerateResponse)
async def generate_image(request: SDGenerateRequest):
    try:
        sd = SD_Generate()
        
        # 配置生成参数
        sd.generate_prompt(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            batch_size=request.batch_size,
            seed=request.seed,
            sampler_name=request.sampler_name,
            use_regional_prompter=request.use_regional_prompter,
            regional_prompt_mode=request.regional_prompt_mode,
            regional_prompt_ratios=request.regional_prompt_ratios,
            enable_hr=request.enable_hr,
            model_name=request.model_name
        )
        
        # 获取图像
        sd.get_img()
        
        # 准备响应数据
        response_data = {
            "images": sd.r.get("images", []),
            "seeds": sd.seeds,
            "info": sd.info
        }
        
        # 如果指定了保存目录，则保存图像
        if request.save_dir:
            _, save_paths = sd.save_img(request.save_dir)
            response_data["save_paths"] = save_paths
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务
if __name__ == "__main__":
    print("启动所有API服务...")
    print("访问 http://localhost:8090/docs 查看API文档")
    # 启动FastAPI服务
    uvicorn.run("main_api:app", host="0.0.0.0", port=8090, reload=True) 