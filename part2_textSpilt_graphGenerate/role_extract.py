import os
import json
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Models import os_setenv, get_gemini_2_5_flash ,get_gemini_2_flash
from dotenv import load_dotenv
import time
from prompt_templates import HUMAN_PROMPTS
load_dotenv()
os_setenv()
"""
用于提取出小说中所有的人物，并生成每个角色的专属画像提示词，以方便后序绘图。


"""
class RoleExtractor:
    def __init__(self, novel_path: str,novel_dir: str):
        # 文件验证与读取
        if not os.path.exists(novel_path):
            raise FileNotFoundError(f"小说文件不存在: {novel_path}")
        
        self.novel_dir = novel_dir
        
        # 创建角色信息目录
        self.role_message_dir = os.path.join(self.novel_dir, "role_message")
        os.makedirs(self.role_message_dir, exist_ok=True)
        
        with open(novel_path, 'r', encoding='utf-8') as file:
            self.novel_text = file.read()  # 读取全部内容
            
        if not self.novel_text:
            raise ValueError("小说文本为空")

        # 设置文本模型
        self.extraction_llm = get_gemini_2_5_flash()
        
        # 初始化存储结构
        self.character_profiles = {}

    def create_extraction_prompt(self) -> ChatPromptTemplate:
        """优化后的特征提取提示模板"""
        template = """
                    你是一个专业的小说分析与Stable Diffusion 提示词优化专家，擅长分析小说提取出所有角色并生成对角色的高质量的 Stable Diffusion 正向提示词（Positive Prompt）。

                    任务说明:
                    请将用户输入的小说中所有出现的人物(包括频繁出现的路人形象)（如果有姓名，则沿用，否则自己取一个代号）提取出来，并生成每个角色的专属画像提示词，以方便后序绘图。
                    注意：每个描述里面只能包含一个人物，并且生成的提示词是你根据小说推理出来的人物正面画像，而不是原文中的一段描述，必须是单人正面画像描述，去除多余的动作。

                    提示词要求:
                    1. 词组化:
                    - 将输入文本拆解为符合 Stable Diffusion 语法的关键词短语
                    - 每个词组之间使用英文逗号 分隔

                    -避免负面元素：不包含 ugly, deformed, blurry, low quality 等负面词汇，以确保生成的图像美观、符合需求。

                    2. 只生成对人物正面外观的描述，包含性别，外观，即可。(注意：表情、动作、服装等限定词不要包含，这些让stable diffusion 自由创作)

                    3. 必须以"a boy"或者"a girl"开头

                    4. 人物最鲜明的特征使用"( :1.2)"强调

                    5.禁止出现句子，只允许出现短语！！！比如黑缎缠目就用blindfolded即可，而不要使用eyes covered with black cloth strips


                   
                    生成严格符合以下格式的JSON响应:
                    {{
                        "characters": [{{
                            "name": "姓名",
                            "photo_prompt": "生成的高质量Stable Diffusion正向提示词(英文，5-6个词组左右)"
                        }}]
                    }}
                    """
        human_template = "文本节选：\n{excerpt}\n\n请按规范提取角色信息并创建提示词。"
        
        return ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", human_template)
        ])

    def extract_character_data(self) -> List[Dict]:
        """带重试机制的特征提取"""
        retries = 3
        parser = JsonOutputParser()
        
        for attempt in range(retries):
            try:
                chain = self.create_extraction_prompt() | self.extraction_llm | parser
                
                # 处理长篇小说，如果超过LLM上下文窗口，只取前20000字符
                excerpt = self.novel_text[:20000] if len(self.novel_text) > 20000 else self.novel_text
                
                response = chain.invoke({
                    "excerpt": excerpt,
                    "human_prompts": json.dumps(HUMAN_PROMPTS, ensure_ascii=False, indent=2)
                })
                
                # 添加数据完整性检查
                if not isinstance(response, dict) or "characters" not in response:
                    raise ValueError("响应格式不正确")
                    
                if not isinstance(response["characters"], list):
                    raise ValueError("角色列表格式错误")
                
                print("成功提取角色列表：")
                for char in response["characters"]:
                    if not all(key in char for key in ["name", "photo_prompt"]):
                        raise ValueError(f"角色{char.get('name','未知')}字段缺失")
                    print(f"• {char['name']} ")
                    print(f"  摄影提示词: {char['photo_prompt']}")
                return response["characters"]
            
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {str(e)}")
                if attempt == retries - 1:
                    raise RuntimeError(f"特征提取失败：{str(e)}")
                time.sleep(1.5)

    def save_role_info(self, characters: List[Dict]):
        """保存角色信息到JSON文件"""
        # 确定JSON文件路径
        json_path = os.path.join(self.role_message_dir, "role_info.json")
        
        # 强制删除旧文件（如果存在）
        try:
            if os.path.exists(json_path):
                print(f"正在删除旧文件: {json_path}")
                # 尝试强制删除文件
                try:
                    os.remove(json_path)
                except PermissionError:
                    # 如果是权限问题，尝试更改权限后删除
                    import stat
                    os.chmod(json_path, stat.S_IWRITE)
                    os.remove(json_path)
                except Exception as e:
                    print(f"删除文件失败: {e}，尝试直接覆盖...")
                    # 删除失败，继续执行，尝试直接覆盖
        except Exception as e:
            print(f"处理旧文件时出错: {e}")
        
        # 准备新数据
        role_info = {}
        for i, char in enumerate(characters, 1):
            role_info[f"{i:03d}"] = {
                "name": char["name"],
                "prompt": char["photo_prompt"]
            }
        
        # 保存到role_info.json，使用写入模式('w')强制覆盖
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(role_info, f, ensure_ascii=False, indent=2)
            
            # 验证文件是否成功写入
            if os.path.exists(json_path):
                file_size = os.path.getsize(json_path)
                if file_size > 0:
                    print(f"角色信息已成功保存至: {json_path}")
                else:
                    raise Exception("文件被创建但大小为0")
            else:
                raise Exception("文件未能成功创建")
        except Exception as e:
            # 如果主路径失败，尝试使用备用路径
            backup_path = os.path.join(self.novel_dir, "role_info_backup.json")
            print(f"保存到主路径失败: {e}，尝试保存到备用路径: {backup_path}")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(role_info, f, ensure_ascii=False, indent=2)
            print(f"角色信息已保存至备用路径: {backup_path}")
            
        return role_info

    def process_novel(self) -> Dict:
        """主处理流程"""
        characters = self.extract_character_data()
        role_info = self.save_role_info(characters)
        return role_info

if __name__ == "__main__":
    extractor = RoleExtractor(
        novel_path="part2_textSpilt_graphGenerate\\files\\斗破苍穹节选.txt"
    )
    result = extractor.process_novel()
    
    # 打印首个人物信息
    if result:
        print("\n示例人物数据：")
        print(json.dumps(result[next(iter(result))], ensure_ascii=False, indent=2)) 