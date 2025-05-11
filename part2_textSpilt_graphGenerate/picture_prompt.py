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
import argparse
from prompt_templates import SCENE_PROMPT
import re

# 状态类型定义，用于记忆
class State(TypedDict):
    messages: Annotated[list, add_messages]
    current_scene: Dict
    id_to_name: Dict[str, str]
    name_to_prompt: Dict[str, str]
    identified_roles: List[str]
    prompt: str

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_characters_to_dict(characters_data):
    """将角色数据转换为字典格式"""
    characters_dict = {}
    for char_id, char_info in characters_data.items():
        characters_dict[char_info['name']] = {
            'role': '',  # 新格式中没有role字段
            'photo_prompt': char_info.get('prompt', ''),
            'visual_reference': char_info.get('path', '')
        }
    return characters_dict

def create_character_mapping(characters_data):
    """创建角色ID和名称的映射关系"""
    id_to_name = {}
    name_to_prompt = {}
    for char_id, char_info in characters_data.items():
        id_to_name[char_id] = char_info['name']
        name_to_prompt[char_info['name']] = char_info['prompt']
    return id_to_name, name_to_prompt

def identify_characters_agent(state: State):
    """使用大模型判断场景中出现的角色"""
    print("正在识别场景中的角色...")
    
    try:
        gemini_model = get_gemini_2_flash()
        model = gemini_model
    except Exception as e:
        print(f"Gemini模型调用失败，切换到智普模型: {e}")
        model = get_zhupuai_model()
    
    scene = state["current_scene"]
    id_to_name = state["id_to_name"]
    scene_text = f"场景描述: {scene['description']}\n原文: {scene['original_text']}"
    
    print(f"当前处理场景: {scene_text[:100]}...")
    
    # 构建提示内容
    character_info = "可能出现的角色包括：\n"
    for _, name in id_to_name.items():
        character_info += f"- {name}\n"

    print(character_info)
    
    prompt_request = f"""
    你是一个精确的文本分析助手。请分析以下场景中出现了哪些角色。

    {scene_text}
    
    {character_info}
    
    请只列出在这个场景中实际出现的角色名称（不要推测）。如果场景中提到"他"、"她"等代词，请根据上下文判断指代的是哪个角色。
    回复格式：仅返回角色名称的列表，用逗号分隔，不需要其他解释。如果没有出现任何已知角色，请回复"无已知角色"。
    """
    
    time.sleep(3)
    
    try:
        response = model.invoke(prompt_request)
        roles_text = response.content.strip()
        print(f"模型返回的角色: {roles_text}")
        if isinstance(roles_text, str):
            if roles_text == "无已知角色":
                identified_roles = []
            else:
                identified_roles = [role.strip() for role in roles_text.split(',')]
        elif isinstance(roles_text, list):
            identified_roles = [role.strip() for role in roles_text]
        else:
            print("无法解析的角色格式:", roles_text)
            identified_roles = []

        
        
        # 过滤确认角色存在于映射中
        valid_roles = [role for role in identified_roles if role in state["name_to_prompt"]]
        print(f"有效角色: {valid_roles}")
        
        return {
            "identified_roles": valid_roles,
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"角色识别失败: {e}")
        return {
            "identified_roles": [],
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=f"错误: {e}")]
        }

