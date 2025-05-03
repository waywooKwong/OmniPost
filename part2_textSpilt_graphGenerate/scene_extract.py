"""
从novel_scenes.json提炼出场景提示词，不包含角色识别
"""

import json
import os
import time
import argparse
import re
from typing import Dict, List, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from Models import os_setenv, get_gemini_2_flash, get_zhupuai_model,get_gemini_2_5_flash
from dotenv import load_dotenv

load_dotenv()
os_setenv()

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
        self.gemini_llm = get_gemini_2_flash()
        self.zhipuai_llm = get_zhupuai_model()
        # 用户聊天历史记录字典，键为用户ID
        self.chat_histories = {}

    def _get_chat_history(self, user_id: str) -> List:
        """获取指定用户的聊天历史"""
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
        return self.chat_histories[user_id]

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

    def generate_scene_prompt(self, scene: Dict, user_id: str = "default_user") -> str:
        """为单个场景生成提示词，加入聊天历史记忆"""
        retries = 2  # Gemini模型重试次数
        chat_history = self._get_chat_history(user_id)
        
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
        
        # 首先尝试使用Gemini模型
        for attempt in range(retries):
            try:
                # 使用带有聊天历史的链
                chain = prompt | self.gemini_llm
                response = chain.invoke({
                    "chat_history": chat_history_text,
                    "description": scene.get("description", ""),
                    "original_text": scene.get("original_text", "")
                })
                
                # 使用自定义的JSON提取函数
                content = response.content if hasattr(response, 'content') else response
                
                # 检查是否为空响应
                if content is None or not str(content).strip():
                    print(f"Gemini返回空响应，尝试第{attempt+1}次...")
                    if attempt == retries - 1:
                        print("Gemini多次返回空响应，将切换到智普AI模型...")
                        break  # 跳出循环，使用智普AI模型
                    time.sleep(1.5)
                    continue
                
                parsed_response = extract_json_from_text(content)
                
                # 添加数据完整性检查
                if not isinstance(parsed_response, dict):
                    raise ValueError("响应格式不正确")
                
                if "prompt" not in parsed_response:
                    # 如果没有prompt字段，但有其他内容，尝试使用整个内容作为prompt
                    if isinstance(content, str) and content.strip():
                        prompt = content.strip()
                    else:
                        raise ValueError("响应中缺少prompt字段")
                else:
                    prompt = parsed_response["prompt"]
                
                if not prompt or len(str(prompt).strip()) == 0:
                    raise ValueError("生成的提示词为空")
                
                # 处理换行符
                if isinstance(prompt, str):
                    prompt = prompt.replace("\\n", " ").replace("\n", " ")
                
                print(f"Gemini成功生成提示词: {str(prompt)[:50]}...")
                
                # 更新聊天历史
                chat_history.append(HumanMessage(content=f"请为场景生成提示词：{scene.get('description', '')}"))
                chat_history.append(AIMessage(content=prompt))
                
                return prompt
            
            except Exception as e:
                print(f"Gemini第{attempt+1}次尝试失败: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(1.5)
                else:
                    print("Gemini模型失败，将切换到智普AI模型...")
        
        # 如果Gemini模型失败，尝试使用智普AI模型
        try:
            print("使用智普AI模型生成提示词...")
            zhipu_chain = prompt | self.zhipuai_llm
            zhipu_response = zhipu_chain.invoke({
                "chat_history": chat_history_text,
                "description": scene.get("description", ""),
                "original_text": scene.get("original_text", "")
            })
            
            # 处理智普AI的响应
            zhipu_content = zhipu_response.content if hasattr(zhipu_response, 'content') else zhipu_response
            zhipu_parsed = extract_json_from_text(zhipu_content)
            
            if isinstance(zhipu_parsed, dict) and "prompt" in zhipu_parsed:
                prompt = zhipu_parsed["prompt"]
                if prompt and len(str(prompt).strip()) > 0:
                    # 处理换行符
                    if isinstance(prompt, str):
                        prompt = prompt.replace("\\n", " ").replace("\n", " ")
                    print(f"智普AI成功生成提示词: {str(prompt)[:50]}...")
                    
                    # 更新聊天历史
                    chat_history.append(HumanMessage(content=f"请为场景生成提示词：{scene.get('description', '')}"))
                    chat_history.append(AIMessage(content=prompt))
                    
                    return prompt
            
            # 如果智普AI也失败了，使用一个简单的默认提示词
            print("智普AI也失败了，使用默认提示词")
            people_count = 1
            if "人" in scene.get("description", "") or "他" in scene.get("description", ""):
                people_count = 2
            default_prompt = f"({people_count} people) simple scene, indoor setting"
            
            # 更新聊天历史
            chat_history.append(HumanMessage(content=f"请为场景生成提示词：{scene.get('description', '')}"))
            chat_history.append(AIMessage(content=default_prompt))
            
            return default_prompt
            
        except Exception as e:
            print(f"智普AI模型失败: {str(e)}")
            default_prompt = "(1 person) generic scene"
            
            # 更新聊天历史
            chat_history.append(HumanMessage(content=f"请为场景生成提示词：{scene.get('description', '')}"))
            chat_history.append(AIMessage(content=default_prompt))
            
            return default_prompt
        
        return "scene with characters"  # 不应该到达这里，但为了类型检查添加

    def create_scene_prompts(self, scenes_file: str, output_file: Optional[str] = None, user_id: str = "default_user") -> List[Dict]:
        """批量处理场景并生成提示词"""
        if not os.path.exists(scenes_file):
            raise FileNotFoundError(f"场景文件不存在: {scenes_file}")
        
        # 自动设置输出文件路径
        if output_file is None:
            output_dir = os.path.dirname(scenes_file)
            output_file = os.path.join(output_dir, "scene_prompts.json")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 加载场景数据
        with open(scenes_file, 'r', encoding='utf-8') as file:
            scenes_data = json.load(file)
            if "scenes" not in scenes_data:
                raise ValueError("场景数据格式不正确，缺少'scenes'字段")
        
        scenes_to_process = scenes_data["scenes"]
        total_scenes = len(scenes_to_process)
        results = []
        
        print(f"\n将处理{total_scenes}个场景...")
        
        for index, scene in enumerate(scenes_to_process):
            print(f"\n===== 处理场景 {index+1}/{total_scenes} =====")
            
            try:
                prompt = self.generate_scene_prompt(scene, user_id)
                scene_result = {"prompt": prompt}
                results.append(scene_result)
                print(f"场景 {index+1} 处理完成")
            except Exception as e:
                print(f"场景 {index+1} 处理失败: {e}")
                scene_result = {"prompt": "(1 person) simple indoor scene"}
                results.append(scene_result)
            
            # 防止API调用过于频繁
            if index < total_scenes - 1:  # 不在最后一个场景后延迟
                wait_time = 2 + (index % 3)  # 变化的等待时间，避免规律性请求
                print(f"等待 {wait_time} 秒后继续...")
                time.sleep(wait_time)
        
        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"scene_prompts": results}, f, ensure_ascii=False, indent=2)
        
        print(f"处理完成，结果已保存到 {output_file}")
        return results

