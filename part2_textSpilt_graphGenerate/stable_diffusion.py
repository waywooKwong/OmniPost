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
           sampler_name="Euler a"
    ):
        self.payload = {
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
            "CLIP_stop_at_last_layers": 2,
        
            # 面部修复 face fix
            "restore_faces": False,
        }
    
    def get_img(self):
        # 对本地连接不使用代理
        local_session = requests.Session()
        local_session.trust_env = False  # 不使用环境变量中的代理设置
        
        response = local_session.post(url=f'{self.url}/sdapi/v1/txt2img', json=self.payload)
        self.r = response.json()
        
        # 解析返回的info信息
        info = json.loads(self.r['info'])
        self.seeds=info['all_seeds']
        print("生成信息：", info)
        print("使用的种子：", self.seeds)
        
        
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
            
            seed_index = int(input("请你选择角色形象（输入0/1/2/3/4）："))
            if seed_index not in range(len(images)):
                print(f"输入的选择 {seed_index} 无效，默认使用第一张图片")
                seed_index = 0  
            
            return seed_index
            
        except Exception as e:
            print(f"保存图片时出错: {str(e)}")
            return 0  # 出错时返回默认值

           
if __name__ == "__main__":
    sd=SD_Generate()
    prompt="best quality,masterpiece,absurdres,4K,hyper detailed,super detailed(1girl:2),female,(12 years old:1.1),young girl,asian,round face,slightly flushed cheeks,(sweat beads on cheeks:1.1),(big black eyes:1.2),innocent eyes,black hair,shoulder-length,concerned expression,kind look,fair skin,petite build,(school uniform:1.2),(close-up portrait:1.1),front view,(soft warm tone:1.2),anime style,moe style.(portrait:1.1),centered,front view,(bright daylight tone:1.2),anime style,clean lines.shotbest quality,masterpiece,absurdres,4K,hyper detailed,super detailed,best quality,masterpiece,absurdres,4K,hyper detailed,super detailed,"
    negative_prompt="NSFW,logo,text,blurry,bad proportions,cropped,watermark,signature,low quality,out of focus,bad anatomy,username,sketches,lowres,normal quality,grayscale,monochrome,worstquality,"
    seed=3324159030
    sd.generate_prompt(prompt=prompt,negative_prompt=negative_prompt,seed=seed,batch_size=2)
    sd.get_img()
    sd.save_img("test/张三")