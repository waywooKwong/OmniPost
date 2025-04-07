"""""
stable diffusion prompt 统一模版


"""

# 通用提示词模板
GENERAL_PROMPTS = {
    "positive_prompt":"best quality、masterpiece、absurdres、4K、hyper detailed、super detailed",
    "negitive_prompt":"worst quality、low qualitiylogo、watermark、text、signature、username、out of focus、blurry、skin spots acnes、skin blemishes、age spot、ugly、ugly face、bad anatomy、bad hands、bad arms、bad legs、bad face、bad fingers、too many arms、extra legs、extra digits、extra fingers、missing limb、missing fingers、missing legs、missing arms、fewer digits",
}

# 人物相关提示词
HUMAN_PROMPTS = {
    # 人数
    "count": {
        "single": ["1 girl", "1 woman", "1 boy", "1 man", "1 little girl", "1 female child", "1 little boy", "1 male child"],
        "multiple": ["Couple", "multiple girls", "group picture"],
        "none": ["no humans"]
    },
    
    # 年龄
    "age": {
        "specific": ["20 years old", "20yo"],
        "young": ["little boy", "tiny girl", "young girl"],
        "adult": ["mature woman"],
        "old": ["old man"],
        "other": ["motherly"]
    },
    
    # 体型
    "body_type": {
        "height": ["tall", "big", "gigantic", "short", "tiny"],
        "weight": ["fat", "plump", "skinny", "emaciated", "thin"],
        "muscle": ["muscle", "muscular female", "muscular male", "toned", "fit-muscled body"],
        "feature": ["narrow waist"]
    },
    
    # 手脚
    "limbs": {
        "arms": ["arms", "skinny arms", "thin arms", "fat arms", "long arms", "short arms"],
        "legs": ["legs"],
        "feet": ["soles"]
    },
    
    # 皮肤
    "skin": {
        "texture": ["shiny skin", "oiled skin", "glistening skin", "high gloss skin", "porcelain skin", 
                  "wet skin", "sweaty skin", "Wrinkles skin"],
        "color": ["green skin"],
        "tan": ["suntan", "tanline", "wheat skin"]
    },
    
    # 人种
    "ethnicity": {
        "real": ["chinese", "japanese", "american", "europian", "white skin", "african", "dark skin"],
        "fantasy": ["elf", "dark elf", "hobbit", "dwarf", "goblin", "orc", "fairy", "monster", 
                   "angel", "demon", "vampire", "zombie"]
    },
    
    # 姿势
    "pose": {
        "basic": ["standing", "sitting", "squatting", "crouching", "lying", "lying on back", "lying on stomach", 
                 "all fours", "on all fours"],
        "hands": ["hand in pocket", "hands in pocket", "open arms", "spread arms"],
        "arms": ["arms at sides", "arms up", "raise hand", "raise one hand", "raise two hands", 
                "surrender", "arms down", "wave hand", "fist pump", "hug"],
        "legs": ["standing on one leg", "kicking", "punching", "high-kick", "high-kick pose"]
    },
    
    # 头发
    "hair": {
        "length": ["medium hair", "long hair", "very long hair", "absurdly long hair", 
                  "short hair", "very short hair", "bald", "beautiful hair"],
        "style": ["parted bangs", "bob cut", "straight hair", "pigtails", "long pigtails", "short pigtails", 
                 "twintails", "low twintails", "drill hair", "pixie cut hairstyle", "flipped hair", 
                 "curly hair", "braid", "single braid", "twin braid", "ponytail", "short ponytail", 
                 "long ponytail", "side ponytail", "forehead", "open forehead", "wavy hair", 
                 "messy hair", "loose hair", "baby hair", "blunt bangs", "straight bangs", "diagonal bangs", 
                 "hair over one eye", "spiked hair"],
        "color": ["black hair", "blonde hair", "colored inner hair", "streaked hair", "shiny hair", 
                 "two-tone hair", "multicolored hair"]
    },
    
    # 脸部
    "face": {
        "type": ["cute", "babyface", "kawaii", "beautiful face", "perfect face", 
               "highly detailed beautiful face and eyes", "attractive face", "smaller face"],
        "features": ["freckles", "mole", "puffy face", "detailed face", "delicate facial features", 
                   "detailed skin", "shiny skin", "wrinkles face"]
    },
    
    # 眼睛
    "eyes": {
        "color": ["green eyes"],
        "size": ["big eyes", "small eyes"],
        "state": ["close eyes", "open eyes", "one eye closed", "wink"],
        "features": ["eyelashes", "eyeliner", "drooping eyes", "slant eyes"]
    },
    
    # 耳朵
    "ears": ["plump ears", "elf ears", "pointy ears"],
    
    # 嘴
    "mouth": {
        "state": ["open mouth", "close mouth", "half-open mouth", "parted_lips"],
        "action": ["tongue", "stick out tongue", "licking", "biting", "raise the corner of the mouth", 
                 "drooling", "saliva"]
    },
    
    # 鼻子
    "nose": ["button nose", "bulbous nose", "aquiline nose", "hooked nose"],
    
    # 表情
    "expression": {
        "happy": ["smile", "laughing", "fearless smile", "adorable smiling"],
        "sad": ["cry", "sad"],
        "angry": ["angry", "wrath", "mad", "furious", "annoyed"],
        "other": ["absence of mind", "dazed state", "stargazing", "shy", "embarrassed", "blush"]
    }
}