class SceneExtractor:
    def __init__(self, scenes_file: str, output_file: str = None):
        """初始化场景提取器"""
        # 文件验证
        if not os.path.exists(scenes_file):
            raise FileNotFoundError(f"场景文件不存在: {scenes_file}")
        
        self.scenes_file = scenes_file
        
        # 自动设置输出文件路径
        if output_file is None:
            output_dir = os.path.dirname(scenes_file)
            output_file = os.path.join(output_dir, "scene_prompts.json")
        
        self.output_file = output_file
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # 加载场景数据
        with open(scenes_file, 'r', encoding='utf-8') as file:
            self.scenes_data = json.load(file)
            if "scenes" not in self.scenes_data:
                raise ValueError("场景数据格式不正确，缺少'scenes'字段")
        
        # 创建内存代理
        self.memory_agent = SceneMemoryAgent()

    def process(self) -> List[Dict]:
        """主处理流程，使用场景记忆代理处理"""
        print("开始处理场景...")
        results = self.memory_agent.create_scene_prompts(
            scenes_file=self.scenes_file,
            output_file=self.output_file
        )
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='处理小说场景并生成图片提示词')
    parser.add_argument('--scenes_file', type=str, 
                        default="part2_textSpilt_graphGenerate/斗破苍穹节选/role_message/novel_scenes.json",
                        help='场景JSON文件路径')
    parser.add_argument('--output_file', type=str, 
                        default=None,  # 如果为None，会自动设置
                        help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        extractor = SceneExtractor(
            scenes_file=args.scenes_file,
            output_file=args.output_file
        )
        extractor.process()
    except Exception as e:
        print(f"程序执行失败: {e}") 