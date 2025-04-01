import os
import json
from PIL import Image
from io import BytesIO
import sys
from Models import get_gemini_photo

def ensure_dir_exists(dir_path):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"已创建目录: {dir_path}")

def load_scenes(json_file):
    """加载场景数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['scenes']

def generate_scene_image(prompt, prev_image=None):
    """生成场景图片"""
    # 准备内容
    if prev_image:
        contents = [prompt, prev_image]
    else:
        contents = prompt
    
    # 调用Gemini API生成图片
    response = get_gemini_photo(contents)
    
    # 处理响应
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            # 返回图片数据
            return Image.open(BytesIO(part.inline_data.data))
    
    return None

def main():
    # 确保输出目录存在
    output_dir = "part2_textSpilt_graphGenerate/output_images"
    ensure_dir_exists(output_dir)
    
    # 加载场景数据
    scenes_file = "part2_textSpilt_graphGenerate/role_message/novel_scenes.json"
    scenes = load_scenes(scenes_file)
    
    # 上一个生成的图片，初始为None
    prev_image = None
    
    # 遍历场景生成图片
    for i, scene in enumerate(scenes):
        print(f"正在生成场景 {i+1}/{len(scenes)}...")
        
        # 构建提示词
        description = scene["description"]
       

        prompt = f"{description}\n,Adopt comic book style,"
        
        # 生成图片
        try:
            image = generate_scene_image(prompt, prev_image)
            if image:
                # 保存图片
                output_path = os.path.join(output_dir, f"scene_{i+1:03d}.jpg")
                image.save(output_path)
                print(f"场景图片已保存到: {output_path}")
                
                # 更新前一个图片
                prev_image = image
            else:
                print(f"警告: 场景 {i+1} 图片生成失败")
        except Exception as e:
            print(f"错误: 场景 {i+1} 图片生成失败: {str(e)}")
    
    print("所有场景图片生成完成!")


if __name__ == "__main__":
    main() 