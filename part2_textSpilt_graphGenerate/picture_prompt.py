"""
从part2_textSpilt_graphGenerate\role_message\novel_scenes.json
以及part2_textSpilt_graphGenerate\role_message\character_archive.json
提炼出提示词
"""

import json
import os
import time
from Models import os_setenv, get_gemini_2_flash, get_zhupuai_model
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver

# 状态类型定义，用于记忆
class State(TypedDict):
    messages: Annotated[list, add_messages]
    current_scene: Dict
    characters: Dict
    identified_roles: List[str]
    prompt: str

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_characters_to_dict(characters_list):
    """将角色列表转换为字典格式"""
    characters_dict = {}
    for char in characters_list:
        characters_dict[char['name']] = {
            'role': char.get('role', ''),
            'photo_prompt': char.get('photo_prompt', ''),
            'visual_reference': char.get('visual_reference', '')
        }
    return characters_dict

def identify_characters_agent(state: State):
    """使用大模型判断场景中出现的角色"""
    print("正在识别场景中的角色...")
    
    try:
        # 首先尝试使用Gemini模型
        gemini_model = get_gemini_2_flash()
        model = gemini_model
    except Exception as e:
        print(f"Gemini模型调用失败，切换到智普模型: {e}")
        # 如果Gemini失败，使用智普模型作为备选
        model = get_zhupuai_model()
    
    scene = state["current_scene"]
    characters = state["characters"]
    scene_text = f"场景描述: {scene['description']}\n原文: {scene['original_text']}"
    
    print(f"当前处理场景: {scene_text[:100]}...")
    
    # 构建提示内容
    character_info = "可能出现的角色包括：\n"
    for char_name, char_info in characters.items():
        character_info += f"- {char_name}: {char_info['role']}\n"

    print(character_info)
    
    prompt_request = f"""
    你是一个精确的文本分析助手。请分析以下场景中出现了哪些角色。

    {scene_text}
    
    {character_info}
    
    请只列出在这个场景中实际出现的角色名称（不要推测）。如果场景中提到"他"、"她"等代词，请根据上下文判断指代的是哪个角色。
    回复格式：仅返回角色名称的列表，用逗号分隔，不需要其他解释。如果没有出现任何已知角色，请回复"无已知角色"。
    """
    
    # 添加延时，防止API调用过于频繁
    time.sleep(3)
    
    # 调用模型识别角色
    try:
        response = model.invoke(prompt_request)
        
        # 解析响应，获取角色列表
        roles_text = response.content.strip()
        print(f"模型返回的角色: {roles_text}")
        
        if roles_text == "无已知角色":
            identified_roles = []
        else:
            identified_roles = [role.strip() for role in roles_text.split(',')]
        
        # 过滤确认角色存在于character_archive中
        valid_roles = [role for role in identified_roles if role in characters]
        print(f"有效角色: {valid_roles}")
        
        return {
            "identified_roles": valid_roles,
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"角色识别失败: {e}")
        # 发生错误时返回空角色列表
        return {
            "identified_roles": [],
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=f"错误: {e}")]
        }

