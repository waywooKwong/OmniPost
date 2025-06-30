# 小说转画像系统 API 文档

## 目录

- [概述](#概述)
- [API 接口](#api接口)
  - [1. 模型管理 API](#1-模型管理api)
    - [1.1 设置默认模型](#11-设置默认模型)
    - [1.2 设置备用模型](#12-设置备用模型)
    - [1.3 获取模型配置](#13-获取模型配置)
    - [1.4 添加提供商模板](#14-添加提供商模板)
    - [1.5 设置代理服务器](#15-设置代理服务器)
  - [2. 角色提取 API](#2-角色提取api)
    - [2.1 从文件提取角色](#21-从文件提取角色)
    - [2.2 从文本提取角色](#22-从文本提取角色)
  - [3. 场景分镜 API](#3-场景分镜api)
    - [3.1 生成场景分镜](#31-生成场景分镜)
  - [4. 场景提示词生成 API](#4-场景提示词生成api)
    - [4.1 生成场景提示词](#41-生成场景提示词)
  - [5. 图像生成 API](#5-图像生成api)
    - [5.1 生成图像](#51-生成图像)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [使用示例](#使用示例)
- [配置文件结构](#配置文件结构)

## 概述

小说转画像系统 API 是一套用于将小说文本转换为图像的 API 集合。系统包括模型管理、角色提取、场景分镜、提示词生成以及最终的图像生成等功能。所有 API 接口均使用 HTTP 协议，并采用 JSON 格式进行数据交换。

- **基础 URL**: `http://localhost:8000`
- **API 文档**: `http://localhost:8000/docs`

## API 接口

### 1. 模型管理 API

#### 1.1 设置默认模型

**路径**: `/set_default_model`

**方法**: `POST`

**描述**: 设置系统使用的默认大语言模型

**请求体**:

```json
{
  "provider": "google",
  "model_name": "gemini-pro",
  "api_key": "your_api_key_here"
}
```

**参数说明**:

- `provider` (string, 必需): 模型供应商，如 "google", "zhipu", "deepseek" 等
- `model_name` (string, 必需): 模型名称
- `api_key` (string, 必需): API 密钥

**响应**:

```json
{
  "success": true,
  "message": "默认模型已更新为 gemini-pro",
  "test_result": {
    "success": true,
    "message": "模型测试成功",
    "response": "你好，很高兴见到你！"
  }
}
```

**状态码**:

- `200`: 成功
- `500`: 服务器错误

#### 1.2 设置备用模型

**路径**: `/set_backup_model`

**方法**: `POST`

**描述**: 设置系统使用的备用大语言模型（当默认模型不可用时使用）

**请求体**:

```json
{
  "provider": "zhipu",
  "model_name": "glm-4",
  "api_key": "your_api_key_here"
}
```

**参数说明**:

- `provider` (string, 必需): 模型供应商，如 "google", "zhipu", "deepseek" 等
- `model_name` (string, 必需): 模型名称
- `api_key` (string, 必需): API 密钥

**响应**:

```json
{
  "success": true,
  "message": "备用模型已更新为 glm-4",
  "test_result": {
    "success": true,
    "message": "模型测试成功",
    "response": "你好，有什么可以帮助你的？"
  }
}
```

**状态码**:

- `200`: 成功
- `500`: 服务器错误

#### 1.3 获取模型配置

**路径**: `/get_model_config`

**方法**: `GET`

**描述**: 获取当前系统的模型配置信息

**响应**:

```json
{
  "default_model": "gemini-2.5-flash-preview-04-17",
  "backup_model": "glm-4-flash",
  "provider_templates": {
    "google": {
      "api_param": "google_api_key",
      "env_var": "GOOGLE_API_KEY",
      "temperature": 0.7
    },
    "zhipu": {
      "api_param": "api_key",
      "env_var": "ZHIPUAI_API_KEY",
      "temperature": 0.7
    },
    "deepseek": {
      "api_param": "deepseek_api_key",
      "env_var": "DEEPSEEK_API_KEY",
      "temperature": 0.7
    }
  },
  "providers": {
    "google": {
      "models": [
        "gemini-2.0-flash",
        "gemini-2.5-flash-preview-04-17",
        "gemini-2.5-pro-exp-03-25"
      ]
    },
    "zhipu": {
      "models": ["glm-4-flash"]
    },
    "deepseek": {
      "models": ["deepseek-chat"]
    }
  }
}
```

**状态码**:

- `200`: 成功
- `500`: 服务器错误

#### 1.4 添加提供商模板

**路径**: `/add_provider_template`

**方法**: `POST`

**描述**: 添加或更新一个提供商的模板配置

**请求参数**:

- `provider_name` (string, 必需): 提供商名称，如 "openai"
- `api_param` (string, 必需): API 参数名称，如 "openai_api_key"
- `env_var` (string, 必需): 环境变量名称，如 "OPENAI_API_KEY"
- `temperature` (float, 可选): 温度参数，默认为 0.7

**响应**:

```json
{
  "success": true,
  "message": "提供商模板 openai 已添加/更新"
}
```

**状态码**:

- `200`: 成功
- `500`: 服务器错误

#### 1.5 设置代理服务器

**路径**: `/set_proxy`

**方法**: `POST`

**描述**: 设置系统使用的 HTTP/HTTPS 代理服务器

**请求参数**:

- `http_proxy` (string, 必需): HTTP 代理服务器地址，如 "http://127.0.0.1:7890"
- `https_proxy` (string, 可选): HTTPS 代理服务器地址，如不提供则使用 HTTP 代理地址

**响应**:

```json
{
  "success": true,
  "message": "代理设置已更新"
}
```

**状态码**:

- `200`: 成功
- `500`: 服务器错误

### 2. 角色提取 API

#### 2.1 从文件提取角色

**路径**: `/role-extract`

**方法**: `POST`

**描述**: 从上传的小说文件中提取角色并生成角色画像提示词

**请求格式**: `multipart/form-data`

**请求参数**:

- `file` (file, 必需): 上传的小说文本文件
- `use_backup_model` (boolean, 可选): 是否使用备用模型，默认为 false
- `project_id` (string, 必需): 工程编号，用于创建对应的工程文件夹

**响应**:

```json
{
  "success": true,
  "message": "成功从 novel.txt 中提取了 5 个角色",
  "data": {
    "001": {
      "name": "小明",
      "prompt": "a boy, young, student, short black hair"
    },
    "002": {
      "name": "小红",
      "prompt": "a girl, teenage, student, long brown hair (curly:1.2)"
    }
  },
  "project_id": "project123"
}
```

**状态码**:

- `200`: 成功
- `500`: 角色提取失败

#### 2.2 从文本提取角色

**路径**: `/role-extract-text`

**方法**: `POST`

**描述**: 从提供的小说文本内容中提取角色并生成角色画像提示词

**请求体**:

```json
{
  "content": "这是小说文本内容...",
  "use_backup_model": false,
  "project_id": "project123"
}
```

**参数说明**:

- `content` (string, 必需): 小说文本内容
- `use_backup_model` (boolean, 可选): 是否使用备用模型，默认为 false
- `project_id` (string, 必需): 工程编号，用于创建对应的工程文件夹

**响应**:

```json
{
  "success": true,
  "message": "成功从文本内容中提取了 5 个角色",
  "data": {
    "001": {
      "name": "小明",
      "prompt": "a boy, young, student, short black hair"
    },
    "002": {
      "name": "小红",
      "prompt": "a girl, teenage, student, long brown hair (curly:1.2)"
    }
  },
  "project_id": "project123"
}
```

**状态码**:

- `200`: 成功
- `500`: 角色提取失败

### 3. 场景分镜 API

#### 3.1 生成场景分镜

**路径**: `/generate-scenes`

**方法**: `POST`

**描述**: 根据项目 ID 和角色信息，生成小说场景分镜描述

**请求体**:

```json
{
  "project_id": "project123",
  "role_info": {
    "001": {
      "name": "小明",
      "prompt": "a boy, young, student, short black hair"
    },
    "002": {
      "name": "小红",
      "prompt": "a girl, teenage, student, long brown hair (curly:1.2)"
    }
  }
}
```

**参数说明**:

- `project_id` (string, 必需): 项目 ID
- `role_info` (object, 必需): 角色信息对象，包含角色 ID、名称和提示词

**响应**:

```json
{
  "status": "success",
  "message": "成功生成 10 个场景",
  "scenes_count": 10,
  "data": {
    "metadata": {
      "source": "novel.txt",
      "processed_at": "2023-07-15 14:30:25",
      "total_scenes": 10
    },
    "scenes": [
      {
        "description": "教室内，阳光透过窗户照射进来。小明坐在窗边的座位上，专注地看着黑板。小红从教室门口走进来，手里拿着一本书。",
        "original_text": "小明坐在窗边，阳光透过玻璃窗照在他的课本上。这时，小红推开门走了进来。",
        "roles": [
          {
            "小明": "sitting by window, focused"
          },
          {
            "小红": "walking, holding book"
          }
        ]
      }
    ]
  }
}
```

**状态码**:

- `200`: 成功
- `500`: 场景生成失败

### 4. 场景提示词生成 API

#### 4.1 生成场景提示词

**路径**: `/generate-scene-prompt`

**方法**: `POST`

**描述**: 将小说场景转换为 Stable Diffusion 提示词

**请求体**:

```json
{
  "project_id": "project123",
  "description": "教室内，阳光透过窗户照射进来。小明坐在窗边的座位上，专注地看着黑板。小红从教室门口走进来，手里拿着一本书。",
  "original_text": "小明坐在窗边，阳光透过玻璃窗照在他的课本上。这时，小红推开门走了进来。",
  "use_backup_model": false
}
```

**参数说明**:

- `project_id` (string, 必需): 项目 ID
- `description` (string, 必需): 场景描述
- `original_text` (string, 必需): 原始文本
- `use_backup_model` (boolean, 可选): 是否使用备用模型，默认为 false

**响应**:

```json
{
  "prompt": "(2 people:1.3, a boy and a girl), classroom, sunlight through window, desk, blackboard, book, school uniform, bright lighting",
  "status": "success",
  "message": "提示词生成成功"
}
```

**状态码**:

- `200`: 成功
- `500`: 提示词生成失败

### 5. 图像生成 API

#### 5.1 生成图像

**路径**: `/sd-generate`

**方法**: `POST`

**描述**: 使用 Stable Diffusion 生成图像

**请求体**:

```json
{
  "prompt": "(2 people:1.3, a boy and a girl), classroom, sunlight through window, desk, blackboard, book, school uniform, bright lighting",
  "negative_prompt": "ugly, deformed, blurry, low quality, nsfw",
  "batch_size": 1,
  "seed": -1,
  "sampler_name": "Euler a",
  "use_regional_prompter": false,
  "enable_hr": true,
  "model_name": "wolfboys2D_v10.safetensors [62d679b7a0]",
  "save_dir": "output/project123/scene1"
}
```

**参数说明**:

- `prompt` (string, 必需): 正向提示词
- `negative_prompt` (string, 可选): 反向提示词，默认为空字符串
- `batch_size` (integer, 可选): 批量生成数量，范围 1-4，默认为 1
- `seed` (integer, 可选): 随机种子，-1 表示随机，默认为-1
- `sampler_name` (string, 可选): 采样器名称，默认为"Euler a"
- `use_regional_prompter` (boolean, 可选): 是否使用区域提示器，默认为 false
- `regional_prompt_mode` (string, 可选): 区域提示模式，默认为"Columns"
- `regional_prompt_ratios` (string, 可选): 区域提示比例，默认为"1,1"
- `enable_hr` (boolean, 可选): 是否启用高清修复，默认为 false
- `model_name` (string, 可选): 使用的模型名称，默认为"wolfboys2D_v10.safetensors [62d679b7a0]"
- `save_dir` (string, 可选): 保存目录，默认为 null

**响应**:

```json
{
  "images": ["base64编码的图像数据..."],
  "seeds": [42],
  "info": {
    "prompt": "(2 people:1.3, a boy and a girl), classroom, sunlight through window, desk, blackboard, book, school uniform, bright lighting",
    "negative_prompt": "ugly, deformed, blurry, low quality, nsfw",
    "all_seeds": [42],
    "all_prompts": ["..."]
  },
  "save_paths": ["output/project123/scene1_0.png"]
}
```

**状态码**:

- `200`: 成功
- `500`: 图像生成失败

## 数据模型

### ModelChangeRequest

```json
{
  "provider": "string",
  "model_name": "string",
  "api_key": "string"
}
```

### TextContentRequest

```json
{
  "content": "string",
  "use_backup_model": false,
  "project_id": "string"
}
```

### SceneGenerateRequest

```json
{
  "project_id": "string",
  "role_info": {
    "propertyName": {
      "name": "string",
      "prompt": "string"
    }
  }
}
```

### SceneRequest

```json
{
  "project_id": "string",
  "description": "string",
  "original_text": "string",
  "use_backup_model": false
}
```

### SDGenerateRequest

```json
{
  "prompt": "string",
  "negative_prompt": "string",
  "batch_size": 1,
  "seed": -1,
  "sampler_name": "Euler a",
  "use_regional_prompter": false,
  "regional_prompt_mode": "Columns",
  "regional_prompt_ratios": "1,1",
  "enable_hr": false,
  "model_name": "wolfboys2D_v10.safetensors [62d679b7a0]",
  "save_dir": "string"
}
```

## 错误处理

所有 API 在遇到错误时都会返回适当的 HTTP 状态码，以及包含错误详情的 JSON 响应：

```json
{
  "detail": "错误信息"
}
```

常见错误码：

- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 配置文件结构

系统使用 YAML 格式的配置文件来管理模型和提供商。配置文件结构如下：

```yaml
api_keys:
  google: "your_google_api_key"
  zhipu: "your_zhipu_api_key"
  deepseek: "your_deepseek_api_key"

backup_model: glm-4-flash
default_model: gemini-2.5-flash-preview-04-17

# 代理设置
proxy:
  http: http://127.0.0.1:7890
  https: http://127.0.0.1:7890

# 厂家模板配置，定义每个厂家的通用参数
provider_templates:
  google:
    api_param: google_api_key
    env_var: GOOGLE_API_KEY
    temperature: 0.7
  zhipu:
    api_param: api_key
    env_var: ZHIPUAI_API_KEY
    temperature: 0.7
  deepseek:
    api_param: deepseek_api_key
    env_var: DEEPSEEK_API_KEY
    temperature: 0.7

# 每个厂家支持的模型列表
providers:
  google:
    models:
      - gemini-2.0-flash
      - gemini-2.5-flash-preview-04-17
  zhipu:
    models:
      - glm-4-flash
  deepseek:
    models:
      - deepseek-chat
```

### 添加新模型或厂家的步骤

1. **添加新厂家**：

   - 使用 `/add_provider_template` API 添加新的提供商模板
   - 或直接在配置文件的 `provider_templates` 部分添加新的提供商配置

2. **添加新模型**：

   - 使用 `/set_default_model` 或 `/set_backup_model` API 添加新模型，系统会自动将模型添加到对应提供商的模型列表中
   - 或直接在配置文件的 `providers.[provider_name].models` 列表中添加该模型

3. **使用新模型**：

   - 设置 `default_model` 或 `backup_model` 为新添加的模型名称

4. **设置代理**：
   - 使用 `/set_proxy` API 设置代理服务器
   - 或直接在配置文件的 `proxy` 部分修改代理设置
