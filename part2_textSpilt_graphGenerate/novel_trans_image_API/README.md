# 小说转画像系统 - 模型管理指南

本文档介绍如何在小说转画像系统中管理大语言模型，包括添加新的模型和厂家。系统采用了灵活的配置架构，使得添加新模型变得简单高效。

## 配置文件结构

系统使用 `config.yaml` 文件来管理模型配置。配置文件结构如下：

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

## 配置说明

- **api_keys**: 存储各个厂家的API密钥
- **backup_model**: 备用模型，当默认模型不可用时使用
- **default_model**: 默认使用的模型
- **proxy**: 代理服务器设置
  - **http**: HTTP代理服务器地址
  - **https**: HTTPS代理服务器地址
- **provider_templates**: 厂家模板配置，定义每个厂家的通用参数
  - **api_param**: API参数名称
  - **env_var**: 环境变量名称
  - **temperature**: 默认温度参数
- **providers**: 每个厂家支持的模型列表

## 添加新模型或厂家

### 方法一：使用API接口

1. **添加新厂家**:

```bash
curl -X POST "http://localhost:8001/add_provider_template?provider_name=openai&api_param=openai_api_key&env_var=OPENAI_API_KEY&temperature=0.7"
```

2. **添加新模型**:

```bash
curl -X POST "http://localhost:8001/set_default_model" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model_name": "gpt-4",
    "api_key": "your_openai_api_key"
  }'
```

3. **设置代理服务器**:

```bash
curl -X POST "http://localhost:8001/set_proxy?http_proxy=http://127.0.0.1:7890&https_proxy=http://127.0.0.1:7890"
```

### 方法二：直接修改配置文件

1. **添加新厂家**:

在 `provider_templates` 部分添加新的厂家配置：

```yaml
provider_templates:
  # 现有厂家...
  openai:
    api_param: openai_api_key
    env_var: OPENAI_API_KEY
    temperature: 0.7
```

2. **添加新模型**:

在 `providers` 部分更新厂家的模型列表：

```yaml
providers:
  # 现有厂家...
  openai:
    models:
    - gpt-4
```

3. **设置代理服务器**:

```yaml
proxy:
  http: http://127.0.0.1:7890
  https: http://127.0.0.1:7890
```

4. **设置为默认或备用模型**（可选）:

```yaml
default_model: gpt-4
# 或
backup_model: gpt-4
```

## 使用示例

### 1. 添加新的厂家（例如：Anthropic）

```yaml
# 在provider_templates中添加
provider_templates:
  anthropic:
    api_param: anthropic_api_key
    env_var: ANTHROPIC_API_KEY
    temperature: 0.7

# 在api_keys中添加密钥
api_keys:
  anthropic: "your_anthropic_api_key"

# 在providers中添加
providers:
  anthropic:
    models: []  # 暂时为空，后续添加模型
```

### 2. 为新厂家添加模型（例如：Claude）

```yaml
# 在providers的模型列表中添加
providers:
  anthropic:
    models:
    - claude-3-opus

# 设置为默认模型（可选）
default_model: claude-3-opus
```

### 3. 添加DeepSeek模型

```yaml
# 在api_keys中添加密钥
api_keys:
  deepseek: "your_deepseek_api_key"

# 在provider_templates中添加（如果尚未添加）
provider_templates:
  deepseek:
    api_param: deepseek_api_key
    env_var: DEEPSEEK_API_KEY
    temperature: 0.7

# 在providers中添加模型
providers:
  deepseek:
    models:
    - deepseek-chat
    - deepseek-coder

# 设置为默认模型（可选）
default_model: deepseek-chat
```

## 模型加载流程

1. 系统从 `config.yaml` 加载配置
2. 根据模型名称在 `providers` 的各个厂家的模型列表中查找
3. 确定模型所属的厂家
4. 根据厂家创建对应的模型实例

## 支持的模型类型

系统目前支持以下类型的模型：

1. **Google Gemini** (provider: google)
   - gemini-2.0-flash
   - gemini-2.5-flash-preview-04-17
   - gemini-2.5-pro-exp-03-25

2. **智谱 GLM** (provider: zhipu)
   - glm-4-flash

3. **DeepSeek** (provider: deepseek)
   - deepseek-chat

## 注意事项

1. 添加新厂家时，确保相关的Python包已安装
2. 添加新模型时，确保已在相应的厂家账户中开通该模型的访问权限
3. API密钥应妥善保管，不要将其提交到版本控制系统中
4. 修改配置文件后，需要重启服务才能生效
5. 如果API访问受到地区限制，请确保设置了正确的代理服务器
