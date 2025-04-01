"""测试智普以及gemini"""
#智普：
from Models import os_setenv
from Models import get_gemini_2_flash
from Models import get_zhupuai_model
from Models import get_gemini_photo
from PIL import Image
from io import BytesIO
import os

os_setenv()

# chat_zhipu=get_zhupuai_model()
# print(chat_zhipu.invoke("你叫什么名字").content)


# #gemini
# chat_gemini=get_gemini_2_flash()
# print(chat_gemini.invoke("你叫什么名字").content)

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 加载参考图像
image_path = os.path.join(current_dir, "test_output", "test_image.jpg")
reference_image = Image.open(image_path)

lu_image = Image.open("part2_textSpilt_graphGenerate\\character_portraits\\阿诺.jpg")

# 创建提示词
img2img_prompt = "Wide-angle shot, scorching summer, August, bustling street scene. Asphalt shimmering with heat haze, cars weaving through traffic, crowded sidewalks with pedestrians. Intense sunlight, long shadows. Dynamic composition, sense of urgency and heat. Focus on textures: rough asphalt, gleaming metal of cars, colorful clothing of pedestrians. High contrast, vibrant colors, realistic rendering. Capture the feeling of oppressive heat and urban energy. Consider adding details like advertisements, street vendors, and architectural elements to enhance the realism."
contents=[img2img_prompt]
img_response=get_gemini_photo(contents=contents)


# 处理响应
for part in img_response.candidates[0].content.parts:
    if part.text is not None:
        print(f"图生图响应文本: {part.text}")
    
    elif part.inline_data is not None:
        # 保存新图像
        output_path = os.path.join(current_dir, "test_output", "test_image_updated_test.jpg")
        image = Image.open(BytesIO(part.inline_data.data))
        image.save(output_path)
        print(f"图生图结果已保存到: {output_path}")