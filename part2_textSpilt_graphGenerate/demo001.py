from google import genai
from google.genai import types
from PIL import Image
import textwrap
import json
from io import BytesIO
import os
# 初始化客户端
client = genai.Client(api_key="AIzaSyBlyxoeYOp5LKGut64EsocjhluN-KVc8h8")

class NovelVisualizer:
    def __init__(self):
        self.context = {
            "characters": {},
            "current_scene": {},
            "previous_elements": []
        }
        self.image_counter = 1
        self.output_dir = "part2_textSpilt_graphGenerate\img_001"
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse_chapter(self, chapter_text: str) -> list:
        """使用LLM解析章节为分镜列表"""
        prompt = textwrap.dedent(f"""
        将以下小说章节转换为分镜头描述，保持角色和场景的连续性。
        请确保输出是有效的JSON格式。
        
        章节内容：
        {chapter_text}
        
        请按照以下格式输出：
        {{
            "scenes": [
                {{
                    "scene_num": 1,
                    "description": "详细场景描述（包含角色特征）",
                    "key_elements": ["元素1", "元素2"],
                    "camera_angle": "镜头角度（如：全景/特写）"
                }}
            ]
        }}
        """)

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # 尝试清理和解析JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            try:
                parsed_data = json.loads(response_text.strip())
                return parsed_data.get("scenes", [])
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {response_text}")
                return [{
                    "scene_num": 1,
                    "description": response_text[:200],
                    "key_elements": ["默认元素"],
                    "camera_angle": "全景"
                }]
        except Exception as e:
            print(f"API调用错误: {e}")
            return []

    def _build_image_prompt(self, scene_data: dict) -> str:
        """构建包含一致性信息的提示词"""
        character_desc = "\n".join(
            [f"{k}: {v['description']}" 
             for k, v in self.context["characters"].items()]
        )
        
        return textwrap.dedent(f"""
        根据以下要求生成连贯的3D渲染风格图像：
        
        当前场景：{scene_data['description']}
        镜头角度：{scene_data['camera_angle']}
        
        角色特征：
        {character_desc}
        
        需要保持的连续性元素：
        {", ".join(self.context["previous_elements"][-3:])}
        
        风格要求：
        - 电影级光照效果
        - 细节丰富的材质纹理
        - 保持场景元素连续性
        """)

    def generate_scene_image(self, scene_data: dict) -> Image.Image:
        """生成并保存场景图片"""
        try:
            # 构建增强提示词
            full_prompt = self._build_image_prompt(scene_data)
            
            # 调用生成API
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",  # 使用新推荐的模型
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            print(f"场景 {scene_data['scene_num']} 描述: {response.text}")

            # 处理生成的内容
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # 保存图像
                    image = Image.open(BytesIO((part.inline_data.data)))
                    output_path = os.path.join(self.output_dir, f"scene_{self.image_counter:03d}.png")
                    image.save(output_path)
                    self.image_counter += 1
                    return f"图像已成功生成并保存到: {output_path}"
            
            # 更新上下文
            self._update_context(scene_data)
            return None
        except Exception as e:
            print(f"场景生成错误: {e}")
            return None

    def _update_context(self, scene_data: dict):
        """更新角色和场景上下文"""
        # 提取角色信息
        for element in scene_data["key_elements"]:
            if "角色" in element:
                name, desc = element.split(":", 1)
                self.context["characters"][name.strip()] = {
                    "description": desc.strip(),
                    "appear_count": self.context["characters"].get(name, {}).get("appear_count", 0) + 1
                }
        
        # 保留最近5个关键元素
        self.context["previous_elements"] = (self.context["previous_elements"] + scene_data["key_elements"])[-5:]

# 使用示例
if __name__ == "__main__":
    visualizer = NovelVisualizer()
    
    # 示例章节文本
    chapter = """
    第一章 天空之城
    张伟穿着标志性的红色皮夹克，站在悬浮平台的边缘。他左脸的伤疤在晨光中格外明显，手中的能量剑发出嗡嗡声。远处，钢铁巨塔的玻璃幕墙反射着朝阳，飞行器在建筑群间穿梭...
    """
    
    scenes = visualizer.parse_chapter(chapter)
    
    for scene in scenes:
        print(f"生成场景 {scene['scene_num']}...")
        img = visualizer.generate_scene_image(scene)
       