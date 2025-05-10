import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.kuangweihua.com/")
    page.get_by_role(
        "link",
        name="我的科研需补足的能力 在每周保持进度的过程中，总结、汇报是比较重要的事情。尤其是当要自己主导项目的推进、论文框架规划与展示，有成熟的技术栈对于进一步深造硕士/博",
    ).click()
    expect(page.get_by_label("Main Content")).to_match_aria_snapshot(
        '- main "Main Content":\n  - article:\n    - heading "我的科研需补足的能力" [level=1]\n    - text: Posted\n    - time: /Apr \\d+, \\d+/\n    - text: By\n    - emphasis:\n      - link "Weihua Kwong"\n    - emphasis: 1 min\n    - text: read\n    - paragraph: 在每周保持进度的过程中，总结、汇报是比较重要的事情。尤其是当要自己主导项目的推进、论文框架规划与展示，有成熟的技术栈对于进一步深造硕士/博士有重要的影响。\n    - paragraph: 在这里记录目前我作为新手的技术栈，并在之后观察学长、老师等更资深研究者的习惯来优化我的技术栈。\n    - list:\n      - listitem:\n        - text: 展示PPT：LaTex Beamer(简约，而且不用花过多精力在排版上)\n        - list:\n          - listitem: PowerPoint 的功底其实也需要增强\n      - listitem: 绘图：draw.io，PowerPoint(画幅太小，还是不太适应，但重在风格比较美观，学长的工作在用)\n      - listitem: 素材：draw.io 图标、iconfont 图标库\n      - listitem: 笔记：obisidian（替换Typora）、飞书（学校有免费企业版，在学校里很方便）、notion（才尝试，可能后面会转向它）\n      - listitem: 编码：vscode, cursor（比trae更接近原生vscode）\n    - text: \n    - link "Personal insights"\n    - text: \n    - link "research"\n    - text: This post is licensed under\n    - link "CC BY 4.0"\n    - text: "by the author. Share:"\n    - link "Twitter"\n    - link "Facebook"\n    - link "Telegram"\n    - button "Copy link"'
    )
    page.get_by_role("listitem").filter(has_text="MCP Server by Python, config").click()
    page.get_by_role("link", name="Brief survey on Multi-Agents").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
