import os
import json
import io
import base64
from PIL import Image
from typing import Dict, List, Optional, Union, Tuple
from stable_diffusion import SD_Generate
from prompt_templates import GENERAL_PROMPTS
from dotenv import load_dotenv
import time

load_dotenv()
"""
用于生成场景图片，并保存到本地。
"""
class SceneImageGenerator:
    def __init__(self, input_dir: str,output_dir: str,novel_name: str):
        """
        初始化场景图片生成器
        
        Args:
            novel_name (str): 小说名称
        """
       
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.novel_name = novel_name
        # 确保输出目录存在
        self.ensure_dir_exists(self.output_dir)
        
        # 初始化SD生成器
        self.sd_generator = SD_Generate()
        
        # 加载所需文件
        self.scene_archive_file = os.path.join(self.output_dir, "scene_archive.json")
        self.scene_prompts = self.load_json_file(os.path.join(self.input_dir, "role_message", "novel_scenes_prompt.json"))
        self.novel_scenes = self.load_json_file(os.path.join(self.input_dir, "role_message", "novel_scenes.json"))
        self.role_info = self.load_json_file(os.path.join(self.input_dir, "role_message", "role_info.json"))
       
        self.scene_results = {}
        
        # 通用提示词
        self.positive_prompt = GENERAL_PROMPTS["positive_prompt"]
        self.negative_prompt = GENERAL_PROMPTS["negitive_prompt"]

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
    
    def save_json_file(self, file_path: str, data: Dict) -> None:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"保存JSON文件成功: {file_path}")
        except Exception as e:
            print(f"保存JSON文件失败: {file_path}, 错误: {str(e)}")

    
    
    def get_character_prompt(self, role_name: str) -> str:
        """
        根据角色名称获取角色提示词
        
        Args:
            role_name: 角色名称
            
        Returns:
            str: 角色提示词或空字符串
        """
        # 在角色信息中查找
        for char_id, char_info in self.role_info.items():
            if char_info.get('name') == role_name:
                return char_info.get('prompt', '')
        
        return ''
    
    def get_character_prompt_with_scene_detail(self, role_name: str, scene_roles: list) -> str:
        """
        获取角色的基准提示词，并与场景中的角色描述合并
        
        Args:
            role_name: 角色名称
            scene_roles: 场景中的角色信息列表
            
        Returns:
            str: 合并后的角色提示词
        """
        # 获取基准提示词
        base_prompt = self.get_character_prompt(role_name)
        
        # 查找角色在场景中的描述
        scene_description = ""
        for role_item in scene_roles:
            if isinstance(role_item, dict) and role_name in role_item:
                scene_description = role_item[role_name]
                break
        
        # 合并基准提示词和场景描述
        if scene_description:
            return f"{base_prompt}, {scene_description}"
        else:
            return base_prompt
    
    def construct_prompt(self, scene_index: int, scene_prompt: Dict, scene_info: Dict) -> Tuple[str, bool, str]:
        """
        构建场景提示词
        
        Args:
            scene_index: 场景索引
            scene_prompt: 场景提示词信息
            scene_info: 小说场景信息
            
        Returns:
            Tuple[str, bool, str]: 返回构建的提示词、是否使用区域提示器、区域比例
        """
        prompt = scene_prompt.get('prompt', '')
        roles = scene_info.get('roles', [])
        role_count = len(roles)
        
        use_regional_prompter = False
        regional_prompt_ratios = "1,1"
        
        # 基础正面提示词
        final_prompt = self.positive_prompt
        
        # 根据角色数量构建提示词
        if role_count == 0:
            # 无角色，直接拼接场景提示词
            final_prompt = prompt+","+final_prompt
        elif role_count == 1:
            # 单角色，获取角色提示词（基准+场景描述）
            role_name = list(roles[0].keys())[0] if isinstance(roles[0], dict) else roles[0]
            role_prompt = self.get_character_prompt_with_scene_detail(role_name, roles)
            final_prompt = prompt + ", " + role_prompt+" ,"+final_prompt
        else:
            print("有多个角色")
            # 多角色，使用区域提示器
            use_regional_prompter = True
            
            # 构建区域提示词
            final_prompt = prompt + ","+final_prompt
            
            # 设置区域比例
            if role_count == 2:
                regional_prompt_ratios = "1,1"
            elif role_count >= 3:
                regional_prompt_ratios = "1,1,1"
                # 如果有超过3个角色，只取前3个
                roles = roles[:3]
            
            # 添加BREAK和角色提示词（基准+场景描述）
            for i, role_item in enumerate(roles):
                if isinstance(role_item, dict):
                    role_name = list(role_item.keys())[0]
                else:
                    role_name = role_item
                
                role_prompt = self.get_character_prompt_with_scene_detail(role_name, roles)
                
                if i > 0:
                    final_prompt += " ,\n  BREAK  \n"
                else:
                    final_prompt += ", \n BREAK "
                final_prompt += role_prompt
        
        print("最终提示词： ",final_prompt," ",use_regional_prompter," ",regional_prompt_ratios)
        return final_prompt, use_regional_prompter, regional_prompt_ratios

    def generate_scene_image(self, scene_index: int, scene_prompt: Dict, scene_info: Dict) -> dict:
        """
        使用stable diffusion生成场景图片
        
        Args:
            scene_index (int): 场景索引
            scene_prompt (Dict): 场景提示词数据
            scene_info (Dict): 场景信息数据
            
        Returns:
            dict: 生成的图像信息，包含路径、种子等
        """
        try:
            # 构建提示词
            prompt, use_regional_prompter, regional_prompt_ratios = self.construct_prompt(
                scene_index, scene_prompt, scene_info
            )
            
            # 获取角色列表
            roles = scene_info.get('roles', [])
            
            # 如果提示词为空，返回None
            if not prompt:
                print(f"警告: 场景 {scene_index+1} 的提示词为空，跳过生成")
                return None
                
            # 默认种子为-1
            seed =-1
            
            # 生成图像
            self.sd_generator.generate_prompt(
                prompt=prompt,
                negative_prompt=self.negative_prompt,
                seed=seed,
                batch_size=4,
                use_regional_prompter=use_regional_prompter,
                regional_prompt_mode="Columns",
                regional_prompt_ratios=regional_prompt_ratios
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
            
            # 保存生成信息
            seeds = self.sd_generator.seeds if hasattr(self.sd_generator, 'seeds') else [-1]
            
            # 返回图像信息
            return {
                "scene_index": scene_index + 1,
                "roles": roles,
                "seeds": seeds,
                "selected_image_index": selected_index,
                "all_images": [f"{base_save_path}_{i}.png" for i in range(len(self.sd_generator.r.get('images', [])))],
                "selected_path": output_path,
                "prompt": prompt,
                "negative_prompt": self.negative_prompt,
                "use_regional_prompter": use_regional_prompter,
                "regional_prompt_ratios": regional_prompt_ratios if use_regional_prompter else "",
                "hd_image": None  # 高清修复图片，初始为None
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
        
        
        # 检查数据是否加载成功
        scene_prompts_data = self.scene_prompts.get('scene_prompts', [])
        novel_scenes_data = self.novel_scenes.get('scenes', [])
        
        if not scene_prompts_data:
            print(f"错误: 未找到场景提示词或为空: {self.scene_prompts_file}")
            return {}
            
        if not novel_scenes_data:
            print(f"错误: 未找到小说场景数据或为空: {self.novel_scenes_file}")
            return {}
        
        if len(scene_prompts_data) != len(novel_scenes_data):
            print(f"警告: 场景提示词({len(scene_prompts_data)})和小说场景({len(novel_scenes_data)})数量不匹配")
        
        print(f"\n开始生成 [{self.novel_name}] 的场景图片...")
        print(f"共找到 {len(scene_prompts_data)} 个场景提示词\n")
        
        # 遍历场景生成图片
        for i, (scene_prompt, scene_info) in enumerate(zip(scene_prompts_data, novel_scenes_data)):
            print(f"正在生成场景 {i+1}/{len(scene_prompts_data)}...")
            print(f"场景角色: {scene_info.get('roles', [])}")
            
            # 生成图片并保存结果
            scene_data = self.generate_scene_image(i, scene_prompt, scene_info)
            if scene_data:
                self.scene_results[f"scene_{i+1:03d}"] = scene_data
                print(f"场景 {i+1} 已生成 {len(scene_data.get('all_images', []))} 张图片")
                print(f"默认选中图片: {scene_data.get('selected_path')}")
        
        # 所有场景生成完毕，保存临时结果
        self.save_json_file(self.scene_archive_file, self.scene_results)
        
        print(f"\n所有场景图片已生成完毕！生成场景数：{len(self.scene_results)}")
        print(f"所有图片保存在：{self.output_dir}")
        print(f"场景归档保存在：{self.scene_archive_file}")
        
        return self.scene_results
    
    def generate_hd_image(self, scene_id: str, image_index: int) -> Dict:
        """
        为指定场景的指定图片生成高清版本
        
        Args:
            scene_id: 场景ID，如'scene_001'
            image_index: 要高清化的图片索引
            
        Returns:
            Dict: 高清图片信息
        """
        # 检查场景是否存在
        if scene_id not in self.scene_results:
            print(f"错误: 场景 {scene_id} 不存在")
            return None
            
        scene_data = self.scene_results[scene_id]
        
        # 检查图片索引是否有效
        if image_index < 0 or image_index >= len(scene_data.get('all_images', [])):
            print(f"错误: 图片索引 {image_index} 超出范围")
            return None
            
        try:
            # 提取场景信息
            scene_prompt = scene_data['prompt']
            negative_prompt = scene_data['negative_prompt']
            seed = scene_data['seeds'][image_index] if len(scene_data['seeds']) > image_index else -1
            use_regional_prompter = scene_data['use_regional_prompter']
            regional_prompt_ratios = scene_data['regional_prompt_ratios']
            
            print(f"正在为场景 {scene_id} 的图片 {image_index} 生成高清版本...")
            
            # 生成高清图片
            self.sd_generator.generate_prompt(
                prompt=scene_prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=1,
                use_regional_prompter=use_regional_prompter,
                regional_prompt_mode="Columns",
                regional_prompt_ratios=regional_prompt_ratios,
                enable_hr=True  # 启用高清修复
            )
            self.sd_generator.get_img()
            
            # 创建高清图片目录
            hd_folder = os.path.join(self.output_dir, f"{scene_id}_hd")
            self.ensure_dir_exists(hd_folder)
            
            # 保存高清图片
            base_save_path = os.path.join(hd_folder, f"{scene_id}_hd")
            hd_index = self.sd_generator.save_img(base_save_path)
            hd_path = f"{base_save_path}_{hd_index}.png"
            
            # 更新场景数据
            hd_info = {
                "path": hd_path,
                "seed": self.sd_generator.seeds[0] if hasattr(self.sd_generator, 'seeds') and self.sd_generator.seeds else seed,
                "original_index": image_index
            }
            
            self.scene_results[scene_id]['hd_image'] = hd_info
            
            # 更新场景归档
            self.save_json_file(self.scene_archive_file, self.scene_results)
            
            print(f"高清图片已保存到: {hd_path}")
            return hd_info
            
        except Exception as e:
            print(f"错误: 生成高清图片失败: {str(e)}")
            return None
    
    def load_scene_archive(self) -> Dict:
        """
        加载场景归档数据
        
        Returns:
            Dict: 场景归档数据
        """
        self.scene_results = self.load_json_file(self.scene_archive_file)
        return self.scene_results

def main():
    # 使用示例
    generator = SceneImageGenerator(novel_name="斗破苍穹节选")
    result = generator.process_scenes()
    
    # 打印所有场景信息并进行高清修复
    if result:
        print("\n开始处理所有场景的高清修复...")
        for scene_id in result:
            print(f"\n当前处理场景数据：")
            print(json.dumps(result[scene_id], ensure_ascii=False, indent=2))
            
            # 对该场景的指定图片进行高清修复
            img_index = int(input(f"请输入要处理的图片索引 (默认为{result[scene_id]['selected_image_index']}): ") or result[scene_id]['selected_image_index'])
            print(f"\n正在处理场景 {scene_id} 的第 {img_index} 张图片...")
            generator.generate_hd_image(scene_id, img_index)
            # 场景之间添加延迟
            if scene_id != list(result.keys())[-1]:
                import time
                time.sleep(3)

if __name__ == "__main__":
    main() 