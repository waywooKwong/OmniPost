"""
主函数，用于调用其他模块，生成小说场景和角色图像。
"""

from novel_handle import NovelSceneGenerator
from role_extract import RoleExtractor
from scene_extract import SceneExtractor
from scene_image_generator import SceneImageGenerator
import os
def main(novel_path: str,output_dir: str):
    """
    主函数，用于调用其他模块，生成小说场景和角色图像。
    """

    # 0. 设置输出目录
      # 获取小说名称
    novel_name = os.path.splitext(os.path.basename(novel_path))[0]
        
    # 创建小说专属目录
    novel_dir = os.path.join(output_dir, novel_name)
    # 确保目录存在
    os.makedirs(novel_dir, exist_ok=True)



    # 1. 提取角色   
    # role_extractor = RoleExtractor(novel_path,novel_dir)
    # role_extractor.process_novel()

    # # 2. 提取场景
    # novel_scene_generator = NovelSceneGenerator(novel_path,novel_dir)
    # novel_scene_generator.process_novel()
    # scene_path = os.path.join(novel_dir, "role_message", "novel_scenes.json")
    # # # 3. 生成提示词
    # prompt_path = os.path.join(novel_dir, "role_message", "novel_scenes_prompt.json")
    # scene_prompt_generator = SceneExtractor(scene_path,prompt_path)
    # scene_prompt_generator.process()

    # # 4. 生成场景图像
    output_dir = os.path.join(novel_dir,"images")
    scene_image_generator = SceneImageGenerator(novel_dir,output_dir,novel_name)
    scene_image_generator.process_scenes()

if __name__ == "__main__":
    main(novel_path="part2_textSpilt_graphGenerate/files/斗破苍穹节选.txt",output_dir="result")