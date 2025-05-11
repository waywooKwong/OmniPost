"""
从前端接收场景描述，生成场景提示词的API接口
"""

import json
import os
import time
import re
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from LLM_Choose import get_default_llm, get_backup_llm, init_environment

# 创建FastAPI应用
app = FastAPI(title="场景提示词生成API", description="将小说场景转换为Stable Diffusion提示词")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 请求模型
class SceneRequest(BaseModel):
    project_id: str
    description: str
    original_text: str
    use_backup_model: bool = False

# 响应模型
class SceneResponse(BaseModel):
    prompt: str
    status: str = "success"
    message: str = "提示词生成成功"

def extract_json_from_text(text: str) -> dict:
    """从文本中提取JSON，处理各种不规范的格式"""
    # 如果已经是字典，直接返回
    if isinstance(text, dict):
        return text
    
    # 处理可能的空响应
    if text is None or not str(text).strip():
        return {"prompt": ""}
    
    text = str(text).strip()
    
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试移除markdown代码块
    if "```" in text:
        # 提取代码块内容
        pattern = r"```(?:json)?(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
    
    # 尝试查找JSON对象
    pattern = r"\{.*\}"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # 如果无法解析，返回包含原始文本的字典
    return {"prompt": text}

class SceneMemoryAgent:
    """场景记忆代理，支持上下文记忆功能"""
    
    def __init__(self):
        """初始化记忆代理"""
        # 用户聊天历史记录字典，键为项目ID
        self.chat_histories = {}

    def _get_chat_history(self, project_id: str) -> List:
        """获取指定项目的聊天历史"""
        if project_id not in self.chat_histories:
            self.chat_histories[project_id] = []
        return self.chat_histories[project_id]

    def create_scene_extraction_prompt(self) -> ChatPromptTemplate:
        """创建场景提示词生成模板，包含历史对话上下文"""
        template = """
        你是一个专业的小说场景转Stable Diffusion提示词专家。请按以下规则生成场景提示词：

        【基础规则】
        1. 开头必须用括号标注人数及性别，如：(2 people:1.3, a boy and a girl)、(1 man:1.4)
        2. 使用简明英文词组（5-10个），用逗号分隔
        3. 禁止：人物外貌描写、情感描述、抽象概念、禁止写人的面部戴着什么东西，比如黑色眼罩遮住眼睛
        4. 禁止出现面部的遮挡物，比如戴着黑色眼罩，墨镜

        
        【注意事项】
        1. 必须结合上下文，保持连贯场景中人物的一致性，比如衣服颜色，头发颜色等等
        2. 遇到与上一个处理过的场景连贯起来的场景时，人物不需要改变特别多，可能只需要改变一下背景
        3. 必须明确指出人物的穿着，颜色，动作
        4. 如果有多个人，则不要写出其中一个人的鲜明特征，比如戴着黑色眼罩，墨镜等等，避免污染其他人
        5. 禁止出现句子
        6. 禁止出现对话内容
        7. 必须使用英文括号包裹需要强调的部分！！！！！！！！！！！
        8. 主要生成背景描写人物之间的互动即可；
        9. 如果没有人，则强调没有人。
       

        生成严格JSON格式：
            {{
                "prompt": "生成该场景的提示词，严格控制在10个英语单词以内"
            }}

        请中立处理敏感内容，确保符合政策。
        """
        
        human_template = """
        以下是历史对话记录:
        {chat_history}
        
        场景信息：
        描述: {description}
        原文: {original_text}
        
        请按照要求为此场景生成提示词。
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", human_template)
        ])

    def generate_scene_prompt(self, description: str, original_text: str, project_id: str, use_backup_model: bool = False) -> str:
        """为单个场景生成提示词，加入聊天历史记忆"""
        retries = 2  # 模型重试次数
        chat_history = self._get_chat_history(project_id)
        
        # 构建携带历史记录的提示模板
        prompt = self.create_scene_extraction_prompt()
        
        # 格式化聊天历史为文本
        chat_history_text = ""
        if chat_history:
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    chat_history_text += f"用户: {message.content}\n"
                elif isinstance(message, AIMessage):
                    chat_history_text += f"AI: {message.content}\n"
        
        # 选择主模型或备用模型
        llm = get_backup_llm() if use_backup_model else get_default_llm()
        
        for attempt in range(retries):
            try:
                # 使用带有聊天历史的链
                chain = prompt | llm
                response = chain.invoke({
                    "chat_history": chat_history_text,
                    "description": description,
                    "original_text": original_text
                })
                
                # 使用自定义的JSON提取函数
                content = response.content if hasattr(response, 'content') else response
                
                # 检查是否为空响应
                if content is None or not str(content).strip():
                    print(f"模型返回空响应，尝试第{attempt+1}次...")
                    if attempt == retries - 1:
                        print("模型多次返回空响应，将尝试使用备用模型...")
                        # 如果当前不是备用模型，则尝试使用备用模型
                        if not use_backup_model:
                            return self.generate_scene_prompt(description, original_text, project_id, True)
                        else:
                            return "(1 person) simple indoor scene"  # 最终失败时的默认值
                    time.sleep(1.5)
                    continue
                
                parsed_response = extract_json_from_text(content)
                
                # 添加数据完整性检查
                if not isinstance(parsed_response, dict):
                    raise ValueError("响应格式不正确")
                
                if "prompt" not in parsed_response:
                    # 如果没有prompt字段，但有其他内容，尝试使用整个内容作为prompt
                    if isinstance(content, str) and content.strip():
                        prompt_text = content.strip()
                    else:
                        raise ValueError("响应中缺少prompt字段")
                else:
                    prompt_text = parsed_response["prompt"]
                
                if not prompt_text or len(str(prompt_text).strip()) == 0:
                    raise ValueError("生成的提示词为空")
                
                # 处理换行符
                if isinstance(prompt_text, str):
                    prompt_text = prompt_text.replace("\\n", " ").replace("\n", " ")
                
                print(f"成功生成提示词: {str(prompt_text)[:50]}...")
                
                # 更新聊天历史
                chat_history.append(HumanMessage(content=f"请为场景生成提示词：{description}"))
                chat_history.append(AIMessage(content=prompt_text))
                
                # 保存生成的提示词到项目文件中
                self._save_prompt_to_file(project_id, description, original_text, prompt_text)
                
                return prompt_text
            
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(1.5)
                elif not use_backup_model:
                    # 如果主模型失败，尝试使用备用模型
                    print("主模型失败，尝试使用备用模型...")
                    return self.generate_scene_prompt(description, original_text, project_id, True)
        
        # 所有尝试都失败，返回默认提示词
        default_prompt = "(1 person) simple indoor scene"
        
        # 更新聊天历史
        chat_history.append(HumanMessage(content=f"请为场景生成提示词：{description}"))
        chat_history.append(AIMessage(content=default_prompt))
        
        # 保存默认提示词到项目文件
        self._save_prompt_to_file(project_id, description, original_text, default_prompt)
        
        return default_prompt

    def _save_prompt_to_file(self, project_id: str, description: str, original_text: str, prompt: str):
        """保存生成的提示词到项目文件中"""
        # 确保项目目录存在
        project_dir = f"part2_textSpilt_graphGenerate/Projects/{project_id}/role_message"
        os.makedirs(project_dir, exist_ok=True)
        
        # 提示词保存文件路径
        prompts_file = os.path.join(project_dir, "scene_prompts.json")
        
        # 读取现有提示词文件（如果存在）
        scene_prompts = {"scene_prompts": []}
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    scene_prompts = json.load(f)
            except json.JSONDecodeError:
                print(f"无法解析现有提示词文件，将创建新文件")
        
        # 添加新的提示词
        new_prompt = {
            "prompt": prompt,
            "description": description,
            "original_text": original_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "scene_prompts" not in scene_prompts:
            scene_prompts["scene_prompts"] = []
            
        scene_prompts["scene_prompts"].append(new_prompt)
        
        # 保存更新后的提示词文件
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(scene_prompts, f, ensure_ascii=False, indent=2)
            
        print(f"提示词已保存到 {prompts_file}")

# 创建全局场景记忆代理实例
scene_memory_agent = SceneMemoryAgent()

@app.post("/generate_scene_prompt", response_model=SceneResponse)
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

if __name__ == "__main__":
    import uvicorn
    # 启动FastAPI服务
    uvicorn.run("Scene_Excrat:app", host="0.0.0.0", port=8000, reload=True) 