# 服装相关提示词
CLOTHING_PROMPTS = {
    # 纹饰
    "pattern": ["Stripe", "plaid", "Plaid", "Polka dot", "tiger-striped", "floral print", 
              "Animal print", "Camouflage", "Herringbone", "Grid", "Leopard print", "Zebra print", 
              "Dot pattern", "Gingham check", "Metallic print", "Yin Yang diagrams"],
    
    # 上衣
    "top": ["clothes", "crop top", "midriff", "off-shoulder", "bare shoulder", "Casual clothes", 
          "casual wear", "shirt", "t-shirt", "collared shirt", "short hem", "short sleeves", 
          "Half-sleeve top", "no-sleeves", "ripping shirt", "Polo shirt", "tank top", "turtleneck", 
          "vest", "blazer", "coat", "white coat", "raincoat", "hoodle", "hood", "jacket", 
          "hooded jacket", "plaid jacket", "blouse", "jumper", "sweater", "cardigan", "Tunic", 
          "Shell top", "Bolero", "cropped jacket", "tracksuit", "jersey", "Pullover", "camisole"],
    
    # 下衣
    "bottom": ["skirt", "pleated skirt", "pants", "jeans", "bottoms", "denim jeans", "plaid pants", 
             "shorts", "short pants", "suspenders", "braces", "leggings", "bike shorts", 
             "compression shorts", "tight shorts", "buruma", "bloomers", "racing bloomers", 
             "sports bikini", "loincloth", "pelvic curtain"],
    
    # 职业服装
    "uniform": ["school uniform", "sailor fuku", "serafuku", "sailor uniform", "sailor suit", 
              "sailor collar", "track uniform", "track and field uniform", "sports bikini", 
              "sport bra", "sport uniform", "gym uniform", "PE uniform", "sportswear", "dress", 
              "beautiful detailed dress with many frills", "suit", "pajamas", "overalls", 
              "japanese clothes", "kimono", "pinafore", "maid", "gothic lolita", "monastery uniform", 
              "leotard", "rhythmic gymnastics costumes", "suimsuit", "one-piece swimsuit", 
              "competition swimsuit", "school swimsuit", "blue one-piece swimsuit", "High-cut swimwear", 
              "Swimwear cut high in the leg", "volleyball uniform", "beachvolleyball uniform", 
              "cheerleader", "tutu", "armor", "miko", "idol girl", "nurse", "china dress", 
              "waitress", "bunny girl", "bodysuit", "race queen", "gyaru", "pinafore", 
              "tennis uniform", "rash guard", "catsuit"],
    
    # 头饰
    "head_accessory": ["hair ornament", "head band", "hair band", "white brim", "ribbon", "hair ribbon", 
                    "hat", "helmet", "beret", "flat cap", "hunting cap", "beanie", "knit cap", 
                    "casquette", "bun cover", "crown", "animal ears", "cat ears", "fox ears", 
                    "mouth mask", "visor cap", "necklace", "scarf", "earrings", "choker", 
                    "piercing", "tie", "bow tie", "bow"],
    
    # 眼睛配饰
    "eye_accessory": ["glasses", "sunglasses", "eyepatch", "blindfold"],
    
    # 手部配饰
    "hand_accessory": ["gloves", "fingerless gloves", "knitted gloves", "mitten", "leather gloves", 
                     "latex gloves", "surgical gloves", "long gloves", "opera gloves", 
                     "detached sleeves", "elbow pads", "arm ring", "bracelet", "wristband", 
                     "watch", "wrist watch", "handcuffs", "cat hands gloves"],
    
    # 物品
    "items": ["sword", "katana", "japanese sword", "fencing sword", "dual wielding", "wand", "rod", 
            "umbrella", "bag", "suitcase", "rod", "stick", "pole rod", "bow", "longbow", 
            "archery bow", "hammer", "warhammer", "scythe", "sickle", "whip"],
    
    # 足部
    "foot_wear": ["shoes", "footwear", "sneakers", "sandals", "flip flops", "socks", "stockings", 
                "thigh-highs", "knee pads", "tights"],
    
    # 身体配饰
    "body_accessory": ["waistcloth", "sarong", "belt", "sash", "apron", "school bag", "backpack", 
                     "knapsack", "backbag", "cloak", "shawl"]
}

