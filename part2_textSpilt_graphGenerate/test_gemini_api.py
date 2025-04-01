import os
import sys
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

def test_gemini_api():
    """测试Gemini API的文本和图像生成功能"""
    try:
        # 配置Gemini API
        print("配置Gemini API...")
       
        client = genai.Client(api_key="AIzaSyC93MxOUrGCH-VOMTM5JVW6tRvgGQy1XcE")
        
        # 测试文本生成
        print("\n1. 测试文本生成功能...")
        text_prompt = "请用三句话描述春天的景色。"
        text_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text_prompt
        )
        print(f"文本生成结果: {text_response.text}")
        
        # 测试图像生成
        print("\n2. 测试图像生成功能...")
        image_prompt = "创建一幅美丽的春季山水画，有山丘、河流和开花的树木。采用中国传统水墨画风格。"
        
        try:
            img_response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=image_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # 处理响应
            image_saved = False
            for part in img_response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"图像生成响应文本: {part.text}")
                
                elif part.inline_data is not None:
                    # 确保输出目录存在
                    os.makedirs("test_output", exist_ok=True)
                    
                    # 保存图像
                    output_path = "test_output/test_image.jpg"
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(output_path)
                    image_saved = True
                    print(f"图像已保存到: {output_path}")
            
            if not image_saved:
                print("警告: 响应中没有找到图像数据")
                
        except Exception as e:
            print(f"图像生成失败: {str(e)}")
        
        # 测试图生图功能
        if os.path.exists("test_output/test_image.jpg"):
            print("\n3. 测试图生图功能...")
            try:
                # 加载参考图像
                reference_image = Image.open("test_output/test_image.jpg")
                
                # 创建提示词
                img2img_prompt = "基于这张山水图，添加一些小动物和人物，保持相同的艺术风格。"
                
                # 调用API
                img2img_response = client.models.generate_content(
                    model="gemini-2.0-flash-exp-image-generation",
                    contents=[img2img_prompt, reference_image],
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image']
                    )
                )
                
                # 处理响应
                for part in img2img_response.candidates[0].content.parts:
                    if part.text is not None:
                        print(f"图生图响应文本: {part.text}")
                    
                    elif part.inline_data is not None:
                        # 保存新图像
                        output_path = "test_output/test_image_updated.jpg"
                        image = Image.open(BytesIO(part.inline_data.data))
                        image.save(output_path)
                        print(f"图生图结果已保存到: {output_path}")
                
            except Exception as e:
                print(f"图生图功能测试失败: {str(e)}")
        
        # 测试多图输入的图生图功能
        print("\n4. 测试多图输入的图生图功能...")
        try:
            # 加载角色图像
            lu_image = Image.open("character_portraits/鲁四老爷.jpg")
            xiangling_image = Image.open("character_portraits/祥林嫂.jpg")
            
            # 创建提示词
            multi_img_prompt = "基于这两张角色图像，创建一个场景图，展示鲁四老爷和祥林嫂在雪夜正在交谈，保持原有的艺术风格。"
            
            # 调用API，传入多张图片
            multi_img_response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=[multi_img_prompt, lu_image, xiangling_image],
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # 处理响应
            multi_img_saved = False
            for part in multi_img_response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"多图输入响应文本: {part.text}")
                
                elif part.inline_data is not None:
                    # 保存新图像
                    output_path = "test_output/multi_image_result.jpg"
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(output_path)
                    multi_img_saved = True
                    print(f"多图输入结果已保存到: {output_path}")
            
            if not multi_img_saved:
                print("警告: 多图输入响应中没有找到图像数据")
                
        except Exception as e:
            print(f"多图输入图生图功能测试失败: {str(e)}")
        
        print("\nAPI测试完成!")
        return True
        
    except Exception as e:
        print(f"Gemini API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gemini_api() 