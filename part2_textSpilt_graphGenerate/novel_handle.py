import os
import json
import time
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_models import ChatZhipuAI
from dotenv import load_dotenv
from Models import os_setenv
from Models import get_gemini_2_flash
from Models import get_zhupuai_model
# 加载环境变量
load_dotenv()

os_setenv()

class NovelSceneGenerator:
    def __init__(self, novel_path: str):
        # 文件验证与读取
        if not os.path.exists(novel_path):
            raise FileNotFoundError(f"小说文件不存在: {novel_path}")
        
        self.novel_path = novel_path
        
        with open(novel_path, 'r', encoding='utf-8') as file:
            self.novel_text = file.read()
            
        if not self.novel_text:
            raise ValueError("小说文本为空")

        # 初始化文本模型
        self.llm = get_gemini_2_flash()
        
        # 创建存储目录
        self.output_dir = "part2_textSpilt_graphGenerate/role_message"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化场景列表
        self.scenes = []
    
    def create_scene_prompt(self) -> ChatPromptTemplate:
        """创建分镜头场景提取的提示模板"""
        return ChatPromptTemplate.from_messages([
            ("system", """
              我希望你充当专业的分镜师,我会发送中文文本给你,请你详细的阅读
                并理解后,合理的将文本拆分为详细的分镜画面,然后将该分镜画面详细的描述出来,并且备注对应的文本
                段落,
              生成严格符合以下格式的JSON响应：
              {{
                "scenes": [
                  {{
                    "description": "详细的画面描述",
                    "original_text": "对应的原文内容，(尽可能一个句子)"
                  }}
                ]
              }}
              
              注意：
              - 不要遗漏任何原文内容
              - 不要添加原文中不存在的内容
              - 确保JSON格式正确无误
              - 按照文本的自然顺序组织场景"""),
            ("human", "文本内容：\n{text_segment}\n\n请将此文本切分为场景分镜头。")
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