def generate_prompt_for_scene(state: State):
    """为场景生成文生图提示词"""
    print("正在生成场景提示词...")
    
    try:
        gemini_model = get_gemini_2_flash()
        model = gemini_model
    except Exception as e:
        print(f"Gemini模型调用失败，切换到智普模型: {e}")
        model = get_zhupuai_model()
    
    scene = state["current_scene"]
    identified_roles = state["identified_roles"]
    
    prompt_request = f"""
    你是一个专业的小说分析与Stable Diffusion提示词优化专家。请根据以下场景生成场景提示词（不包含人物描述）。
    场景信息：
    描述: {scene['description']}
    
    注意：分析场景,将场景场景内容使用简要的英文词组表达出来,不需要特别详细
        - 开头必须以人数开始附带每个人的性别 比如(2 people,a girl and a boy:1.4)或者(2 girl:1.4),必须使用括号强调!!!
        - 镜头，比如：中景、远景、特写等
        - 背景：背景建筑/室内/家具等
        - 之后换行(重要)
        - 人物：必须先写出识别出的人物名称,(禁止出现人物的外貌描写),然后写该角色的穿搭，动作，表情，以及一些道具辅助。比如"张三，西装，坐在椅子上，手中拿着杯子"。写完后换行进行下一个人物。
    请按照以下JSON格式生成提示词：
    {{
        "roles": "{', '.join(identified_roles)}",
        "prompt": "场景提示词（不包含人物外貌描述，但要包含人物的动作、服装等。5-15个词组）"
    }}
    注意：生成的角色数组必须按照 [角色1,角色2,角色3] 格式，不要添加任何其他格式。
    生成提示词要求：
    1. 必须包含以上所有内容，不要遗漏。
    2. 不要添加任何markdown标记或其他格式。
    3. 不要添加任何解释或说明。
    4. 不要添加任何人物外貌描写，只需包含人物个数以及人物的服装、动作、姿态等。
    6. 不要太夸张的描述
    7. 不能为空
    8. 调整关键字强度的等效方法是使用 () 和 []。 (keyword) 将tag的强度增加 1.1 倍，与 (keyword:1.1) 相同，最多可加三层。 [keyword] 将强度降低 0.9 倍，与 (keyword:0.9) 相同。
    请直接返回JSON格式的结果，不要添加任何markdown标记或其他格式。
    """
    
    time.sleep(2)
    
    try:
        response = model.invoke(prompt_request)
        response_text = response.content.strip()
        print(f"生成的提示词: {response_text[:100]}...")
        
        # 清理响应文本，移除可能的markdown标记
        if response_text.startswith('```'):
            # 找到第一个和最后一个```的位置
            start = response_text.find('\n') + 1
            end = response_text.rfind('```')
            if end == -1:  # 如果没有找到结束标记
                end = len(response_text)
            response_text = response_text[start:end].strip()
        
        # 如果响应文本以'json'开头，移除它
        if response_text.startswith('json'):
            response_text = response_text[4:].strip()
        
        # 解析JSON响应
        prompt_data = json.loads(response_text)
        
        # 处理提示词
        if isinstance(prompt_data["roles"], str):
        
            roles = [role.strip() for role in prompt_data["roles"].split(',')]
        elif isinstance(prompt_data["roles"], list):
            roles = [role.strip() for role in prompt_data["roles"]]
        else:
            print("无法解析的角色格式:", prompt_data["roles"])
            roles = []
       
        base_prompt = prompt_data["prompt"]
        
        # 构建最终提示词
        final_prompt = base_prompt

        if roles:
            # 过滤出实际存在于 name_to_prompt 中的角色
            valid_roles = [role for role in roles if role in state["name_to_prompt"]]

            if valid_roles:
                for role in valid_roles:
                    role_desc = state["name_to_prompt"][role]

                    # 替换 base_prompt 中的角色名为其描述（确保只替换单词边界）
                    final_prompt = re.sub(rf'\b{re.escape(role)}\b', role_desc, final_prompt)

        return {
            "prompt": final_prompt,
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"提示词生成失败: {e}")
        return {
            "prompt": f"处理错误: {e}",
            "messages": [HumanMessage(content=prompt_request), AIMessage(content=f"错误: {e}")]
        }

def process_scenes(scenes_file: str, characters_file: str, output_file: str):
    """
    处理场景并生成提示词
    Args:
        scenes_file (str): 场景JSON文件路径
        characters_file (str): 角色JSON文件路径
        output_file (str): 输出文件路径
    """
    print("开始处理场景...")
    os_setenv()
    
    print(f"加载数据文件: {scenes_file}")
    scenes_data = load_json_file(scenes_file)
    print(f"加载数据文件: {characters_file}")
    characters_data = load_json_file(characters_file)
    
    # 创建角色映射
    id_to_name, name_to_prompt = create_character_mapping(characters_data)
    
    workflow = StateGraph(State)
    
    workflow.add_node("identify_characters", identify_characters_agent)
    workflow.add_node("generate_prompt", generate_prompt_for_scene)
    
    workflow.add_edge(START, "identify_characters")
    workflow.add_edge("identify_characters", "generate_prompt")
    
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    results = []
    
    # 限制处理前10个场景
    # scenes_to_process = scenes_data["scenes"][:10]
    scenes_to_process = scenes_data["scenes"]
    total_scenes = len(scenes_to_process)
    print(f"\n将处理前{total_scenes}个场景...")
    
    for index, scene in enumerate(scenes_to_process):
        print(f"\n===== 处理场景 {index+1}/{total_scenes} =====")
        
        initial_state = {
            "messages": [],
            "current_scene": scene,
            "id_to_name": id_to_name,
            "name_to_prompt": name_to_prompt,
            "identified_roles": [],
            "prompt": ""
        }
        
        config = {"configurable": {"thread_id": f"scene_{index}"}}
        
        try:
            final_state = graph.invoke(initial_state, config)
            
            scene_result = {
                "prompt": final_state["prompt"],
                "roles": final_state["identified_roles"]
            }
            
            results.append(scene_result)
            print(f"场景 {index+1} 处理完成")
        except Exception as e:
            print(f"场景 {index+1} 处理失败: {e}")
            scene_result = {
                "prompt": f"处理错误: {e}",
                "roles": []
            }
            results.append(scene_result)
        
        time.sleep(3)
    
    print(f"\n保存结果到文件: {output_file}")
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"scene_prompts": results}, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成，结果已保存到 {output_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='处理小说场景并生成图片提示词')
    parser.add_argument('--scenes_file', type=str, 
                        default="part2_textSpilt_graphGenerate/斗破苍穹节选/role_message/novel_scenes.json",
                        help='场景JSON文件路径')
    parser.add_argument('--characters_file', type=str, 
                        default="part2_textSpilt_graphGenerate/斗破苍穹节选/role_message/character_archive.json",
                        help='角色JSON文件路径')
    parser.add_argument('--output_file', type=str, 
                        default="part2_textSpilt_graphGenerate/斗破苍穹节选/role_message/scene_prompts.json",
                        help='输出文件路径')
    
    args = parser.parse_args()
    
    process_scenes(
        scenes_file=args.scenes_file,
        characters_file=args.characters_file,
        output_file=args.output_file
    )
