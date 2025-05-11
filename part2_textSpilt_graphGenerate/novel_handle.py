import os
import json
import time
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_models import ChatZhipuAI
from dotenv import load_dotenv
from Models import os_setenv
from Models import get_gemini_2_flash,get_gemini_2_5_flash
from Models import get_zhupuai_model
# 加载环境变量
load_dotenv()

os_setenv()
"""
用于将小说文本拆分为多个场景，并保存到JSON文件中。
"""
class NovelSceneGenerator:
    def __init__(self, novel_path: str):
        # 文件验证与读取
        if not os.path.exists(novel_path):
            raise FileNotFoundError(f"小说文件不存在: {novel_path}")
        
          # 获取小说名称
        self.novel_name = os.path.splitext(os.path.basename(novel_path))[0]
        
        # 创建小说专属目录
        self.novel_dir = os.path.join("part2_textSpilt_graphGenerate", self.novel_name)

        self.novel_path = novel_path
        
        with open(novel_path, 'r', encoding='utf-8') as file:
            self.novel_text = file.read()
            
        if not self.novel_text:
            raise ValueError("小说文本为空")

        # 初始化文本模型
        self.llm = get_gemini_2_5_flash()
        
        # 创建存储目录
        self.output_dir = os.path.join(self.novel_dir, "role_message")
        
        # 加载角色信息
        self.role_names = self.load_role_names()
        
        # 初始化场景列表
        self.scenes = []
    
    def load_role_names(self) -> List[str]:
        """从role_info.json加载角色名称列表"""
        role_info_path = os.path.join(self.novel_dir, "role_message", "role_info.json")
        
        if not os.path.exists(role_info_path):
            print(f"角色信息文件不存在: {role_info_path}，将使用空角色列表")
            return []
        
        try:
            with open(role_info_path, 'r', encoding='utf-8') as file:
                role_info = json.load(file)
                
            # 提取所有角色名称
            role_names = [info["name"] for _, info in role_info.items()]
            print(f"已加载角色列表: {role_names}")
            return role_names
        except Exception as e:
            print(f"加载角色信息失败: {str(e)}，将使用空角色列表")
            return []
    
    def create_scene_prompt(self) -> ChatPromptTemplate:
        """创建分镜头场景提取的提示模板"""
        # 将角色列表格式化为提示词中的部分
        roles_text = "、".join(self.role_names) if self.role_names else "未找到角色信息"
        
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
            - 禁止生成任何人物的对话，只生成人物的站位、动作、表情即可。
            - 尽可能一句话对应一个分镜头
            - 处理每个分镜头的人物角色信息，将出现的角色提取出来并写出每个角色在当前场景下的动作，手中的物品等英文词组
            - 注意，生成角色提示词的时候禁止生成人物性别，外貌等基本信息，这些信息我在之前步骤已经得到了，不需要重复生成，只需要人物最新的穿着打扮，动作即可，不超过5个英语单词！！！
            
          
            
            输出的格式必须严格符合以下结构：
            {{{{
                "scenes": [
                {{{{
                    "description": "详细的画面描述，包括场景设定、人物动作、镜头视角等",
                    "original_text": "该场景对应的原文段落或句子（尽可能一句话）",
                    "roles": [
                                "{roles_text}中出现的其中角色":"英文stablediffusion提示词，描述该角色在当前场景的动作、服装、手中物品等，不包括外貌描述（严格控制在5个英语单词之内）"
             
                        ]
                    
                }}}}
                ]
            }}}}
            
            额外要求：
            - 每个场景描述要简明扼要，但同时确保所有重要细节不遗漏。
            - 如果遇到多个分镜，可以将每个分镜描述作为一个独立的JSON对象放入"scenes"列表中。
            """),
            ("human", "文本内容：\n{text_segment}\n\n请将此文本切分为多个场景分镜头，并严格按照要求描述每个场景。")
        ])

    
    def process_novel(self) -> List[Dict]:
        """处理整个小说文本，生成所有场景"""
        retries = 3
        parser = JsonOutputParser()
        
        print("开始处理小说文本...")
        start_time = time.time()
        
        for attempt in range(retries):
            try:
                print(f"第{attempt+1}次尝试处理小说...")
                chain = self.create_scene_prompt() | self.llm | parser
                response = chain.invoke({"text_segment": self.novel_text})
                
                # 数据完整性检查
                if not isinstance(response, dict) or "scenes" not in response:
                    raise ValueError("响应格式不正确")
                    
                if not isinstance(response["scenes"], list):
                    raise ValueError("场景列表格式错误")
                
                for scene in response["scenes"]:
                    if not all(key in scene for key in ["description", "original_text"]):
                        raise ValueError(f"场景字段缺失")
                
                self.scenes = response["scenes"]
                
                end_time = time.time()
                print(f"处理完成！共生成 {len(self.scenes)} 个场景")
                print(f"总耗时: {end_time - start_time:.2f} 秒")
                
                return self.scenes
            
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {str(e)}")
                if attempt == retries - 1:
                    raise RuntimeError(f"场景提取失败：{str(e)}")
                time.sleep(2)
    
    def save_scenes_to_json(self, output_path: str = None):
        """保存场景到JSON文件"""
        if output_path is None:
            output_path = os.path.join(self.output_dir, "novel_scenes.json")
        
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


# 使用示例
if __name__ == "__main__":
    generator = NovelSceneGenerator(
        novel_path="part2_textSpilt_graphGenerate/files/斗破苍穹节选.txt"  # 替换为实际路径
    )
    scenes = generator.process_novel()
    generator.save_scenes_to_json()
