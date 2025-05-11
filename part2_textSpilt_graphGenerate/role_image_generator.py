import os
import json
from typing import Dict
from stable_diffusion import SD_Generate
from dotenv import load_dotenv
from prompt_templates import GENERAL_PROMPTS
import time
load_dotenv()
"""
用于生成角色图像，并保存到本地。
"""
class RoleImageGenerator:
    def __init__(self, novel_name: str):
        """
        初始化角色图片生成器
        
        Args:
            novel_name (str): 小说名称
        """
        # 设置相关目录路径
        self.novel_name = novel_name
        self.novel_dir = os.path.join("part2_textSpilt_graphGenerate", self.novel_name)
        self.role_img_dir = os.path.join(self.novel_dir, "role_img")
        self.role_message_dir = os.path.join(self.novel_dir, "role_message")
        
        # 确保目录存在
        os.makedirs(self.role_img_dir, exist_ok=True)
        os.makedirs(self.role_message_dir, exist_ok=True)
        
        # 初始化SD生成器
        self.sd_generator = SD_Generate()
        
        # 初始化角色信息存储
        self.character_profiles = {}

    def load_role_info(self) -> Dict:
        """
        从JSON文件加载角色信息
        
        Returns:
            Dict: 角色信息字典
        """
        json_path = os.path.join(self.role_message_dir, "role_info.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"角色信息文件不存在: {json_path}")
            
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_character_image(self, character: Dict, char_index: str) -> dict:
        """
        使用Stable Diffusion生成角色图像
        
        Args:
            character (Dict): 角色信息
            char_index (str): 角色索引
            
        Returns:
            dict: 生成的图像信息
        """
        try:
            # 准备提示词
            prompt=character["prompt"] 
            finally_prompt = GENERAL_PROMPTS["positive_prompt"]+ prompt
            negative_prompt = GENERAL_PROMPTS["negitive_prompt"]
            
            # 生成图像
            self.sd_generator.generate_prompt(
                prompt=finally_prompt,
                negative_prompt=negative_prompt,
                seed=-1,
                batch_size=2
            )
            self.sd_generator.get_img()
            
            # 构建保存路径
            base_save_path = os.path.join(self.role_img_dir, character["name"])
            self.sd_generator.save_img(base_save_path)
            
          
            
            return {
                "name": character["name"],
                "prompt": prompt,
                "seeds": self.sd_generator.seeds,
                "path": base_save_path
            }
            
        except Exception as e:
            print(f"生成{character['name']}图像失败：{str(e)}")
            return None

    def process_characters(self) -> Dict:
        """
        处理所有角色并生成图像
        
        Returns:
            Dict: 处理结果信息
        """
        # 加载角色信息
        role_info = self.load_role_info()
        
        # 处理每个角色
        for char_id, char_info in role_info.items():
            print(f"\n正在生成 [{char_info['name']}] 的角色形象...")
            char_data = self.generate_character_image(char_info, char_id)
            
            if char_data:
                self.character_profiles[char_id] = char_data
        
        # 保存生成结果
        archive_path = os.path.join(self.role_message_dir, "character_archive.json")
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(self.character_profiles, f, ensure_ascii=False, indent=2)
        
        print("\n处理完成！生成角色数：", len(self.character_profiles))
        return self.character_profiles
    
    #高清修复选中的图片
    def high_resolution_image(self, char_id: str, image_index: int = 0):
        """
        高清修复选中的图片
        
        Args:
            char_id (str): 角色ID
            image_index (int, optional): 选择的图片索引. Defaults to 0.
        
        Returns:
            str: 高清修复后的图片路径
        """
        # 检查角色是否存在
        if not self.character_profiles or char_id not in self.character_profiles:
            try:
                # 尝试加载已有的角色档案
                archive_path = os.path.join(self.role_message_dir, "character_archive.json")
                if os.path.exists(archive_path):
                    with open(archive_path, "r", encoding="utf-8") as f:
                        self.character_profiles = json.load(f)
                if char_id not in self.character_profiles:
                    raise ValueError(f"未找到角色ID: {char_id}")
            except Exception as e:
                print(f"加载角色信息失败: {str(e)}")
                return None
        
        # 获取角色信息
        char_info = self.character_profiles[char_id]
        name = char_info["name"]
        prompt = char_info["prompt"]
        seed = char_info["seeds"][image_index] if image_index < len(char_info["seeds"]) else -1
        
        print(f"\n正在对 [{name}] 的图片进行高清修复...")
        
        # 准备提示词
        finally_prompt = GENERAL_PROMPTS["positive_prompt"] + prompt
        negative_prompt = GENERAL_PROMPTS["negitive_prompt"]
        
        # 高清修复
        self.sd_generator.generate_prompt(
            prompt=finally_prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            batch_size=1,
            enable_hr=True  # 启用高清修复
        )
        
        self.sd_generator.get_img()
        
        # 构建保存路径
        hd_save_path = os.path.join(self.role_img_dir, f"{name}_HD")
        self.sd_generator.save_img(hd_save_path)
        
        # 更新角色档案中的高清图片信息
        self.character_profiles[char_id]["hd_image"] = {
            "path": hd_save_path,
            "seed": seed,
            "original_index": image_index
        }
        
        # 保存更新后的角色档案
        archive_path = os.path.join(self.role_message_dir, "character_archive.json")
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(self.character_profiles, f, ensure_ascii=False, indent=2)
        
        print(f"已完成 [{name}] 的高清修复，保存至: {hd_save_path}")
        return hd_save_path

if __name__ == "__main__":
    # 使用示例
    generator = RoleImageGenerator(novel_name="斗破苍穹节选")
    result = generator.process_characters()
    
    # 打印所有角色信息并进行高清修复
    if result:
        print("\n开始处理所有角色的高清修复...")
        for char_id in result:
            print(f"\n当前处理角色数据：")
            print(json.dumps(result[char_id], ensure_ascii=False, indent=2))
            
            # 对该角色的指定图片进行高清修复
            img_index = int(input("请输入要处理的图片索引：")) # 指定要处理的图片索引
            print(f"\n正在处理角色 {result[char_id]['name']} 的第 {img_index+1} 张图片...")
            generator.high_resolution_image(char_id, img_index)
            # 角色之间添加延迟
            if char_id != list(result.keys())[-1]:
                time.sleep(3)