# 场景设定提示词
SCENE_PROMPTS = {
    # 构图/光源
    "composition": {
        "front": ["front view", "from front"],
        "back": ["back view", "from back", "from behind"],
        "side": ["side view", "from side"],
        "top": ["top view", "from top", "from above", "overhead shot", "bird's-eye view"],
        "bottom": ["low angle", "bottom view", "from below", "under view", "very low camera angle"],
        "tilt": ["dutch angle"],
        "special": ["satellite photo", "fisheye lens", "dynamic angle", "foreground", "facing straight at viewer"],
        "close": ["close-up", "extreme close-up", "macro lens", "upper body", "upper body", "full body"],
        "wide": ["wide shot", "very wide shot"],
        "angle": ["portrait", "profile", "cowboy shot"],
        "focus": ["focus"]
    },
    
    # 光源
    "lighting": ["professional lighting", "spotlight", "stage lights", "underlighting", "sidelighting", 
               "backlighting", "rim light", "best light", "dynamic lighting", "amazing shading", 
               "diffraction spikes", "lens flare"],
    
    # 色调
    "tone": ["warm tone", "cool tone", "natural tone", "bright tone", "dark tone", 
            "soft tone", "harsh tone", "muted tone", "vibrant tone", "pastel tone",
            "monochromatic", "sepia tone", "vintage tone", "film tone", "dramatic tone"],
    
    # 天气
    "weather": {
        "sunny": ["sunny", "sun", "shiny sun lighting"],
        "rainy": ["rainny", "rain"],
        "cloudy": ["cloudy", "cloud"],
        "sky": ["gray sky"],
        "fog": ["mist"],
        "other": ["falling petals"]
    },
    
    # 时间
    "time": {
        "morning": ["morning"],
        "evening": ["evening", "night", "midnight"],
        "dawn": ["dawn"],
        "dusk": ["sunset", "dusk"]
    },
    
    # 背景
    "background": {
        "location": ["Beijing", "shanghai", "Paris"],
        "style": ["chinese architecture"],
        "general": ["outdoors", "indoors", "city", "cityscape", "street", "road", "crosswalk", 
                  "sidewalk", "lamppost", "traffic light", "guard rail", "curtains", "neon city", 
                  "castle", "crowd", "audience"],
        "environment": ["beautiful forest", "ruins", "desert", "beach", "sea", "mountain", 
                      "volcanic mountain", "grassland", "plain", "lake", "wheat field", 
                      "stone hallway", "subsurface", "dungeon"],
        "facility": ["school", "classroom", "gymnasium", "sports hall", "train station", "bus stop", 
                   "museum", "library", "fort", "kitchen", "dining", "restaurant", "park", 
                   "amusement park", "parking lot", "public bath", "hot spring", "colloseum", 
                   "amusement arcade", "party"],
        "color": ["blue background"],
        "blur": ["blurry background", "depth of field", "bokeh"],
        "special": ["no background", "starly sky", "milky way", "bagua background", "yin yang background", 
                  "speed lines", "motion blur"]
    }
}

# 角色描述提示词（合并人物特征）
ROLE_PROMPT = {
    "age": HUMAN_PROMPTS["age"],
    "limbs": HUMAN_PROMPTS["limbs"],
    "skin": HUMAN_PROMPTS["skin"],
    "ethnicity": HUMAN_PROMPTS["ethnicity"],
    "body_type": HUMAN_PROMPTS["body_type"],
    "hair": HUMAN_PROMPTS["hair"],
    "face": HUMAN_PROMPTS["face"],
    "eyes": HUMAN_PROMPTS["eyes"],
    "ears": HUMAN_PROMPTS["ears"],
    "mouth": HUMAN_PROMPTS["mouth"],
    "nose": HUMAN_PROMPTS["nose"],
    "expression": HUMAN_PROMPTS["expression"],
    "tone": SCENE_PROMPTS["tone"],
}

# 场景描述提示词
SCENE_PROMPT = {
    "composition": SCENE_PROMPTS["composition"],
    "lighting": SCENE_PROMPTS["lighting"],
    "tone": SCENE_PROMPTS["tone"],
    "weather": SCENE_PROMPTS["weather"],
    "time": SCENE_PROMPTS["time"],
    "background": SCENE_PROMPTS["background"],
    "pattern": CLOTHING_PROMPTS["pattern"],
    "top": CLOTHING_PROMPTS["top"],
    "bottom": CLOTHING_PROMPTS["bottom"],
    "uniform": CLOTHING_PROMPTS["uniform"],
    "head_accessory": CLOTHING_PROMPTS["head_accessory"],
    "eye_accessory": CLOTHING_PROMPTS["eye_accessory"],
    "hand_accessory": CLOTHING_PROMPTS["hand_accessory"],
    "items": CLOTHING_PROMPTS["items"],
    "foot_wear": CLOTHING_PROMPTS["foot_wear"],
    "body_accessory": CLOTHING_PROMPTS["body_accessory"],
    "pose": HUMAN_PROMPTS["pose"],
    "count": HUMAN_PROMPTS["count"],

    
}