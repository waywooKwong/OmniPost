"""
调用 stablediffusion 生成图片


"""
import json
import requests
import io
import base64
from PIL import Image
import os
 
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
    ):
        self.payload = {
            # 模型设置
            "override_settings":{
                "sd_model_checkpoint": "wolfboys2D_v10.safetensors [62d679b7a0]",
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
                info = json.loads(self.r['info'])
                self.seeds = info.get('all_seeds', [])
                print("生成信息：", info)
                print("使用的种子：", self.seeds)
            else:
                print("警告：未在返回结果中找到info信息")
                self.seeds = []
        except Exception as e:
            print(f"生成图像时出错: {str(e)}")
            self.r = {'images': []}

    #保存图片
    def save_img(self, save_dir: str):
        try:
            images = []
            # 创建保存目录
            os.makedirs(os.path.dirname(save_dir), exist_ok=True)
            
            if 'images' not in self.r:
                raise ValueError("No images generated")
                
            # 使用循环处理所有生成的图片
            for i, image_data in enumerate(self.r['images']):
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                image.show()
                #保存图片
                save_path = f"{save_dir}_{i}.png"
                image.save(save_path)
                print(f"已保存图片到 {save_path}")
                images.append(image)
            
            if not images:
                raise ValueError("No images were saved")
            
            # 默认返回第一张图片的索引，不再需要用户选择
            selected_index = 0
            print(f"默认选择图片 {selected_index}，可在后续步骤中更改")
            return selected_index
            
        except Exception as e:
            print(f"保存图片时出错: {str(e)}")
            return 0  # 出错时返回默认值

           
if __name__ == "__main__":
    sd=SD_Generate()
    # 使用BREAK分隔的多区域提示词
    prompt="""
        best quality,masterpiece,(2 people, 1 boy:1.2, 1 girl:1.2) Medium Long Shot,busy street sidewalk,boy and girl holding hands,crossing street,crowd,vehicles,warm atmosphere,slow pan or side move,
        BREAK
        1girl,12 years old,asian,black hair,school uniform,
        BREAK
        teenager,black hair,blindfolded,determined,
        
        """
    negative_prompt="NSFW,logo,text,blurry,bad proportions,cropped,watermark,signature,low quality,out of focus,bad anatomy,username,sketches,lowres,normal quality,grayscale,monochrome,worstquality,"
    seed=-1
    
    # # 不使用区域提示器的示例
    # sd.generate_prompt(prompt=prompt,negative_prompt=negative_prompt,seed=seed,batch_size=2)
    # sd.get_img()
    # sd.save_img("test/张三01")
    
    # 使用区域提示器的示例
    sd.generate_prompt(
        prompt=prompt,
        negative_prompt=negative_prompt,
        seed=seed,
        batch_size=4,
        use_regional_prompter=True,
        regional_prompt_mode="Columns",
        regional_prompt_ratios="1,1"
    )
    
    sd.get_img()
    index=sd.save_img("test/张三02")
    seed=sd.seeds[index]

    # 使用高清修复
    sd.generate_prompt(
        prompt=prompt,
        negative_prompt=negative_prompt,
        seed=seed,
        batch_size=1,
        use_regional_prompter=True,
        regional_prompt_mode="Columns",
        regional_prompt_ratios="1,1",
        enable_hr=True,
    )

    sd.get_img()
    seed=sd.save_img("test/张三03")
