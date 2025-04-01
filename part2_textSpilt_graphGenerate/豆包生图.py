# coding:utf-8
from volcengine.visual.VisualService import VisualService
import base64
import requests
import os
from datetime import datetime

def text_to_image(ak, sk, prompt):
    # 初始化视觉服务
    visual_service = VisualService()
    
    # 设置访问凭证
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)

    # 构造请求参数（根据接口文档调整）
    form = {
        "req_key": "high_aes_general_v21_L",  # 固定值
        "prompt": prompt,  # 核心提示词
        "model_version": "general_v2.1_L",  # 模型版本
        "width": 512,  # 图片宽度
        "height": 512,  # 图片高度
        "use_sr": True,  # 开启超分辨率
        "return_url": True,  # 返回图片URL
        "ddim_steps": 25,  # 生成步数
        "seed": -1,  # 随机种子
        "req_schedule_conf": "general_v20_9B_pe",  # 使用美感版
        "logo_info": {  # 水印配置
            "add_logo": True,
            "position": 0,
            "language": 0,
            "opacity": 0.3
        }
    }

    try:
        # 调用同步接口
        response = visual_service.cv_process(form)
        
        if response["code"] == 10000:
            print("生成成功！图片地址：", response["data"]["image_urls"][0])
            return response["data"]["image_urls"][0]
        else:
            print("生成失败，错误信息：", response.get("message", "未知错误"))
            return None
            
    except Exception as e:
        print("API调用异常：", str(e))
        return None

# 使用示例
if __name__ == '__main__':
    # 使用文档注释中的凭据
    AK = ""
    # 直接使用原始的Base64编码字符串作为SK
    SK = ""
    
    # 构造符合要求的prompt（包含文字内容）
    PROMPT = (
        "现代扁平插画风格，数字城市主题，"
        "未来感的蓝色调，背景有流动的数据线条，"
        "画面中央写着\"AI 2.0\"，文字使用霓虹灯效果"
    )
    
    image_url = text_to_image(AK, SK, PROMPT)
    if image_url:
        # 下载并保存图片
        try:
            print("开始下载图片...")
            # 创建保存图片的文件夹
            save_dir = "generated_images"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"创建文件夹: {save_dir}")
            else:
                print(f"文件夹已存在: {save_dir}")
            
            # 生成文件名（使用时间戳确保唯一性）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_dir}/ai_image_{timestamp}.jpg"
            print(f"将保存为: {filename}")
            
            # 下载图片
            print(f"正在请求URL: {image_url}")
            response = requests.get(image_url, stream=True)
            print(f"请求状态码: {response.status_code}")
            response.raise_for_status()  # 确保请求成功
            
            # 保存图片到本地
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    
            print(f"图片已保存到: {filename}")
            
        except Exception as e:
            print(f"保存图片失败: {str(e)}")
            import traceback
            traceback.print_exc()