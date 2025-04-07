import os
import json
import io
import base64
from PIL import Image
from typing import Dict, List, Optional
from stable_diffusion import SD_Generate
from prompt_templates import GENERAL_PROMPTS
from dotenv import load_dotenv

load_dotenv()

class SceneImageGenerator:
    def __init__(self, novel_name: str):
        """
        初始化场景图片生成器
        
        Args:
            novel_name (str): 小说名称
        """
        # 设置相关目录路径
        self.novel_name = novel_name
        self.novel_dir = os.path.join("part2_textSpilt_graphGenerate", self.novel_name)
        self.role_message_dir = os.path.join(self.novel_dir, "role_message")
        self.output_dir = os.path.join(self.novel_dir, "scene_images")
        
        # 设置文件路径

        self.character_archive_file = os.path.join(self.role_message_dir, "character_archive.json")
        self.scene_prompts_file = os.path.join(self.role_message_dir, "scene_prompts.json")
        
        # 确保输出目录存在
        self.ensure_dir_exists(self.output_dir)
        
        # 初始化SD生成器
        self.sd_generator = SD_Generate()
        
        # 角色信息和场景提示词将在处理时加载
        self.character_archive = {}
        self.scene_prompts = {}
        self.scene_results = {}

    def ensure_dir_exists(self, dir_path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"已创建目录: {dir_path}")

    def load_json_file(self, file_path: str) -> Dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败: {file_path}, 错误: {str(e)}")
            return {}

    def get_character_seed(self, role_names: List[str]) -> int:
        """
        根据角色名称获取种子
        如果有角色，则使用第一个角色的种子
        否则返回-1表示使用随机种子
        """
        if not role_names:
            return -1
            
        # 获取第一个角色名称
        first_role = role_names[0]
        
        # 在角色存档中查找该角色的信息
        for char_id, char_info in self.character_archive.items():
            if char_info.get('name') == first_role:
                return char_info.get('seed', -1)
                
        return -1

    def generate_scene_image(self, scene_index: int, scene_prompt: Dict) -> dict:
        """
        使用stable diffusion生成场景图片
        
        Args:
            scene_index (int): 场景索引
            scene_prompt (Dict): 场景提示词数据
            
        Returns:
            dict: 生成的图像信息，包含路径、种子等
        """
        try:
            # 获取提示词和角色
            prompt = scene_prompt.get('prompt', '')
            roles = scene_prompt.get('roles', [])
            
            # 如果提示词为空，返回None
            if not prompt:
                print(f"警告: 场景 {scene_index+1} 的提示词为空，跳过生成")
                return None
                
            # 获取种子
            seed = self.get_character_seed(roles)
            
            # 使用通用负面提示词
            prompt = GENERAL_PROMPTS["positive_prompt"] + prompt
            negative_prompt = GENERAL_PROMPTS["negitive_prompt"]
            
            # 生成图像
            self.sd_generator.generate_prompt(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=1
            )
            self.sd_generator.get_img()
            
            # 创建场景专用目录，按照场景编号分类
            scene_folder = os.path.join(self.output_dir, f"scene_{scene_index+1:03d}")
            self.ensure_dir_exists(scene_folder)
            
            # 构建保存路径基础部分（不含序号和扩展名）
            base_save_path = os.path.join(scene_folder, f"scene_{scene_index+1:03d}")
            selected_index = self.sd_generator.save_img(base_save_path)

            # 构建选中图片的完整路径
            output_path = f"{base_save_path}_{selected_index}.png"
            
            # 返回图像信息
            return {
                "scene_index": scene_index + 1,
                "roles": roles,
                "seed": self.sd_generator.seeds[0] if self.sd_generator.seeds else -1,
                "selected_image_index": selected_index,
                "all_images": [f"{base_save_path}_{i}.png" for i in range(len(self.sd_generator.r.get('images', [])))],
                "selected_path": output_path
            }
            
        except Exception as e:
            print(f"错误: 场景 {scene_index+1} 图片生成失败: {str(e)}")
            return None

    def process_scenes(self) -> Dict:
        """
        处理所有场景并生成图片
        
        Returns:
            Dict: 所有场景的生成结果
        """
        # 加载角色信息
        self.character_archive = self.load_json_file(self.character_archive_file)
        if not self.character_archive:
            print(f"警告: 未找到角色存档或为空: {self.character_archive_file}")
        
        # 加载场景提示词
        self.scene_prompts = self.load_json_file(self.scene_prompts_file)
        scene_prompts_data = self.scene_prompts.get('scene_prompts', [])
        
        if not scene_prompts_data:
            print(f"错误: 未找到场景提示词或为空: {self.scene_prompts_file}")
            return {}
        
        print(f"\n开始生成 [{self.novel_name}] 的场景图片...")
        print(f"共找到 {len(scene_prompts_data)} 个场景提示词\n")
        
        # 遍历场景生成图片
        for i, scene_prompt in enumerate(scene_prompts_data):
            print(f"正在生成场景 {i+1}/{len(scene_prompts_data)}...")
            
            # 生成图片并保存结果
            scene_data = self.generate_scene_image(i, scene_prompt)
            if scene_data:
                self.scene_results[f"scene_{i+1:03d}"] = scene_data
                print(f"场景 {i+1} 已生成 {len(scene_data.get('all_images', []))} 张图片")
                print(f"选中的图片保存在: {scene_data.get('selected_path')}")
        
        # 保存生成结果到JSON
        results_path = os.path.join(self.role_message_dir, "scene_archive.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(self.scene_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成！生成场景数：{len(self.scene_results)}")
        print(f"所有图片保存在：{self.output_dir}")
        return self.scene_results

def main():
    # 使用示例
    generator = SceneImageGenerator(novel_name="斗破苍穹节选")
    result = generator.process_scenes()
    
    # 打印首个场景信息
    if result:
        print("\n示例场景数据：")
        print(json.dumps(result[next(iter(result))], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 