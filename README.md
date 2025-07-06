# OmniPost

OmniPost 是一款跨平台流媒体内容智能迁移工作站，极大提升内容创作者与团队的流媒体平台运营效率。

<!-- 使用 HTML 标签插入图片并控制大小 -->
<!-- 方法1：使用 width 和 height 属性 -->
<!-- <img src="src/readme/logo.png" width="300" height="200" alt="OmniPost 界面截图"> -->
<!-- 方法4：响应式图片，在不同屏幕尺寸下自适应 -->
<img src="src/readme/logo.jpg" style="max-width: 10%; height: auto; display: block; margin: 0 auto;" alt="OmniPost 响应式展示">

从一个创作思路出发，自动化内容图文增强，面向平台进行风格适配与发布。将原始创作思路（如视频、短文、配图等）进行
- 基于平台风格的高定制度适配和优化、
- 细粒度图文补充生成与内容格式匹配、
- LLM自动化桌面控制并行发布至不同平台

<img src="src/readme/structure.png" style="max-width: 60%; display: block; margin: 0 auto;">

据我们所知，OmniPost 是首个面向跨平台流媒体内容智能迁移这一场景的端到端解决方案。


## Poster

<img src="src/readme/post.png" style="max-width: 60%; display: block; margin: 0 auto;">

## Requirements

- python 3.11(less than 3.10 may not support MCP from Anthropic)
- crewai(latest)
- langchain(latest)
- stable diffusion
- browser use(latest)

<img src="src/readme/tech_workflow.png" style="max-width: 60%; display: block; margin: 0 auto;">

## How to run

```structure
OmniPost
├─aigc-AdGraph-front // Andriod APP UI
├─part1_graph_generate // 多智能体交互生成内容
├─part2_textSpilt_graphGenrate // 细粒度文生图
├─part3_browser_use // LLM自动化桌面控制
└─other...
```
详细参考各模块内部的readme.md文件

## Copyright
邝伟华*(weihua.kwong@mail.nankai.edu.cn)、王璞、沈超、李群、钱程