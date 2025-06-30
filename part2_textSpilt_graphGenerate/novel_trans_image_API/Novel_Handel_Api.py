import os
import json
import time
import re
import requests
import requests.exceptions
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from LLM_Choose import get_default_llm, get_backup_llm, init_environment


# 加载环境变量
load_dotenv()
init_environment()


app = FastAPI(title="小说场景分镜API", description="用于将小说文本拆分为多个场景，生成分镜头描述")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 请求模型
class SceneGenerateRequest(BaseModel):
    project_id: str
    role_info: Dict[str, Dict[str, str]]

"""
用于将小说文本拆分为多个场景，并保存到JSON文件中。
"""
class NovelSceneGenerator:
    def __init__(self, project_id: str, role_info: Dict[str, Dict[str, str]]):
        # 设置项目ID
        self.project_id = project_id
        
        # 项目目录路径
        self.project_dir = os.path.join("part2_textSpilt_graphGenerate/Projects", self.project_id)
        
        # 角色信息
        self.role_info = role_info
        self.role_names = [info["name"] for _, info in role_info.items()]
        
        # 读取小说文本（已确保存在，不需要验证）
        self.files_dir = os.path.join(self.project_dir, "files")
        # 获取第一个文本文件
        text_files = [f for f in os.listdir(self.files_dir) if f.endswith('.txt')]
        if not text_files:
            raise FileNotFoundError(f"在目录 {self.files_dir} 中未找到小说文本文件")
        
        self.novel_path = os.path.join(self.files_dir, text_files[0])
        with open(self.novel_path, 'r', encoding='utf-8') as file:
            self.novel_text = file.read()
        
        # 小说名称
        self.novel_name = os.path.splitext(os.path.basename(self.novel_path))[0]
        
        # 初始化文本模型
        self.llm = get_default_llm()
        
        # 存储路径
        self.role_message_dir = os.path.join(self.project_dir, "role_message")
        os.makedirs(self.role_message_dir, exist_ok=True)
        
        # 初始化场景列表
        self.scenes = []
        
        # 原始响应保存路径
        self.raw_response_path = os.path.join(self.role_message_dir, "raw_llm_response.txt")
    
    def create_scene_prompt(self) -> ChatPromptTemplate:
        """创建分镜头场景提取的提示模板"""
        # 将角色列表格式化为提示词中的部分
        roles_text = "、".join(self.role_names) if self.role_names else "未找到角色信息"

        print("角色信息：",roles_text)
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""
            我希望你充当一名专业的分镜师或导演，你将根据我提供的中文文本进行详细拆解。请仔细阅读并理解每一段文本， 
            然后将其转化为多个场景分镜描述。你需要根据文本内容合理分配每个场景，并确保以下几点：
            - 每个分镜头应详细描述场景中的每个元素，如人物、背景、动作等，尽可能具体。
            - 每个场景的描述应包括但不限于以下信息：场景的设定、人物的动作、摄像机的角度与视角、镜头的长度（如特写、远景等）、任何视觉或情感上的细节。
            - 结合上下文，保持人物角色的一致性，比如人物的穿着、发型、手里拿的物品等。
            - 确保描述的连贯性，保持文本的自然顺序，不漏掉任何关键信息。
            - 使用简洁而精确的中文语言，避免添加原文中没有的内容。
            - 禁止生成任何含有文字的画面描述
            - 禁止在description中生成任何人物的对话，只生成人物的站位、动作、表情即可。
            - 尽可能一句话对应一个分镜头
            - 处理每个分镜头的人物角色信息，将出现的角色提取出来并写出每个角色在当前场景下的动作，手中的物品等英文词组
            - 注意，生成角色提示词的时候禁止生成人物性别，外貌等基本信息，这些信息我在之前步骤已经得到了，不需要重复生成，只需要人物最新的穿着打扮，动作即可，不超过5个英语单词！！！
            
          
            
            输出的格式必须严格符合以下结构：
            {{{{
                "scenes": [
                {{{{
                    "description": "详细的画面描述，包括场景设定、人物动作、镜头视角等",
                    "original_text": "该场景对应的原文段落或句子（尽可能一句话，不要太长，也不要太短，禁止出现一个字，也不要全部是对话）",
                    "roles": [
                               {{{{
                                   "{roles_text}中出现的其中角色":"英文stablediffusion提示词，描述该角色在当前场景的动作、服装、手中物品等，不包括外貌描述（严格控制在5个英语单词之内）"

                               }}}}
             
                        ]
                    
                }}}}
                ]
            }}}}
            
            额外要求：
            - 每个场景描述要简明扼要，但同时确保所有重要细节不遗漏。
            - 如果遇到多个分镜，可以将每个分镜描述作为一个独立的JSON对象放入"scenes"列表中。
            - 第一个场景要额外细致的打磨，确保足够吸引人
            - 不要遗漏任何原文信息，包括原文的对话，不要遗漏任何对话
            """),
            ("human", "文本内容：\n{text_segment}\n\n请将此文本切分为多个场景分镜头，并严格按照要求描述每个场景。")
        ])
    
    

    def process_novel(self) -> List[Dict]:
        """处理整个小说文本，生成所有场景"""
        retries = 3
        
        print("开始处理小说文本...")
        start_time = time.time()
        
        # 限制文本长度，避免超出模型上下文窗口
        max_text_length = 15000  # 设置一个合理的最大文本长度
        if len(self.novel_text) > max_text_length:
            print(f"小说文本过长({len(self.novel_text)}字符)，截取前{max_text_length}字符进行处理")
            text_to_process = self.novel_text[:max_text_length]
        else:
            text_to_process = self.novel_text
        
        for attempt in range(retries):
            try:
                print(f"第{attempt+1}次尝试处理小说...")
                # 使用LLM但不使用Parser
                chain = self.create_scene_prompt() | self.llm 
                
                # 添加超时控制
                try:
                    # 尝试使用默认模型
                    response = chain.invoke({"text_segment": text_to_process}, timeout=120)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    print(f"连接错误或超时: {str(e)}")
                    # 如果是最后一次尝试，尝试使用备用模型
                    if attempt == retries - 1:
                        print("尝试使用备用模型...")
                        backup_llm = get_backup_llm()
                        backup_chain = self.create_scene_prompt() | backup_llm
                        response = backup_chain.invoke({"text_segment": text_to_process}, timeout=120)
                    else:
                        raise
                
                # 获取AIMessage的内容
                if hasattr(response, "content"):
                    response_text = response.content
                else:
                    # 如果不是AIMessage对象
                    response_text = str(response)
                
                # 处理可能包含在Markdown代码块中的JSON
                json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
                json_match = re.search(json_pattern, response_text)
                
                if json_match:
                    # 提取代码块中的内容
                    json_text = json_match.group(1).strip()
                    print("从Markdown代码块中提取JSON")
                else:
                    # 如果没有代码块，使用原始文本
                    json_text = response_text

                # 保存提取的JSON
                with open(self.raw_response_path, 'w', encoding='utf-8') as f:
                    f.write(json_text)
                print(f"原始LLM响应已保存至: {self.raw_response_path}")
                
                # 尝试解析JSON
                try:
                    response_data = json.loads(json_text)
                    
                    # 保存JSON数据
                    with open(os.path.join(self.role_message_dir, "final_used_json.json"), 'w', encoding='utf-8') as f:
                        json.dump(response_data, f, ensure_ascii=False, indent=2)
                    
                    self.scenes = response_data["scenes"]
                    
                    end_time = time.time()
                    print(f"处理完成！共生成 {len(self.scenes)} 个场景")
                    print(f"总耗时: {end_time - start_time:.2f} 秒")
                    
                    return self.scenes
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    if attempt == retries - 1:
                        raise
                    else:
                        print("尝试重新解析...")
            
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {str(e)}")
                if attempt == retries - 1:
                    # 最后一次尝试失败，创建最小可用结果
                    error_message = str(e)
                    mock_scene = {
                        "description": f"处理失败，请重试。错误: {error_message[:100]}...",
                        "original_text": "解析错误",
                        "roles": []
                    }
                    self.scenes = [mock_scene]
                    error_path = os.path.join(self.role_message_dir, "error_log.txt")
                    with open(error_path, 'w', encoding='utf-8') as f:
                        f.write(f"场景提取失败: {str(e)}")
                    return self.scenes
                time.sleep(5)  # 增加重试间隔时间
    
    def save_scenes_to_json(self) -> str:
        """保存场景到JSON文件"""
        # 确保目录存在
        os.makedirs(self.role_message_dir, exist_ok=True)
        output_path = os.path.join(self.role_message_dir, "novel_scenes.json")
        
        result = {
            "metadata": {
                "source": os.path.basename(self.novel_path),
                "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_scenes": len(self.scenes)
            },
            "scenes": self.scenes
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"场景数据已保存到: {output_path}")
        return output_path

@app.post("/generate-scenes")
async def generate_scenes(request: SceneGenerateRequest):
    """
    根据项目ID和角色信息，生成小说场景分镜描述
    
    - **project_id**: 项目ID
    - **role_info**: 角色信息JSON对象
    """
    # 初始化环境
    init_environment()
    
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

# 如果作为独立程序运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

