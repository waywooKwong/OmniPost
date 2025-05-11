"""
调用 stablediffusion 生成图片，并提供FastAPI接口


"""
import json
import requests
import io
import base64
from PIL import Image
import os
from typing import List, Optional, Union, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# url = "http://127.0.0.1:7860"
 
# prompt = "dog"
# negative_prompt = ""
 
# payload = {
 
#     # 模型设置
#     "override_settings":{
#           "sd_model_checkpoint": "realisticVisionV51_v51VAE.safetensors [15012c538f]",
#           "sd_vae": "animevae.pt",
#           "CLIP_stop_at_last_layers": 2,
#     },
 
#     # 基本参数
#     "prompt": prompt,
#     "negative_prompt": negative_prompt,
#     "steps": 30,
#     "sampler_name": "Euler a",
#     "width": 512,
#     "height": 512,
#     "batch_size": 1,
#     "n_iter": 1,
#     "seed": 1,
#     "CLIP_stop_at_last_layers": 2,
 
#     # 面部修复 face fix
#     "restore_faces": False,
 
#     #高清修复 highres fix
#     # "enable_hr": True,
#     # "denoising_strength": 0.4,
#     # "hr_scale": 2,
#     # "hr_upscaler": "Latent",
 
# # }
 
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
# r = response.json()
# image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
 
# image.show()
# image.save('output.png')

# FastAPI 请求模型定义
class SDGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    batch_size: int = Field(default=1, ge=1, le=4)
    seed: int = Field(default=-1)
    sampler_name: str = "Euler a"
    use_regional_prompter: bool = False
    regional_prompt_mode: str = "Columns"
    regional_prompt_ratios: str = "1,1"
    enable_hr: bool = False
    model_name: str = "wolfboys2D_v10.safetensors [62d679b7a0]"
    save_dir: Optional[str] = None

# FastAPI 响应模型定义
class SDGenerateResponse(BaseModel):
    images: List[str]
    seeds: List[int]
    info: Dict[str, Any]
    save_paths: Optional[List[str]] = None

