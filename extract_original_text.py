import json

# 读取JSON文件
with open('part2_textSpilt_graphGenerate/斗破苍穹节选/role_message/novel_scenes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有的original_text
original_texts = [scene["original_text"] for scene in data["scenes"]]

# 将所有文本以换行符连接
combined_text = "\n".join(original_texts)

# 将结果写入文件
with open('combined_text.txt', 'w', encoding='utf-8') as f:
    f.write(combined_text)

print("文本已合并并保存到combined_text.txt文件中") 