def generate_prompt_for_scene(state: State):
    """为场景生成文生图提示词"""
    print("正在生成场景提示词...")
    
    try:
        # 首先尝试使用Gemini模型
        gemini_model = get_gemini_2_flash()
        model = gemini_model
    except Exception as e:
        print(f"Gemini模型调用失败，切换到智普模型: {e}")
        # 如果Gemini失败，使用智普模型作为备选
        model = get_zhupuai_model()
    
    scene = state["current_scene"]
    characters = state["characters"]
    identified_roles = state["identified_roles"]
    
    scene_info = f"场景描述: {scene['description']}\n原文: {scene['original_text']}"
    characters_info = ""
    
    for char_name in identified_roles:
        if char_name in characters:
            char_info = characters[char_name]
            characters_info += f"\n角色: {char_name}, 描述: {char_info['photo_prompt']}"
    
    # 构建提示内容
    prompt_request = f"""
    你是一个专业的小说分析与Stable Diffusion提示词优化专家。请根据以下场景和角色信息，生成一个高质量的文生图提示词。

    场景信息：
    {scene_info}
    
    角色信息：
    {characters_info if characters_info else '场景中没有明确出现已知角色'}
    
    请生成一个高质量的Stable Diffusion正向提示词，要求：
    发挥你的想象力，尽可能扩写场景描述，包含人物描写，背景细节，动作细节
    1. 词组化：将描述拆解为符合Stable Diffusion语法的关键词英文短语，用英文逗号分隔
    2. 层次化：按以下类别构造提示词：
       - 人物特征（如外貌、表情、服装等）
       - 环境信息（如场景、背景等）
       - 光线条件（如光照效果）
       - 视角构图（如wide angle, close-up等）
       - 画质增强（如ultra-detailed, 8K, masterpiece等）
    3. 优化要求：
       - 确保提示词逻辑清晰，遵循"主语→场景→光线→视角→画质"的顺序
       - 添加高质量关键词如masterpiece, best quality, ultra-detailed
       - 使用unreal engine rendered等提升细节
       - 对重要特征使用权重调整，如(golden hair:1.2)
       - 避免使用ugly, deformed, blurry, low quality等负面词汇
    4. 保持提示词在50-60个字之间，注重场景的视觉效果和氛围
    
    请直接返回生成的提示词，不需要其他解释。
    """
    
    # 添加延时，防止API调用过于频繁
    time.sleep(2)
    
    # 调用模型生成提示词
    try:
        response = model.invoke(prompt_request)
        print(f"生成的提示词: {response.content[:100]}...")
        
        return {
            "prompt": response.content,
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"提示词生成失败: {e}")
        # 发生错误时返回默认提示词
        default_prompt = f"根据场景描述生成一张图片: {scene['description']}"
        return {
            "prompt": default_prompt,
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=f"错误: {e}")]
        }

def process_scenes():
    print("开始处理场景...")
    # 设置环境变量
    os_setenv()
    
    # 加载场景和角色文件
    scenes_file = "part2_textSpilt_graphGenerate/role_message/novel_scenes.json"
    characters_file = "part2_textSpilt_graphGenerate/role_message/character_archive.json"
    
    print(f"加载数据文件: {scenes_file}")
    scenes_data = load_json_file(scenes_file)
    print(f"加载数据文件: {characters_file}")
    characters_data = load_json_file(characters_file)
    
    # 将角色列表转换为字典格式
    characters_dict = convert_characters_to_dict(characters_data["characters"])
    
    # 构建状态流图
    print("构建工作流...")
    workflow = StateGraph(State)
    
    # 添加节点
    workflow.add_node("identify_characters", identify_characters_agent)
    workflow.add_node("generate_prompt", generate_prompt_for_scene)
    
    # 添加边缘连接
    workflow.add_edge(START, "identify_characters")
    workflow.add_edge("identify_characters", "generate_prompt")
    
    # 配置内存保存器用于记忆
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    # 结果列表
    results = []
    
    # 处理每个场景
    total_scenes = len(scenes_data["scenes"])
    for index, scene in enumerate(scenes_data["scenes"]):
        print(f"\n===== 处理场景 {index+1}/{total_scenes} =====")
        # 如果场景太多，可以限制测试数量
        # if index >= 3:  # 测试时只处理前3个场景
        #     break
            
        # 初始化状态
        initial_state = {
            "messages": [],
            "current_scene": scene,
            "characters": characters_dict,
            "identified_roles": [],
            "prompt": ""
        }
        
        # 使用唯一ID作为线程ID
        config = {"configurable": {"thread_id": f"scene_{index}"}}
        
        try:
            # 执行工作流
            print(f"执行场景 {index+1} 的工作流")
            final_state = graph.invoke(initial_state, config)
            
            # 从最终状态提取结果
            roles = final_state["identified_roles"]
            prompt = final_state["prompt"]
            
            # 构建场景结果
            scene_result = {
                "prompt": prompt,
                "roles": roles,
                "roles_photo": {name: characters_dict[name]["visual_reference"] 
                               for name in roles if name in characters_dict}
            }
            
            results.append(scene_result)
            print(f"场景 {index+1} 处理完成")
        except Exception as e:
            print(f"场景 {index+1} 处理失败: {e}")
            # 发生错误时添加空结果
            scene_result = {
                "prompt": f"处理错误: {e}",
                "roles": [],
                "roles_photo": {}
            }
            results.append(scene_result)
        
        # 在每个场景之间添加额外延时
        time.sleep(3)
    
    # 保存结果到文件
    output_file = "part2_textSpilt_graphGenerate/role_message/scene_prompts.json"
    print(f"\n保存结果到文件: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"scene_prompts": results}, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    process_scenes()