class SD_Generate:
    def __init__(self) -> None:
        #初始化定义
        self.url="http://127.0.0.1:7860"
    def generate_prompt(
            self,
           prompt,
           negative_prompt,
           batch_size=1,
           seed=-1,
           sampler_name="Euler a",
           #使用区域提示器
           use_regional_prompter=False,
           regional_prompt_mode="Columns",
           regional_prompt_ratios="1,1",
           #高清修复
           enable_hr=False,
           #选择模型
           model_name="wolfboys2D_v10.safetensors [62d679b7a0]",
    ):
        self.payload = {
            # 模型设置
            "override_settings":{
                "sd_model_checkpoint": model_name,
                "sd_vae": "vae-ft-mse-840000-ema-pruned.safetensors",
                "CLIP_stop_at_last_layers": 2,
            },
            # 基本参数
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": 25,
            "sampler_name": sampler_name,
            "width": 512,
            "height": 768,
            "batch_size": batch_size,
            "n_iter": 1,
            "seed": seed,
            # "CLIP_stop_at_last_layers": 2,
        
            # 面部修复 face fix
            "restore_faces": False,

            #高清修复 highres fix
            "enable_hr": enable_hr,
            "denoising_strength": 0.3,#降噪强度
            "hr_scale": 2,#放大倍数
            "hr_upscaler": "R-ESRGAN 4x+",#放大算法
            "hr_second_pass_steps": 30,#放大次数
        }
        
        # 添加区域提示器(Regional Prompter)插件API调用
        if use_regional_prompter:
            self.payload["alwayson_scripts"] = {
                "Regional Prompter": {
                    "args": [
                        True,             # Active
                        False,            # debug
                        "Matrix",         # Mode
                        regional_prompt_mode,  # Mode (Matrix): Horizontal, Vertical, Columns, Rows
                        "Mask",           # Mode (Mask)
                        "Prompt",         # Mode (Prompt)
                        regional_prompt_ratios,  # Ratios
                        "0.2",              # Base Ratios
                        False,            # Use Base
                        True,            # Use Common
                        False,            # Use Neg-Common
                        "Latent",      # Calcmode
                        False,            # Not Change AND
                        "0",              # LoRA Textencoder
                        "0",              # LoRA U-Net
                        "0",              # Threshold
                        "",               # Mask
                    ]
                }
            }
    
    def get_img(self):
        # 对本地连接不使用代理
        local_session = requests.Session()
        local_session.trust_env = False  # 不使用环境变量中的代理设置
        
        try:
            response = local_session.post(url=f'{self.url}/sdapi/v1/txt2img', json=self.payload)
            self.r = response.json()
            
            # 检查是否成功获取到响应内容
            if 'images' not in self.r:
                print("警告：未在返回结果中找到图像数据")
                print(f"返回内容：{self.r}")
                return
            
            # 解析返回的info信息（如果存在）
            if 'info' in self.r:
                self.info = json.loads(self.r['info'])
                self.seeds = self.info.get('all_seeds', [])
                print("生成信息：", self.info)
                print("使用的种子：", self.seeds)
            else:
                print("警告：未在返回结果中找到info信息")
                self.seeds = []
                self.info = {}
        except Exception as e:
            print(f"生成图像时出错: {str(e)}")
            self.r = {'images': []}
            self.seeds = []
            self.info = {}

    #保存图片
    def save_img(self, save_dir: str):
        try:
            images = []
            save_paths = []
            
            # 检查保存路径是否有效
            if not save_dir or save_dir.strip() == "":
                print("警告：保存路径为空，将使用默认路径")
                save_dir = "output/images"
            
            # 获取目录部分并创建目录
            directory = os.path.dirname(save_dir)
            if directory == "":  # 如果没有目录部分，使用默认目录
                directory = "output/images"
                save_dir = os.path.join(directory, os.path.basename(save_dir) or "image")
            
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            
            if 'images' not in self.r:
                raise ValueError("No images generated")
                
            # 使用循环处理所有生成的图片
            for i, image_data in enumerate(self.r['images']):
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                #保存图片
                save_path = f"{save_dir}_{i}.png"
                image.save(save_path)
                print(f"已保存图片到 {save_path}")
                images.append(image)
                save_paths.append(save_path)
            
            if not images:
                raise ValueError("No images were saved")
            
            # 默认返回第一张图片的索引
            selected_index = 0
            print(f"默认选择图片 {selected_index}，可在后续步骤中更改")
            return selected_index, save_paths
            
        except Exception as e:
            print(f"保存图片时出错: {str(e)}")
            return 0, []  # 出错时返回默认值和空列表

# FastAPI应用
app = FastAPI(title="StableDiffusion API", description="使用StableDiffusion生成图像的API接口")

@app.post("/generate", response_model=SDGenerateResponse)
async def generate_image(request: SDGenerateRequest):
    try:
        sd = SD_Generate()
        
        # 配置生成参数
        sd.generate_prompt(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            batch_size=request.batch_size,
            seed=request.seed,
            sampler_name=request.sampler_name,
            use_regional_prompter=request.use_regional_prompter,
            regional_prompt_mode=request.regional_prompt_mode,
            regional_prompt_ratios=request.regional_prompt_ratios,
            enable_hr=request.enable_hr,
            model_name=request.model_name
        )
        
        # 获取图像
        sd.get_img()
        
        # 准备响应数据
        response_data = {
            "images": sd.r.get("images", []),
            "seeds": sd.seeds,
            "info": sd.info
        }
        
        # 如果指定了保存目录，则保存图像
        if request.save_dir:
            _, save_paths = sd.save_img(request.save_dir)
            response_data["save_paths"] = save_paths
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":

    uvicorn.run("SD_Image:app", host="0.0.0.0", port=8000, reload=True) 