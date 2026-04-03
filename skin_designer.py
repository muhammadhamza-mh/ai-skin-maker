"""
Skin designer - all cosmetics drawn ON the character pixels (mask-constrained).
Cosmetics: crown, eye glow, collar, chest runes, belt, robe trim, scythe runes,
           scythe glow, orbiting particles, cape shimmer, shoulder pads.
"""
import os, math, random, io, base64, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BLACK_SKIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "black_skin")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

THEMES = [
    {"name":"Inferno",   "style":"armor",   "weapon":"sword",   "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(80,5,5),    "hl":(220,60,0),   "bd":(120,10,0),  "bl":(255,80,0),   "rd":(60,0,0),    "rl":(200,40,0),   "ac":(255,160,0), "hi":(255,230,80), "s":(155,75,45),  "pt":(255,70,0),   "fl":(255,50,50),"border":"fire_border","anim1":"hellfire","anim2":"lightning"},
    {"name":"Void",      "style":"robe",    "weapon":"scythe",  "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(10,0,25),   "hl":(100,0,180),  "bd":(15,0,35),   "bl":(140,0,220),  "rd":(8,0,20),    "rl":(80,0,150),   "ac":(180,80,255),"hi":(220,160,255),"s":(95,55,75),   "pt":(170,0,255),  "fl":(195,70,255),"border":"void_border","anim1":"wisps","anim2":"smoke"},
    {"name":"Frost",     "style":"royal",   "weapon":"staff",   "head_anim":"ice_crown",   "body_anim":"snowflakes",   "hd":(5,20,60),   "hl":(0,120,200),  "bd":(8,30,80),   "bl":(0,160,230),  "rd":(5,15,50),   "rl":(0,100,170),  "ac":(100,200,255),"hi":(200,240,255),"s":(130,165,195),"pt":(90,195,255), "fl":(170,235,255),"border":"ice_border","anim1":"crystal","anim2":"aurora"},
    {"name":"Toxic",     "style":"tattered","weapon":"axe",     "head_anim":"bubble_crown","body_anim":"drip_dots",    "hd":(5,25,5),    "hl":(30,160,30),  "bd":(8,35,8),    "bl":(50,200,50),  "rd":(5,20,5),    "rl":(30,140,30),  "ac":(150,255,50),"hi":(200,255,100),"s":(95,135,75),  "pt":(90,250,45),  "fl":(140,255,70),"border":"nature_border","anim1":"smoke","anim2":"wisps"},
    {"name":"Gold",      "style":"royal",   "weapon":"hammer",  "head_anim":"gold_crown",  "body_anim":"coin_sparkle", "hd":(50,30,0),   "hl":(180,120,0),  "bd":(70,45,0),   "bl":(220,160,0),  "rd":(40,25,0),   "rl":(160,100,0),  "ac":(255,200,0), "hi":(255,230,100),"s":(175,115,55), "pt":(255,190,0),  "fl":(255,170,0),"border":"gold_border","anim1":"sand","anim2":"lightning"},
    {"name":"Crimson",   "style":"armor",   "weapon":"sword",   "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(40,0,0),    "hl":(160,0,30),   "bd":(55,0,0),    "bl":(200,0,50),   "rd":(30,0,0),    "rl":(140,0,20),   "ac":(255,60,80), "hi":(255,160,180),"s":(155,75,75),  "pt":(255,0,70),   "fl":(255,90,140),"border":"fire_border","anim1":"blood","anim2":"hellfire"},
    {"name":"Ocean",     "style":"suit",    "weapon":"trident", "head_anim":"wave_crown",  "body_anim":"bubble_rise",  "hd":(0,12,40),   "hl":(0,80,140),   "bd":(0,18,55),   "bl":(0,110,180),  "rd":(0,10,35),   "rl":(0,70,120),   "ac":(0,180,255), "hi":(120,220,255),"s":(75,125,155), "pt":(0,175,255),  "fl":(70,215,255),"border":"electric_border","anim1":"aurora","anim2":"wisps"},
    {"name":"Neon",      "style":"ninja",   "weapon":"katana",  "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(5,0,20),    "hl":(0,200,160),  "bd":(8,0,25),    "bl":(0,240,180),  "rd":(5,0,15),    "rl":(0,180,140),  "ac":(180,255,0), "hi":(220,255,80), "s":(95,195,175), "pt":(0,255,175),  "fl":(175,255,0),"border":"electric_border","anim1":"lightning","anim2":"crystal"},
    {"name":"Sakura",    "style":"robe",    "weapon":"staff",   "head_anim":"petal_crown", "body_anim":"petal_fall",   "hd":(60,10,30),  "hl":(180,60,100), "bd":(75,15,40),  "bl":(220,90,130), "rd":(50,8,25),   "rl":(160,50,80),  "ac":(255,160,190),"hi":(255,210,225),"s":(195,135,125),"pt":(255,140,175),"fl":(255,175,205),"border":"nature_border","anim1":"wisps","anim2":"aurora"},
    {"name":"Phantom",   "style":"tattered","weapon":"scythe",  "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(20,0,35),   "hl":(120,0,155),  "bd":(28,0,48),   "bl":(160,0,200),  "rd":(15,0,28),   "rl":(100,0,130),  "ac":(200,100,255),"hi":(230,170,255),"s":(115,75,135), "pt":(195,45,255), "fl":(215,115,255),"border":"void_border","anim1":"wisps","anim2":"smoke"},
    {"name":"Lava",      "style":"armor",   "weapon":"hammer",  "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(30,5,0),    "hl":(190,60,0),   "bd":(45,8,0),    "bl":(230,90,0),   "rd":(25,4,0),    "rl":(170,50,0),   "ac":(255,180,0), "hi":(255,220,80), "s":(175,95,45),  "pt":(255,115,0),  "fl":(255,75,0),"border":"fire_border","anim1":"hellfire","anim2":"blood"},
    {"name":"Emerald",   "style":"royal",   "weapon":"axe",     "head_anim":"leaf_crown",  "body_anim":"leaf_swirl",   "hd":(0,28,12),   "hl":(0,130,60),   "bd":(0,38,18),   "bl":(0,170,80),   "rd":(0,22,10),   "rl":(0,110,50),   "ac":(80,240,140),"hi":(160,255,200),"s":(75,155,95),  "pt":(0,215,95),   "fl":(90,250,145),"border":"nature_border","anim1":"aurora","anim2":"wisps"},
    {"name":"Celestial", "style":"suit",    "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"star_orbit",   "hd":(0,5,38),    "hl":(60,60,180),  "bd":(0,8,50),    "bl":(80,80,210),  "rd":(0,4,30),    "rl":(50,50,160),  "ac":(160,160,255),"hi":(210,210,255),"s":(115,115,175),"pt":(115,115,255),"fl":(175,195,255),"border":"gold_border","anim1":"aurora","anim2":"crystal"},
    {"name":"Plague",    "style":"tattered","weapon":"axe",     "head_anim":"bubble_crown","body_anim":"drip_dots",    "hd":(12,20,0),   "hl":(80,130,0),   "bd":(18,28,0),   "bl":(100,160,0),  "rd":(10,16,0),   "rl":(70,110,0),   "ac":(160,220,0), "hi":(200,255,80), "s":(115,135,55), "pt":(145,215,0),  "fl":(175,250,45),"border":"nature_border","anim1":"smoke","anim2":"blood"},
    {"name":"Specter",   "style":"ninja",   "weapon":"katana",  "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(25,25,32),  "hl":(100,100,140),"bd":(35,35,45),  "bl":(130,130,170),"rd":(20,20,28),  "rl":(90,90,120),  "ac":(180,180,230),"hi":(220,220,255),"s":(155,155,175),"pt":(175,175,255),"fl":(215,215,255),"border":"void_border","anim1":"wisps","anim2":"lightning"},
    # ── Seasonal ──
    {"name":"Halloween", "style":"tattered","weapon":"scythe",  "head_anim":"fire_crown",  "body_anim":"drip_dots",    "hd":(5,3,0),     "hl":(57,40,24),   "bd":(4,3,0),     "bl":(95,78,39),   "rd":(0,0,0),     "rl":(176,204,41), "ac":(255,120,0), "hi":(200,230,40), "s":(84,68,30),   "pt":(255,100,0),  "fl":(180,220,0),"border":"fire_border","anim1":"blood","anim2":"wisps"},
    {"name":"Xmas",      "style":"royal",   "weapon":"staff",   "head_anim":"ice_crown",   "body_anim":"snowflakes",   "hd":(4,5,6),     "hl":(57,78,95),   "bd":(4,5,6),     "bl":(213,234,237),"rd":(4,5,6),     "rl":(232,241,250),"ac":(180,220,255),"hi":(255,255,255),"s":(200,160,140),"pt":(160,210,255),"fl":(255,255,255),"border":"ice_border","anim1":"crystal","anim2":"aurora"},
    {"name":"Easter",    "style":"robe",    "weapon":"staff",   "head_anim":"petal_crown", "body_anim":"petal_fall",   "hd":(20,20,20),  "hl":(152,80,153), "bd":(30,30,30),  "bl":(153,149,80), "rd":(0,0,0),     "rl":(255,255,232),"ac":(255,216,124),"hi":(255,255,200),"s":(200,160,130),"pt":(200,100,200),"fl":(255,220,100),"border":"nature_border","anim1":"wisps","anim2":"aurora"},
    {"name":"Lunar",     "style":"armor",   "weapon":"sword",   "head_anim":"gold_crown",  "body_anim":"coin_sparkle", "hd":(60,2,5),    "hl":(176,24,44),  "bd":(40,1,3),    "bl":(180,20,35),  "rd":(20,1,2),    "rl":(230,230,230),"ac":(255,200,0), "hi":(255,240,120),"s":(180,120,80), "pt":(255,180,0),  "fl":(255,220,50),"border":"gold_border","anim1":"sand","anim2":"lightning"},
    {"name":"Valentines","style":"robe",    "weapon":"staff",   "head_anim":"petal_crown", "body_anim":"void_orbs",    "hd":(27,2,39),   "hl":(59,38,111),  "bd":(27,2,39),   "bl":(77,50,146),  "rd":(20,0,60),   "rl":(43,0,171),   "ac":(255,80,150),"hi":(255,180,220),"s":(180,120,140),"pt":(255,60,120),  "fl":(255,150,200),"border":"void_border","anim1":"wisps","anim2":"blood"},
    {"name":"Patrick",   "style":"royal",   "weapon":"staff",   "head_anim":"leaf_crown",  "body_anim":"leaf_swirl",   "hd":(20,60,25),  "hl":(70,147,85),  "bd":(20,60,25),  "bl":(255,255,255),"rd":(15,50,20),  "rl":(255,231,47), "ac":(80,180,60), "hi":(255,240,50), "s":(160,180,100),"pt":(60,180,40),   "fl":(255,220,0),"border":"nature_border","anim1":"aurora","anim2":"sand"},
    # ── v1.01 Themes ──
    {"name":"Shadow",    "style":"ninja",   "weapon":"katana",  "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(5,5,8),     "hl":(30,30,50),   "bd":(8,8,12),    "bl":(50,50,80),   "rd":(3,3,5),     "rl":(20,20,35),   "ac":(80,80,120), "hi":(160,160,220),"s":(60,60,80),   "pt":(100,100,180),"fl":(120,120,200),"border":"void_border","anim1":"smoke","anim2":"wisps"},
    {"name":"Magma",     "style":"armor",   "weapon":"hammer",  "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(60,5,0),    "hl":(200,40,0),   "bd":(80,8,0),    "bl":(255,60,0),   "rd":(40,3,0),    "rl":(220,30,0),   "ac":(255,140,0), "hi":(255,220,50), "s":(180,90,40),  "pt":(255,80,0),   "fl":(255,160,0),"border":"fire_border","anim1":"hellfire","anim2":"blood"},
    {"name":"Arctic",    "style":"royal",   "weapon":"staff",   "head_anim":"ice_crown",   "body_anim":"snowflakes",   "hd":(15,25,40),  "hl":(60,100,150), "bd":(20,35,55),  "bl":(140,190,230),"rd":(10,20,35),  "rl":(200,220,240),"ac":(160,210,255),"hi":(240,250,255),"s":(160,190,210),"pt":(120,180,255),"fl":(200,230,255),"border":"ice_border","anim1":"crystal","anim2":"aurora"},
    {"name":"Demon",     "style":"tattered","weapon":"axe",     "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(40,0,0),    "hl":(120,0,0),    "bd":(50,0,5),    "bl":(160,0,10),   "rd":(30,0,0),    "rl":(100,0,5),    "ac":(220,0,0),   "hi":(255,80,0),   "s":(140,60,50),  "pt":(200,0,0),    "fl":(255,40,0),"border":"fire_border","anim1":"hellfire","anim2":"blood"},
    {"name":"Galaxy",    "style":"robe",    "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"star_orbit",   "hd":(5,0,20),    "hl":(40,0,80),    "bd":(8,0,30),    "bl":(80,20,140),  "rd":(3,0,15),    "rl":(50,10,100),  "ac":(180,100,255),"hi":(220,180,255),"s":(100,80,140), "pt":(160,80,255), "fl":(200,150,255),"border":"void_border","anim1":"aurora","anim2":"wisps"},
    {"name":"Cyber",     "style":"suit",    "weapon":"katana",  "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(0,20,20),   "hl":(0,100,100),  "bd":(0,25,25),   "bl":(0,160,160),  "rd":(0,15,15),   "rl":(0,120,120),  "ac":(0,220,200), "hi":(100,255,240),"s":(80,160,150), "pt":(0,200,180),  "fl":(50,255,220),"border":"electric_border","anim1":"lightning","anim2":"crystal"},
    {"name":"Storm",     "style":"armor",   "weapon":"trident", "head_anim":"wave_crown",  "body_anim":"bubble_rise",  "hd":(20,20,40),  "hl":(60,60,120),  "bd":(25,25,50),  "bl":(100,100,180),"rd":(15,15,30),  "rl":(80,80,150),  "ac":(150,150,255),"hi":(220,220,255),"s":(120,120,160),"pt":(130,130,255),"fl":(180,180,255),"border":"electric_border","anim1":"lightning","anim2":"smoke"},
    {"name":"Nature",    "style":"royal",   "weapon":"staff",   "head_anim":"leaf_crown",  "body_anim":"leaf_swirl",   "hd":(10,30,5),   "hl":(40,100,20),  "bd":(15,40,8),   "bl":(80,160,40),  "rd":(8,25,4),    "rl":(60,130,30),  "ac":(120,200,60),"hi":(200,240,120),"s":(120,160,80), "pt":(100,200,50), "fl":(180,230,100),"border":"nature_border","anim1":"aurora","anim2":"wisps"},
    {"name":"Abyssal",   "style":"robe",    "weapon":"scythe",  "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(0,5,15),    "hl":(0,20,50),    "bd":(0,8,20),    "bl":(0,40,80),    "rd":(0,4,12),    "rl":(0,25,60),    "ac":(0,80,160),  "hi":(0,160,220),  "s":(40,80,120),  "pt":(0,100,200),  "fl":(0,140,200),"border":"void_border","anim1":"wisps","anim2":"smoke"},
    {"name":"Prism",     "style":"suit",    "weapon":"sword",   "head_anim":"star_crown",  "body_anim":"coin_sparkle", "hd":(30,0,30),   "hl":(100,0,100),  "bd":(40,0,40),   "bl":(160,0,160),  "rd":(20,0,20),   "rl":(120,0,120),  "ac":(255,0,255), "hi":(255,180,255),"s":(160,100,160),"pt":(220,0,220),  "fl":(255,150,255),"border":"rainbow_border","anim1":"aurora","anim2":"crystal"},
    {"name":"Obsidian",  "style":"armor",   "weapon":"sword",   "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(8,8,10),    "hl":(25,25,35),   "bd":(10,10,14),  "bl":(40,40,60),   "rd":(6,6,8),     "rl":(20,20,30),   "ac":(80,80,120), "hi":(160,160,200),"s":(60,60,80),   "pt":(100,100,160),"fl":(120,120,180),"border":"void_border","anim1":"smoke","anim2":"wisps"},
    {"name":"Sunrise",   "style":"royal",   "weapon":"staff",   "head_anim":"gold_crown",  "body_anim":"coin_sparkle", "hd":(80,20,0),   "hl":(220,80,0),   "bd":(100,30,0),  "bl":(255,140,0),  "rd":(60,15,0),   "rl":(255,200,50), "ac":(255,160,0), "hi":(255,230,100),"s":(200,130,80), "pt":(255,120,0),  "fl":(255,200,50),"border":"gold_border","anim1":"aurora","anim2":"sand"},
    {"name":"Midnight",  "style":"ninja",   "weapon":"katana",  "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(5,5,20),    "hl":(20,20,60),   "bd":(8,8,25),    "bl":(30,30,80),   "rd":(4,4,15),    "rl":(15,15,50),   "ac":(60,60,180), "hi":(120,120,255),"s":(60,60,100),  "pt":(80,80,220),  "fl":(100,100,240),"border":"electric_border","anim1":"lightning","anim2":"wisps"},
    # ── v1.02 Themes ──
    {"name":"Aurora",    "style":"royal",   "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"aurora_wave",  "hd":(0,20,40),   "hl":(0,180,160),  "bd":(0,30,55),   "bl":(0,220,200),  "rd":(0,15,35),   "rl":(80,255,220), "ac":(0,255,200), "hi":(180,255,240),"s":(80,180,160), "pt":(0,220,180),  "fl":(100,255,220),"border":"ice_border","anim1":"aurora","anim2":"wisps"},
    {"name":"Infernal",  "style":"armor",   "weapon":"trident", "head_anim":"fire_crown",  "body_anim":"hellfire_rise","hd":(50,0,0),    "hl":(180,0,0),    "bd":(70,5,0),    "bl":(220,20,0),   "rd":(35,0,0),    "rl":(160,0,0),    "ac":(255,40,0),  "hi":(255,160,0),  "s":(160,70,40),  "pt":(255,20,0),   "fl":(255,100,0),"border":"fire_border","anim1":"hellfire","anim2":"blood"},
    {"name":"Crystal",   "style":"suit",    "weapon":"sword",   "head_anim":"ice_crown",   "body_anim":"crystal_shards","hd":(10,20,50),  "hl":(80,160,255), "bd":(15,30,70),  "bl":(120,200,255),"rd":(8,18,45),   "rl":(200,230,255),"ac":(100,180,255),"hi":(255,255,255),"s":(140,175,215),"pt":(80,160,255),"fl":(180,220,255),"border":"plasma_wide","anim1":"crystal","anim2":"iceshatter"},
    # ── v1.03 Themes ──
    {"name":"Wraith",    "style":"tattered","weapon":"scythe",  "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(5,5,10),    "hl":(60,60,80),   "bd":(8,8,15),    "bl":(90,90,120),  "rd":(3,3,8),     "rl":(50,50,70),   "ac":(150,150,200),"hi":(220,220,255),"s":(80,80,100),  "pt":(180,180,240),"fl":(200,200,255),"border":"void_border","anim1":"wisps","anim2":"smoke"},
    {"name":"Molten",    "style":"armor",   "weapon":"hammer",  "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(70,15,0),   "hl":(230,80,0),   "bd":(90,20,0),   "bl":(255,110,0),  "rd":(50,10,0),   "rl":(200,60,0),   "ac":(255,140,0), "hi":(255,220,80), "s":(190,100,50), "pt":(255,100,0),  "fl":(255,180,0),"border":"fire_border","anim1":"hellfire","anim2":"sand"},
    {"name":"Blossom",   "style":"robe",    "weapon":"staff",   "head_anim":"petal_crown", "body_anim":"petal_fall",   "hd":(50,5,25),   "hl":(200,80,120), "bd":(65,10,35),  "bl":(240,120,160),"rd":(40,4,20),   "rl":(255,180,210),"ac":(255,120,170),"hi":(255,220,235),"s":(200,140,155),"pt":(255,100,150),"fl":(255,200,220),"border":"nature_border","anim1":"wisps","anim2":"aurora"},
    {"name":"Thunder",   "style":"armor",   "weapon":"trident", "head_anim":"neon_ring",   "body_anim":"circuit_lines","hd":(15,15,40),  "hl":(80,80,180),  "bd":(20,20,55),  "bl":(120,120,220),"rd":(10,10,30),  "rl":(160,160,255),"ac":(180,180,255),"hi":(240,240,255),"s":(120,120,170),"pt":(150,150,255),"fl":(200,200,255),"border":"electric_border","anim1":"lightning","anim2":"smoke"},
    {"name":"Venom",     "style":"ninja",   "weapon":"katana",  "head_anim":"bubble_crown","body_anim":"drip_dots",    "hd":(0,30,0),    "hl":(0,160,40),   "bd":(0,40,5),    "bl":(0,200,60),   "rd":(0,20,0),    "rl":(80,220,80),  "ac":(80,255,80), "hi":(180,255,120),"s":(80,150,80),  "pt":(60,240,60),  "fl":(140,255,100),"border":"nature_border","anim1":"blood","anim2":"smoke"},
    {"name":"Sandstorm", "style":"royal",   "weapon":"axe",     "head_anim":"gold_crown",  "body_anim":"coin_sparkle", "hd":(60,40,10),  "hl":(200,150,50), "bd":(80,55,15),  "bl":(240,190,80), "rd":(45,30,8),   "rl":(220,170,60), "ac":(255,200,80),"hi":(255,240,160),"s":(200,160,100),"pt":(240,180,60), "fl":(255,220,120),"border":"gold_border","anim1":"sand","anim2":"smoke"},
    {"name":"Specter2",  "style":"tattered","weapon":"scythe",  "head_anim":"void_spiral", "body_anim":"void_orbs",    "hd":(0,0,20),    "hl":(0,0,80),     "bd":(0,0,28),    "bl":(0,0,120),    "rd":(0,0,15),    "rl":(0,0,90),     "ac":(0,80,255),  "hi":(80,160,255), "s":(40,60,120),  "pt":(0,100,255),  "fl":(60,140,255),"border":"electric_border","anim1":"lightning","anim2":"wisps"},
    {"name":"Plague2",   "style":"tattered","weapon":"axe",     "head_anim":"bubble_crown","body_anim":"drip_dots",    "hd":(20,25,0),   "hl":(100,140,0),  "bd":(28,35,0),   "bl":(140,180,0),  "rd":(15,20,0),   "rl":(120,160,0),  "ac":(180,230,0), "hi":(220,255,80), "s":(130,150,60), "pt":(160,220,0),  "fl":(200,255,60),"border":"nature_border","anim1":"blood","anim2":"smoke"},
    {"name":"Dusk",      "style":"robe",    "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"star_orbit",   "hd":(40,10,30),  "hl":(140,50,100), "bd":(55,15,40),  "bl":(180,80,130), "rd":(30,8,22),   "rl":(220,120,170),"ac":(255,100,160),"hi":(255,200,220),"s":(180,120,150),"pt":(240,80,140), "fl":(255,160,200),"border":"void_border","anim1":"wisps","anim2":"aurora"},
    {"name":"Titan",     "style":"armor",   "weapon":"hammer",  "head_anim":"gold_crown",  "body_anim":"lava_cracks",  "hd":(30,25,20),  "hl":(120,100,80), "bd":(40,35,28),  "bl":(160,140,110),"rd":(22,18,14),  "rl":(200,180,150),"ac":(220,200,160),"hi":(255,240,200),"s":(170,150,120),"pt":(200,180,140),"fl":(240,220,180),"border":"gold_border","anim1":"sand","anim2":"lightning"},
    {"name":"Wisp",      "style":"robe",    "weapon":"staff",   "head_anim":"petal_crown", "body_anim":"bubble_rise",  "hd":(10,20,30),  "hl":(60,120,180), "bd":(15,28,42),  "bl":(80,160,220), "rd":(8,15,25),   "rl":(120,180,240),"ac":(140,200,255),"hi":(220,240,255),"s":(120,160,200),"pt":(100,180,255),"fl":(180,220,255),"border":"ice_border","anim1":"wisps","anim2":"aurora"},
    {"name":"Reaper2",   "style":"tattered","weapon":"scythe",  "head_anim":"fire_crown",  "body_anim":"lava_cracks",  "hd":(20,0,20),   "hl":(100,0,100),  "bd":(28,0,28),   "bl":(140,0,140),  "rd":(15,0,15),   "rl":(180,0,180),  "ac":(220,0,220), "hi":(255,100,255),"s":(140,80,140), "pt":(200,0,200),  "fl":(255,80,255),"border":"void_border","anim1":"blood","anim2":"wisps"},
    {"name":"Blizzard",  "style":"royal",   "weapon":"staff",   "head_anim":"ice_crown",   "body_anim":"snowflakes",   "hd":(0,10,30),   "hl":(40,100,180), "bd":(0,15,40),   "bl":(60,140,210), "rd":(0,8,22),    "rl":(180,210,240),"ac":(120,180,255),"hi":(220,240,255),"s":(140,170,210),"pt":(100,160,255),"fl":(180,220,255),"border":"ice_border","anim1":"crystal","anim2":"aurora"},
    # ── v1.04 Themes ──
    {"name":"Dora",      "style":"royal",   "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"petal_fall",   "hd":(60,10,80),  "hl":(180,40,220), "bd":(80,15,100), "bl":(220,60,255), "rd":(40,8,60),   "rl":(200,100,240),"ac":(255,80,220), "hi":(255,200,255),"s":(180,120,180),"pt":(240,60,200),"fl":(255,160,240),"border":"flaming_wide","anim1":"wisps","anim2":"aurora","special1":"sparkle_trail","special2":"star_burst_fx"},
    {"name":"Doraemon",  "style":"suit",    "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"bubble_rise",  "hd":(0,60,160),  "hl":(0,140,220),  "bd":(0,80,180),  "bl":(0,180,240),  "rd":(0,50,140),  "rl":(100,200,255),"ac":(0,180,255),  "hi":(180,240,255),"s":(100,160,200),"pt":(0,200,255),"fl":(100,220,255),"border":"electric_wide","anim1":"crystal","anim2":"lightning","special1":"gadget_glow","special2":"pocket_sparkle"},
    {"name":"TrollFace", "style":"tattered","weapon":"axe",     "head_anim":"neon_ring",   "body_anim":"drip_dots",    "hd":(20,20,20),  "hl":(80,80,80),   "bd":(25,25,25),  "bl":(100,100,100),"rd":(15,15,15),  "rl":(60,60,60),   "ac":(200,200,200),"hi":(255,255,255),"s":(120,120,120),"pt":(180,180,180),"fl":(220,220,220),"border":"chaos_wide","anim1":"smoke","anim2":"blood","special1":"troll_grin","special2":"chaos_sparks"},
    {"name":"FreeStyle", "style":"ninja",   "weapon":"katana",  "head_anim":"void_spiral", "body_anim":"aurora_wave",  "hd":(20,0,40),   "hl":(120,0,200),  "bd":(30,0,55),   "bl":(160,20,240), "rd":(15,0,30),   "rl":(100,0,180),  "ac":(200,50,255), "hi":(240,150,255),"s":(140,80,160),"pt":(180,30,255),"fl":(220,100,255),"border":"rainbow_wide","anim1":"wisps","anim2":"sand","special1":"freestyle_trail","special2":"color_burst"},
    {"name":"Epic",      "style":"armor",   "weapon":"sword",   "head_anim":"fire_crown",  "body_anim":"hellfire_rise","hd":(60,0,10),   "hl":(220,20,40),  "bd":(80,5,15),   "bl":(255,40,60),  "rd":(45,0,8),    "rl":(200,15,30),  "ac":(255,50,80),  "hi":(255,180,200),"s":(180,80,100),"pt":(255,30,60),"fl":(255,120,150),"border":"flaming_wide","anim1":"hellfire","anim2":"lightning","special1":"epic_aura","special2":"power_surge"},
    {"name":"Nebula2",   "style":"robe",    "weapon":"staff",   "head_anim":"star_crown",  "body_anim":"soul_orbs",    "hd":(5,0,20),    "hl":(60,0,120),   "bd":(8,0,30),    "bl":(100,20,180), "rd":(3,0,15),    "rl":(70,10,140),  "ac":(160,80,255), "hi":(220,160,255),"s":(100,70,140), "pt":(140,60,255),"fl":(200,140,255),"border":"plasma_wide","anim1":"wisps","anim2":"aurora","special1":"void_rift","special2":"solar_flare"},
    {"name":"Solaris",   "style":"armor",   "weapon":"sword",   "head_anim":"gold_crown",  "body_anim":"divine_light", "hd":(60,30,0),   "hl":(220,140,0),  "bd":(80,40,0),   "bl":(255,180,0),  "rd":(45,22,0),   "rl":(240,200,50), "ac":(255,200,0),  "hi":(255,240,150),"s":(200,160,80), "pt":(255,180,0),"fl":(255,230,100),"border":"plasma_border","anim1":"aurora","anim2":"lightning","special1":"solar_flare","special2":"divine_rays"},
    {"name":"Legendary", "style":"royal",   "weapon":"staff",   "head_anim":"gold_crown",  "body_anim":"coin_sparkle", "hd":(50,35,0),   "hl":(200,160,0),  "bd":(70,50,0),   "bl":(240,200,20), "rd":(35,25,0),   "rl":(220,180,0),  "ac":(255,220,0),  "hi":(255,255,180),"s":(200,170,80),"pt":(255,200,0),"fl":(255,240,100),"border":"gold_wide","anim1":"aurora","anim2":"crystal","special1":"legendary_crown","special2":"divine_rays"},
]

# Exact per-frame data extracted from pixel analysis
FRAME_DATA = {
    "attack": [
        {"face":(246,190),"hface":(302,155),"eyes":[(199,149),(283,158)],"face_top":139,"head_top":(165,29),"head_w":166,"body":(215,125),"body_w":248,"bot":(234,238),"bot_w":195,"scythe":(175,29),"bbox":(82,29,339,253)},
        {"face":(241,144),"hface":(235,79), "eyes":[(271,86)],          "face_top":48, "head_top":(182,31),"head_w":227,"body":(196,123),"body_w":251,"bot":(198,231),"bot_w":126,"scythe":(171,31),"bbox":(69,31,322,246)},
        {"face":(271,170),"hface":(254,154),"eyes":[(199,149),(283,158)],"face_top":148,"head_top":(158,32),"head_w":185,"body":(161,113),"body_w":199,"bot":(203,206),"bot_w":199,"scythe":(168,32),"bbox":(62,32,303,221)},
        {"face":(268,188),"hface":(255,170),"eyes":[(199,149),(283,158)],"face_top":162,"head_top":(175,31),"head_w":214,"body":(174,112),"body_w":212,"bot":(202,206),"bot_w":187,"scythe":(170,31),"bbox":(68,31,296,221)},
        {"face":(246,188),"hface":(299,148),"eyes":[(202,144),(284,152)],"face_top":129,"head_top":(169,29),"head_w":165,"body":(218,126),"body_w":234,"bot":(232,240),"bot_w":200,"scythe":(174,29),"bbox":(87,29,335,255)},
        {"face":(227,211),"hface":(182,201),"eyes":[(148,202),(238,202)],"face_top":197,"head_top":(177,28),"head_w":164,"body":(217,142),"body_w":214,"bot":(227,277),"bot_w":205,"scythe":(177,28),"bbox":(95,28,330,292)},
        {"face":(235,204),"hface":(291,193),"eyes":[(149,194),(225,194)],"face_top":189,"head_top":(173,28),"head_w":164,"body":(221,138),"body_w":229,"bot":(234,268),"bot_w":203,"scythe":(175,28),"bbox":(91,28,336,283)},
        {"face":(241,197),"hface":(301,174),"eyes":[(199,149),(283,158)],"face_top":164,"head_top":(169,29),"head_w":166,"body":(222,133),"body_w":236,"bot":(232,255),"bot_w":194,"scythe":(174,29),"bbox":(86,29,340,270)},
    ],
    "idle": [
        {"face":(245,192),"hface":(303,158),"eyes":[(200,151),(282,162)],"face_top":143,"head_top":(166,31),"head_w":166,"body":(217,128),"body_w":246,"bot":(234,242),"bot_w":195,"scythe":(174,31),"bbox":(83,31,340,257)},
        {"face":(245,191),"hface":(302,158),"eyes":[(199,151),(282,161)],"face_top":142,"head_top":(165,30),"head_w":166,"body":(215,127),"body_w":247,"bot":(234,241),"bot_w":195,"scythe":(173,30),"bbox":(82,30,339,256)},
        {"face":(246,188),"hface":(301,153),"eyes":[(198,147),(283,156)],"face_top":136,"head_top":(163,29),"head_w":166,"body":(213,124),"body_w":252,"bot":(234,236),"bot_w":196,"scythe":(173,29),"bbox":(80,29,339,251)},
        {"face":(246,186),"hface":(301,148),"eyes":[(199,144),(282,152)],"face_top":131,"head_top":(160,28),"head_w":167,"body":(210,123),"body_w":255,"bot":(234,233),"bot_w":196,"scythe":(175,28),"bbox":(77,28,338,248)},
        {"face":(246,183),"hface":(300,144),"eyes":[(199,141),(282,148)],"face_top":126,"head_top":(158,27),"head_w":167,"body":(208,122),"body_w":256,"bot":(234,233),"bot_w":198,"scythe":(175,27),"bbox":(75,27,336,248)},
        {"face":(246,180),"hface":(299,139),"eyes":[(199,137),(281,143)],"face_top":120,"head_top":(156,27),"head_w":167,"body":(206,122),"body_w":258,"bot":(233,233),"bot_w":199,"scythe":(172,27),"bbox":(73,27,335,248)},
    ],
    "flying": [
        {"face":(241,198),"hface":(302,178),"eyes":[(150,188),(239,180)],"face_top":169,"head_top":(176,26),"head_w":164,"body":(225,132),"body_w":232,"bot":(236,258),"bot_w":209,"scythe":(175,26),"bbox":(94,26,341,273)},
        {"face":(241,199),"hface":(301,180),"eyes":[(151,189),(240,182)],"face_top":172,"head_top":(174,27),"head_w":164,"body":(224,134),"body_w":232,"bot":(236,260),"bot_w":209,"scythe":(177,27),"bbox":(92,27,341,275)},
        {"face":(240,201),"hface":(298,184),"eyes":[(150,190),(239,185)],"face_top":176,"head_top":(172,29),"head_w":165,"body":(223,136),"body_w":233,"bot":(235,262),"bot_w":209,"scythe":(176,29),"bbox":(90,29,340,277)},
        {"face":(239,202),"hface":(300,186),"eyes":[(149,191),(225,187)],"face_top":179,"head_top":(170,30),"head_w":165,"body":(222,138),"body_w":234,"bot":(234,265),"bot_w":209,"scythe":(176,30),"bbox":(88,30,339,280)},
        {"face":(238,204),"hface":(297,189),"eyes":[(148,191),(224,190)],"face_top":183,"head_top":(168,31),"head_w":165,"body":(221,139),"body_w":235,"bot":(234,267),"bot_w":209,"scythe":(176,31),"bbox":(86,31,339,282)},
    ],
}

def get_mask(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    return arr[:,:,3] > 10

def clamp_to_mask(x, y, mask):
    """Find nearest pixel inside mask to (x,y)"""
    h, w = mask.shape
    x, y = int(np.clip(x, 0, w-1)), int(np.clip(y, 0, h-1))
    if mask[y, x]:
        return x, y
    # Search nearby
    for r in range(1, 12):
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                nx, ny = x+dx, y+dy
                if 0<=nx<w and 0<=ny<h and mask[ny,nx]:
                    return nx, ny
    return x, y

def recolor(img_path, theme, variation):
    """Zone-aware recolor: head/body/robe each get different outfit colors.
       Chain (isolated right cluster) gets accent color treatment."""
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    out = arr.copy()
    r,g,b,a = arr[:,:,0],arr[:,:,1],arr[:,:,2],arr[:,:,3]
    gray = r*0.299 + g*0.587 + b*0.114
    mask = a > 10
    warm = (r>g)&(r>b)&((r-b)>20)&(r>80)&(r<200)&mask

    # Find character vertical extent for zone splitting
    rows = np.where(np.any(mask, axis=1))[0]
    if len(rows) == 0:
        return img
    rmin, rmax = rows[0], rows[-1]
    h_total = max(rmax - rmin, 1)

    # Detect chain pixels: isolated cluster separated from main body by a gap
    # For each row, find pixels that are >5px gap from the main body cluster
    chain_mask = np.zeros(arr.shape[:2], dtype=bool)
    for row in range(arr.shape[0]):
        row_px = np.where(mask[row])[0]
        if len(row_px) < 2:
            continue
        gaps = np.diff(row_px)
        big_gap_idx = np.where(gaps > 5)[0]
        if len(big_gap_idx) > 0:
            # Everything after the last big gap = chain
            split = big_gap_idx[-1] + 1
            chain_cols = row_px[split:]
            chain_mask[row, chain_cols] = True

    # Zone boundaries (applied to non-chain pixels)
    head_end = rmin + int(h_total * 0.28)
    body_end = rmin + int(h_total * 0.65)
    row_idx = np.arange(arr.shape[0])[:,None] * np.ones((1, arr.shape[1]))
    head_zone = (row_idx < head_end)
    body_zone  = (row_idx >= head_end) & (row_idx < body_end)
    robe_zone  = (row_idx >= body_end)

    ac_col = np.array(theme["ac"], dtype=np.float32)
    hi_col = np.array(theme["hi"], dtype=np.float32)
    style = theme.get("style", "robe")

    zones = [
        (head_zone, np.array(theme["hd"],dtype=np.float32), np.array(theme["hl"],dtype=np.float32)),
        (body_zone, np.array(theme["bd"],dtype=np.float32), np.array(theme["bl"],dtype=np.float32)),
        (robe_zone, np.array(theme["rd"],dtype=np.float32), np.array(theme["rl"],dtype=np.float32)),
    ]

    fl_col = np.array(theme["fl"], dtype=np.float32)
    pt_col = np.array(theme["pt"], dtype=np.float32)

    for zone_idx, (zone_mask_z, dark, light) in enumerate(zones):
        gm = (~warm) & mask & zone_mask_z & (~chain_mask)
        if not gm.any():
            continue
        t = np.clip((gray - 20) / 235, 0, 1)
        t_rich = np.power(t, 0.6)  # gamma → richer midtones

        for c in range(3):
            mapped = dark[c] + (light[c] - dark[c]) * t_rich

            if style == "armor":
                mapped = np.where(gray > 130, ac_col[c] + (hi_col[c]-ac_col[c])*np.clip((gray-130)/125,0,1), mapped)
                mapped = np.where(gray > 210, 255, mapped)
                # Head zone: add accent tint for richer look
                if zone_idx == 0:
                    mapped = mapped * 0.7 + ac_col[c] * 0.3
            elif style == "royal":
                mapped = np.where(gray > 150, hi_col[c]*np.clip((gray-150)/105,0,1) + mapped*(1-np.clip((gray-150)/105,0,1)), mapped)
                # Head: blend in flower color for richness
                if zone_idx == 0:
                    mapped = mapped * 0.75 + fl_col[c] * 0.25
            elif style == "ninja":
                mapped = np.where(gray < 60, mapped * 0.4, mapped)
                mapped = np.where(gray > 170, np.minimum(255, mapped * 1.4), mapped)
                if zone_idx == 0:
                    mapped = mapped * 0.6 + pt_col[c] * 0.4
            elif style == "suit":
                # Crystal: high contrast with strong specular highlights
                mapped = mapped * 0.75 + dark[c] * 0.25
                # Bright specular on highlights
                mapped = np.where(gray > 160, hi_col[c] * np.clip((gray-160)/95, 0, 1) + mapped * (1-np.clip((gray-160)/95, 0, 1)), mapped)
                # Pure white on brightest pixels (specular)
                mapped = np.where(gray > 220, 255, mapped)
                if zone_idx == 0:
                    mapped = mapped * 0.7 + ac_col[c] * 0.3
            elif style == "tattered":
                noise = np.sin(gray * 0.3) * 10
                mapped = np.clip(mapped + noise, 0, 255)
                if zone_idx == 0:
                    mapped = mapped * 0.7 + ac_col[c] * 0.3
            elif style == "robe":
                # Head: richer by blending accent
                if zone_idx == 0:
                    mapped = mapped * 0.65 + ac_col[c] * 0.35

            if variation:
                mapped = np.clip(mapped + variation*10*(c-1), 0, 255)
            out[:,:,c] = np.where(gm, np.clip(mapped, 0, 255), out[:,:,c])

    # Chain pixels: color with accent→highlight gradient (looks like glowing chain)
    if chain_mask.any():
        t = np.clip((gray - 20) / 235, 0, 1)
        for c in range(3):
            chain_color = ac_col[c] + (hi_col[c] - ac_col[c]) * t
            out[:,:,c] = np.where(chain_mask & (~warm), chain_color, out[:,:,c])

    # Skin tone pixels — richer gradient with subtle accent tint
    sk = np.array(theme["s"], dtype=np.float32)
    if warm.any():
        wg = gray[warm]
        t = np.clip((wg-80)/120, 0, 1)
        for c in range(3):
            # Base skin + slight accent tint on bright areas
            base = sk[c]*0.5 + sk[c]*0.7*t
            tinted = base * 0.85 + ac_col[c] * 0.15
            out[:,:,c][warm] = np.clip(tinted, 0, 255)

    out[:,:,3] = arr[:,:,3]
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8),"RGBA")

def px(draw, x, y, color, r=1):
    draw.ellipse([x-r,y-r,x+r,y+r], fill=color)

def draw_on_mask(img, mask, points_colors, radius=2):
    """Draw colored dots only where mask is True"""
    draw = ImageDraw.Draw(img)
    for (x,y),color in points_colors:
        x,y = int(x),int(y)
        h_,w_ = mask.shape
        if 0<=x<w_ and 0<=y<h_ and mask[y,x]:
            draw.ellipse([x-radius,y-radius,x+radius,y+radius], fill=color)


# ─── WEAPON OVERLAYS ──────────────────────────────────────────────────────────
# All weapons are drawn at the scythe tip position (sx, sy) pointing up-left
# The scythe blade area is rows ~31-70, cols ~84-241 in idle/1

def draw_weapon(draw, mask, sx, sy, weapon, ac, hi, pt, frame_idx, total, W, H):
    pulse = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 2)

    def dot(x, y, color, r=1):
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H and mask[yi, xi]:
            draw.ellipse([xi-r, yi-r, xi+r, yi+r], fill=color)

    def seg(x0, y0, x1, y1, color, w=2):
        # Only draw segment pixels that are on the mask
        steps = max(abs(int(x1)-int(x0)), abs(int(y1)-int(y0)), 1)
        for s in range(steps+1):
            t = s/steps
            xi,yi = int(x0+(x1-x0)*t), int(y0+(y1-y0)*t)
            if 0<=xi<W and 0<=yi<H and mask[yi,xi]:
                draw.ellipse([xi-w//2,yi-w//2,xi+w//2,yi+w//2], fill=color)

    # Blade origin: scythe tip area, draw relative to (sx, sy)
    bx, by = sx + 10, sy + 10   # blade anchor slightly inside

    if weapon == "sword":
        # Long straight blade going up-right from anchor
        blade_len = 55
        angle = math.radians(-55)
        ex = bx + math.cos(angle) * blade_len
        ey = by + math.sin(angle) * blade_len
        # Blade body (3 parallel lines = thick sword)
        for off in [-1, 0, 1]:
            seg(bx + off, by, ex + off, ey, hi + (220,), 2)
        # Edge highlight
        seg(bx - 1, by - 1, ex - 1, ey - 1, (255, 255, 255, 180), 1)
        # Guard (crossguard)
        gx, gy = bx + math.cos(angle)*20, by + math.sin(angle)*20
        perp = angle + math.pi/2
        seg(gx + math.cos(perp)*10, gy + math.sin(perp)*10,
            gx - math.cos(perp)*10, gy - math.sin(perp)*10, ac + (230,), 3)
        # Tip glow
        dot(ex, ey, pt + (int(150 + pulse*80),), int(3 + pulse*2))

    elif weapon == "hammer":
        # Short handle + big rectangular head
        handle_len = 35
        angle = math.radians(-50)
        hx = bx + math.cos(angle) * handle_len
        hy = by + math.sin(angle) * handle_len
        seg(bx, by, hx, hy, hi + (200,), 3)
        # Hammer head (rectangle perpendicular to handle)
        perp = angle + math.pi/2
        head_w, head_h = 18, 10
        for i in range(-head_h//2, head_h//2+1):
            sx2 = hx + math.cos(perp)*head_w + math.cos(angle)*i
            sy2 = hy + math.sin(perp)*head_w + math.sin(angle)*i
            ex2 = hx - math.cos(perp)*head_w + math.cos(angle)*i
            ey2 = hy - math.sin(perp)*head_w + math.sin(angle)*i
            seg(sx2, sy2, ex2, ey2, ac + (200,), 1)
        # Head highlight
        dot(hx, hy, hi + (int(180+pulse*60),), 4)

    elif weapon == "axe":
        # Handle + crescent axe head
        handle_len = 40
        angle = math.radians(-60)
        hx = bx + math.cos(angle) * handle_len
        hy = by + math.sin(angle) * handle_len
        seg(bx, by, hx, hy, hi + (200,), 3)
        # Axe blade: arc of dots
        for a_deg in range(-30, 80, 8):
            a_rad = math.radians(a_deg) + angle
            ax2 = hx + math.cos(a_rad) * 18
            ay2 = hy + math.sin(a_rad) * 18
            dot(ax2, ay2, ac + (220,), 3)
        # Inner arc (thinner)
        for a_deg in range(-20, 70, 10):
            a_rad = math.radians(a_deg) + angle
            ax2 = hx + math.cos(a_rad) * 12
            ay2 = hy + math.sin(a_rad) * 12
            dot(ax2, ay2, hi + (180,), 2)
        dot(hx, hy, pt + (int(160+pulse*80),), 3)

    elif weapon == "trident":
        # Long staff + 3 prongs at top
        staff_len = 50
        angle = math.radians(-80)
        tx = bx + math.cos(angle) * staff_len
        ty = by + math.sin(angle) * staff_len
        seg(bx, by, tx, ty, hi + (200,), 2)
        # 3 prongs
        for prong_off in [-12, 0, 12]:
            px2 = tx + prong_off
            py2 = ty
            seg(px2, py2, px2, py2 - 14, ac + (220,), 2)
            dot(px2, py2 - 14, pt + (int(160+pulse*80),), 2)
        # Middle prong longer
        seg(tx, ty, tx, ty - 20, hi + (230,), 2)
        dot(tx, ty - 20, (255,255,255,int(200+pulse*55)), 2)

    elif weapon == "katana":
        # Very long thin blade, slight curve
        blade_len = 65
        angle = math.radians(-50)
        for i in range(0, blade_len, 3):
            t = i / blade_len
            curve = math.sin(t * math.pi) * 4
            kx = bx + math.cos(angle)*i + math.cos(angle+math.pi/2)*curve
            ky = by + math.sin(angle)*i + math.sin(angle+math.pi/2)*curve
            alpha = int(220 - t*60)
            dot(kx, ky, hi + (alpha,), 1)
        # Edge line
        for i in range(0, blade_len, 2):
            t = i / blade_len
            curve = math.sin(t * math.pi) * 4
            kx = bx + math.cos(angle)*i + math.cos(angle+math.pi/2)*(curve+1)
            ky = by + math.sin(angle)*i + math.sin(angle+math.pi/2)*(curve+1)
            dot(kx, ky, (255,255,255,int(150-t*80)), 1)
        # Guard
        gx = bx + math.cos(angle)*8; gy = by + math.sin(angle)*8
        perp = angle + math.pi/2
        seg(gx+math.cos(perp)*8, gy+math.sin(perp)*8,
            gx-math.cos(perp)*8, gy-math.sin(perp)*8, ac+(230,), 2)
        # Tip glow
        tip_x = bx + math.cos(angle)*blade_len
        tip_y = by + math.sin(angle)*blade_len
        dot(tip_x, tip_y, pt+(int(140+pulse*80),), int(2+pulse*2))

    elif weapon == "staff":
        # Long staff with glowing orb at top
        staff_len = 55
        angle = math.radians(-75)
        tx = bx + math.cos(angle) * staff_len
        ty = by + math.sin(angle) * staff_len
        # Staff body with gradient
        for i in range(0, staff_len, 2):
            t = i / staff_len
            kx = bx + math.cos(angle)*i
            ky = by + math.sin(angle)*i
            c = tuple(int(hi[j]*0.4 + ac[j]*0.6*t) for j in range(3))
            dot(kx, ky, c+(200,), 2)
        # Orb at top
        orb_r = int(7 + pulse*3)
        draw.ellipse([int(tx)-orb_r, int(ty)-orb_r, int(tx)+orb_r, int(ty)+orb_r],
                     fill=pt+(int(100+pulse*80),))
        draw.ellipse([int(tx)-4, int(ty)-4, int(tx)+4, int(ty)+4],
                     fill=hi+(int(200+pulse*55),))
        # Orb sparkles
        for a_deg in range(0, 360, 60):
            a_rad = math.radians(a_deg + frame_idx*15)
            sx2 = tx + math.cos(a_rad)*(orb_r+3)
            sy2 = ty + math.sin(a_rad)*(orb_r+3)
            dot(sx2, sy2, (255,255,255,int(120+pulse*80)), 1)

    elif weapon == "scythe":
        # Enhanced version of original scythe with extra glow
        blade_len = 50
        for i in range(0, blade_len, 3):
            t = i / blade_len
            angle = math.radians(-40 - t*30)
            kx = bx + math.cos(angle)*i*0.8
            ky = by + math.sin(angle)*i*0.5
            alpha = int(180 - t*60)
            dot(kx, ky, ac+(alpha,), int(3-t*1.5))
        # Blade edge glow
        for i in range(0, blade_len, 4):
            t = i / blade_len
            angle = math.radians(-40 - t*30)
            kx = bx + math.cos(angle)*i*0.8 + 1
            ky = by + math.sin(angle)*i*0.5 - 1
            dot(kx, ky, hi+(int(120+pulse*80),), 1)
        dot(bx, by, pt+(int(160+pulse*80),), int(4+pulse*2))


# ─── PER-THEME HEAD ANIMATIONS ────────────────────────────────────────────────

def draw_head_anim(draw, mask, htx, hty, hw, head_anim, ac, hi, pt, fl, frame_idx, total, W, H):
    pulse  = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 2)
    pulse2 = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 4)
    t_norm = frame_idx / max(total - 1, 1)

    def dot(x, y, color, r=1):
        xi, yi = int(x), int(y)
        # Only draw ON the character mask AND below the scythe blade area
        # hty is the head_top row — restrict to rows >= hty+5 to avoid scythe
        if 0 <= xi < W and 0 <= yi < H and mask[yi, xi] and yi >= hty + 5:
            draw.ellipse([xi-r, yi-r, xi+r, yi+r], fill=color)

    crown_y = hty + 3

    if head_anim == "fire_crown":
        # Flame spikes that flicker in height
        for i, dx in enumerate([-10,-5,0,5,10]):
            flicker = int(8 + math.sin(frame_idx*1.3 + i*0.9)*5)
            for dy in range(flicker):
                t = dy / flicker
                c = tuple(int(fl[j]*(1-t) + ac[j]*t) for j in range(3))
                dot(htx+dx, crown_y-dy, c+(int(200-t*80),), 1)
        # Base band
        for dx in range(-13, 14, 2):
            dot(htx+dx, crown_y+4, ac+(200,), 1)

    elif head_anim == "void_spiral":
        # Spiral of dots rotating around head
        for i in range(8):
            angle = (i/8)*math.pi*2 + t_norm*math.pi*2
            r = 12 + i*1.5
            hx = htx + math.cos(angle)*r
            hy = hty + math.sin(angle)*r*0.4
            dot(hx, hy, pt+(int(120+80*math.sin(angle),),), int(2+pulse))
        # Crown spikes
        for i, dx in enumerate([-10,-5,0,5,10]):
            sh = int(7 + pulse2*4)
            dot(htx+dx, crown_y-sh, fl+(220,), 2)
            draw.line([htx+dx, crown_y-sh, htx+dx, crown_y+2], fill=hi+(160,), width=1)

    elif head_anim == "ice_crown":
        # Crystal spikes with icicle drip
        for i, dx in enumerate([-10,-5,0,5,10]):
            sh = [8,11,14,11,8][i]
            # Crystal spike
            draw.polygon([htx+dx, crown_y-sh, htx+dx+3, crown_y, htx+dx-3, crown_y],
                         fill=hi+(200,))
            dot(htx+dx, crown_y-sh, (255,255,255,220), 1)
        # Snowflake dots orbiting
        for i in range(6):
            angle = (i/6)*math.pi*2 + t_norm*math.pi*2
            hx = htx + math.cos(angle)*16
            hy = hty - 4 + math.sin(angle)*5
            dot(hx, hy, (200,240,255,int(140+80*pulse)), 2)

    elif head_anim == "bubble_crown":
        # Bubbles rising from head
        for i in range(5):
            rise = (frame_idx*(2+i)*3 + i*20) % 35
            bx2 = htx - 12 + i*6
            by2 = crown_y - rise
            r = int(2 + pulse*1.5)
            draw.ellipse([bx2-r, by2-r, bx2+r, by2+r], fill=ac+(int(160-rise*3),))
            dot(bx2-1, by2-1, hi+(int(100+pulse*60),), 1)
        # Crown base
        for dx in range(-12, 13, 3):
            dot(htx+dx, crown_y+3, ac+(180,), 1)

    elif head_anim == "gold_crown":
        # Solid crown with jewels
        for dx in range(-13, 14, 2):
            dot(htx+dx, crown_y+4, ac+(220,), 1)
        for i, dx in enumerate([-10,-5,0,5,10]):
            sh = [6,9,12,9,6][i]
            draw.polygon([htx+dx, crown_y-sh, htx+dx+4, crown_y, htx+dx-4, crown_y],
                         fill=ac+(220,))
            # Jewel at tip
            jewel_c = [fl, hi, (255,255,255), hi, fl][i]
            dot(htx+dx, crown_y-sh, jewel_c+(int(200+pulse*55),), 2)

    elif head_anim == "wave_crown":
        # Wave-shaped crown
        for dx in range(-14, 15, 2):
            wave_h = int(6 + math.sin(dx*0.4 + t_norm*math.pi*4)*5)
            for dy in range(wave_h):
                t = dy/wave_h
                c = tuple(int(ac[j]*(1-t)+hi[j]*t) for j in range(3))
                dot(htx+dx, crown_y-dy, c+(int(180+t*60),), 1)

    elif head_anim == "neon_ring":
        # Glowing neon ring
        ring_r = int(14 + pulse*3)
        for i in range(16):
            angle = (i/16)*math.pi*2 + t_norm*math.pi*2
            hx = htx + math.cos(angle)*ring_r
            hy = hty - 2 + math.sin(angle)*ring_r*0.3
            alpha = int(150+80*math.sin(angle+t_norm*math.pi*2))
            dot(hx, hy, ac+(max(0,alpha),), 2)
        # Crown spikes
        for dx in [-8,-4,0,4,8]:
            sh = int(6+pulse2*4)
            dot(htx+dx, crown_y-sh, hi+(220,), 2)

    elif head_anim == "petal_crown":
        # Flower petals around head
        for i in range(6):
            angle = (i/6)*math.pi*2 + t_norm*math.pi
            hx = htx + math.cos(angle)*14
            hy = hty - 2 + math.sin(angle)*5
            dot(hx, hy, fl+(int(160+80*pulse),), int(3+pulse))
        # Center
        dot(htx, hty-2, hi+(220,), 3)
        # Crown
        for dx in [-8,-4,0,4,8]:
            dot(htx+dx, crown_y-int(6+pulse*4), ac+(200,), 2)

    elif head_anim == "star_crown":
        # 5-pointed star crown
        for i in range(5):
            angle = (i/5)*math.pi*2 - math.pi/2 + t_norm*math.pi*0.5
            hx = htx + math.cos(angle)*14
            hy = hty - 2 + math.sin(angle)*5
            dot(hx, hy, hi+(int(180+pulse*60),), int(2+pulse))
        # Spikes
        for i, dx in enumerate([-10,-5,0,5,10]):
            sh = int(7+pulse*5)
            dot(htx+dx, crown_y-sh, ac+(220,), 2)
            draw.line([htx+dx, crown_y-sh, htx+dx, crown_y+2], fill=hi+(160,), width=1)

    elif head_anim == "leaf_crown":
        # Leaf-shaped crown
        for i, dx in enumerate([-10,-5,0,5,10]):
            sh = [7,10,13,10,7][i]
            # Leaf shape
            draw.polygon([htx+dx, crown_y-sh, htx+dx+4, crown_y-sh//2,
                          htx+dx, crown_y, htx+dx-4, crown_y-sh//2], fill=ac+(200,))
            dot(htx+dx, crown_y-sh, hi+(220,), 1)
        # Swaying dots
        for i in range(4):
            sway = int(math.sin(t_norm*math.pi*2+i)*5)
            dot(htx-9+i*6, hty-8+sway, fl+(int(160+pulse*60),), 2)


# ─── PER-THEME BODY ANIMATIONS ────────────────────────────────────────────────

def draw_body_anim(draw, mask, bx, by, bw, botx, boty, botw, body_anim,
                   ac, hi, pt, fl, frame_idx, total, W, H):
    pulse  = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 2)
    t_norm = frame_idx / max(total - 1, 1)

    def dot(x, y, color, r=1):
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H:
            draw.ellipse([xi-r, yi-r, xi+r, yi+r], fill=color)

    def on(x, y):
        xi, yi = int(x), int(y)
        return 0 <= xi < W and 0 <= yi < H and mask[yi, xi]

    if body_anim == "lava_cracks":
        # Glowing crack lines on body
        for i in range(4):
            cx = bx - bw//4 + i*(bw//3)
            cy = by - 15 + i*8
            crack_len = int(12 + pulse*6)
            angle = math.radians(70 + i*25)
            for j in range(crack_len):
                kx = cx + math.cos(angle)*j
                ky = cy + math.sin(angle)*j
                if on(kx, ky):
                    t = j/crack_len
                    c = tuple(int(ac[k]*(1-t)+hi[k]*t) for k in range(3))
                    dot(kx, ky, c+(int(180-t*80),), 1)

    elif body_anim == "void_orbs":
        # Small orbs orbiting body
        for i in range(5):
            angle = (i/5)*math.pi*2 + t_norm*math.pi*2
            ox = bx + math.cos(angle)*bw//3
            oy = by + math.sin(angle)*20
            if on(ox, oy):
                dot(ox, oy, pt+(int(160+60*math.sin(angle),),), int(2+pulse))

    elif body_anim == "snowflakes":
        # Snowflake dots drifting down
        for i in range(6):
            drift = (frame_idx*(2+i%3)*3 + i*15) % 50
            sx2 = bx - bw//3 + i*(bw*2//3//5)
            sy2 = by - 20 + drift
            if on(sx2, sy2):
                dot(sx2, sy2, hi+(int(180-drift*2),), 2)
                # Snowflake arms
                for a_deg in [0,60,120]:
                    a_rad = math.radians(a_deg)
                    dot(sx2+math.cos(a_rad)*3, sy2+math.sin(a_rad)*3, (255,255,255,120), 1)

    elif body_anim == "drip_dots":
        # Toxic drips falling from body
        for i in range(5):
            drip = (frame_idx*(3+i)*4 + i*18) % 45
            dx2 = bx - bw//3 + i*(bw*2//3//4)
            dy2 = by + drip
            if on(dx2, dy2):
                dot(dx2, dy2, ac+(int(200-drip*3),), int(2+pulse))

    elif body_anim == "coin_sparkle":
        # Gold sparkles on body
        for i in range(6):
            angle = (i/6)*math.pi*2 + t_norm*math.pi*4
            ox = bx + math.cos(angle)*bw//4
            oy = by + math.sin(angle)*15
            if on(ox, oy):
                dot(ox, oy, hi+(int(150+80*math.sin(angle*2),),), int(2+pulse))

    elif body_anim == "bubble_rise":
        # Bubbles rising through body
        for i in range(5):
            rise = (frame_idx*(2+i)*3 + i*20) % 60
            bx2 = bx - bw//3 + i*(bw*2//3//4)
            by2 = boty - rise
            if on(bx2, by2):
                r = int(2+pulse)
                draw.ellipse([bx2-r, by2-r, bx2+r, by2+r], fill=ac+(int(140-rise*1.5),))

    elif body_anim == "circuit_lines":
        # Neon circuit pattern
        for i in range(3):
            cx = bx - bw//4 + i*(bw//3)
            cy = by - 10 + i*10
            # Horizontal segment
            for dx2 in range(-8, 9, 2):
                if on(cx+dx2, cy):
                    dot(cx+dx2, cy, ac+(int(160+pulse*60),), 1)
            # Vertical segment
            for dy2 in range(-6, 7, 2):
                if on(cx, cy+dy2):
                    dot(cx, cy+dy2, hi+(int(140+pulse*60),), 1)
            # Node dot
            dot(cx, cy, pt+(int(200+pulse*55),), 2)

    elif body_anim == "petal_fall":
        # Petals drifting down
        for i in range(5):
            fall = (frame_idx*(2+i)*3 + i*22) % 55
            px2 = bx - bw//3 + i*(bw*2//3//4) + int(math.sin(fall*0.2)*5)
            py2 = by - 20 + fall
            if on(px2, py2):
                dot(px2, py2, fl+(int(180-fall*2),), int(2+pulse))

    elif body_anim == "star_orbit":
        # Stars orbiting body
        for i in range(4):
            angle = (i/4)*math.pi*2 + t_norm*math.pi*2
            ox = bx + math.cos(angle)*bw//3
            oy = by + math.sin(angle)*18
            if on(ox, oy):
                # Star shape
                dot(ox, oy, hi+(int(180+60*pulse),), 2)
                for a_deg in [0,72,144,216,288]:
                    a_rad = math.radians(a_deg)
                    dot(ox+math.cos(a_rad)*3, oy+math.sin(a_rad)*3, ac+(120,), 1)

    elif body_anim == "leaf_swirl":
        # Leaves swirling around body
        for i in range(5):
            angle = (i/5)*math.pi*2 + t_norm*math.pi*2
            ox = bx + math.cos(angle)*bw//3
            oy = by + math.sin(angle)*20
            if on(ox, oy):
                dot(ox, oy, ac+(int(160+60*math.sin(angle),),), int(2+pulse))
                dot(ox+2, oy-2, hi+(120,), 1)

    elif body_anim == "aurora_wave":
        # Northern lights — horizontal bands of color sweeping up the body
        colors = [ac, hi, pt, fl, (255,255,255)]
        for band in range(5):
            phase = (t_norm + band/5) % 1.0
            wave_y = int(boty - phase * (boty - (by - 30)))
            width = int(bw * 0.6 * math.sin(phase * math.pi))
            for dx2 in range(-width//2, width//2, 2):
                c = colors[band % len(colors)]
                alpha = int(180 * math.sin(phase * math.pi))
                if on(bx+dx2, wave_y):
                    dot(bx+dx2, wave_y, c+(alpha,), 2)
        # Shimmer dots
        for i in range(8):
            angle = (i/8)*math.pi*2 + t_norm*math.pi*3
            ox = bx + math.cos(angle)*bw//3
            oy = by + math.sin(angle)*22
            if on(ox, oy):
                dot(ox, oy, hi+(int(100+pulse*120),), int(1+pulse))

    elif body_anim == "hellfire_rise":
        # Hellfire columns rising from robe bottom
        for i in range(6):
            col_x = botx - botw//3 + i*(botw*2//3//5)
            height = int(20 + math.sin(t_norm*math.pi*2 + i*1.1)*12)
            for dy2 in range(height):
                t = dy2/height
                c = (int(255*(1-t*0.3)), int(40+80*t), 0)
                if on(col_x, boty-dy2):
                    dot(col_x, boty-dy2, c+(int(200-t*80),), int(2-t))
            # Ember sparks
            spark_rise = (frame_idx*(3+i)*4 + i*17) % 40
            if on(col_x, boty-height-spark_rise):
                dot(col_x, boty-height-spark_rise, pt+(int(200-spark_rise*4),), 2)
        # Ground fire glow
        for dx2 in range(-botw//2, botw//2, 3):
            wave = int(3*math.sin(dx2*0.3+t_norm*math.pi*4))
            if on(botx+dx2, boty+wave):
                dot(botx+dx2, boty+wave, ac+(int(120+pulse*80),), 2)

    elif body_anim == "crystal_shards":
        import colorsys
        # Large orbiting crystal shards with prismatic inner glow
        for i in range(8):
            angle = (i/8)*math.pi*2 + t_norm*math.pi*1.2
            dist = bw//3 + int(math.sin(t_norm*math.pi*2+i*0.8)*10)
            ox = bx + math.cos(angle)*dist
            oy = by + math.sin(angle)*22
            if on(ox, oy):
                r = int(5+pulse*3)
                # Outer glow halo
                draw.ellipse([int(ox)-r-3,int(oy)-r-3,int(ox)+r+3,int(oy)+r+3],fill=(100,180,255,int(60+pulse*40)))
                # Crystal diamond body
                draw.polygon([int(ox),int(oy)-r, int(ox)+r,int(oy), int(ox),int(oy)+r, int(ox)-r,int(oy)],fill=(120,200,255,int(200+pulse*40)))
                # Prismatic face highlight (shifts hue per shard)
                hue=(i/8+t_norm*0.3)%1.0; rc,gc,bc=colorsys.hsv_to_rgb(hue,0.4,1.0)
                draw.polygon([int(ox),int(oy)-r, int(ox)+r,int(oy), int(ox),int(oy)],fill=(int(rc*255),int(gc*255),int(bc*255),int(140+pulse*60)))
                # Sharp white specular
                dot(ox-1, oy-r+1, (255,255,255,int(220+pulse*35)), 1)
        # Deep crack lines with blue-white gradient
        for i in range(4):
            cx2 = bx - bw//3 + i*(bw*2//3//3)
            cy2 = by - 15 + i*10
            crack_len = int(14+pulse*6)
            angle = math.radians(50+i*25)
            for j in range(crack_len):
                kx = cx2 + math.cos(angle)*j
                ky = cy2 + math.sin(angle)*j
                if on(kx, ky):
                    t2 = j/crack_len
                    # Blue core with white edge
                    dot(kx, ky, (int(80+120*t2),int(160+80*t2),255,int(200-t2*80)), 1)
                    if j%3==0: dot(kx-1, ky-1, (255,255,255,int(120-t2*80)), 1)
        # Frost sparkles
        for i in range(5):
            a = (i/5)*math.pi*2 + t_norm*math.pi*2
            fx2 = bx + math.cos(a)*bw//4
            fy2 = by + math.sin(a)*14
            if on(fx2, fy2):
                dot(fx2, fy2, (220,240,255,int(140+pulse*80)), int(2+pulse))


    elif body_anim == "meteor_shower":
        for i in range(6):
            t2=(t_norm+i/6)%1.0; mx=bx-bw//2+int(t2*bw); my=by-30+int(t2*60)
            if on(mx,my): dot(mx,my,ac+(int(200-t2*100),),int(3-t2*2))
            for j in range(1,4):
                if on(mx-j,my-j): dot(mx-j,my-j,hi+(int(160-j*40),),1)

    elif body_anim == "ice_shatter":
        for i in range(8):
            a=(i/8)*math.pi*2+t_norm*math.pi*2
            dist=int((bw//3)*(0.5+0.5*math.sin(t_norm*math.pi*4+i)))
            ox=bx+math.cos(a)*dist; oy=by+math.sin(a)*dist*0.5
            if on(ox,oy):
                draw.polygon([int(ox),int(oy)-4,int(ox)+3,int(oy),int(ox),int(oy)+4,int(ox)-3,int(oy)],fill=hi+(int(160+pulse*80),))
                dot(ox,oy,(255,255,255,int(100+pulse*80)),1)

    elif body_anim == "dark_tendrils":
        for i in range(5):
            base_x=botx-botw//3+i*(botw*2//3//4)
            for step in range(10):
                rise=(frame_idx*3+i*9+step*4)%55
                sx2=base_x+int(math.sin((rise+i*15)*0.3)*10)
                sy2=boty-rise
                if on(sx2,sy2): dot(sx2,sy2,(int(ac[0]*0.4),int(ac[1]*0.4),int(ac[2]*0.4),int(160*(1-rise/55))),int(2-rise//30))

    elif body_anim == "neon_pulse":
        for ring in range(3):
            phase=(t_norm+ring/3)%1.0; ease=math.sin(phase*math.pi)
            r2=int(ease*bw*0.4); alpha=int(200*ease)
            if alpha>15:
                for a_deg in range(0,360,6):
                    a=math.radians(a_deg)
                    ox=bx+math.cos(a)*r2; oy=by+math.sin(a)*r2*0.5
                    if on(ox,oy): dot(ox,oy,ac+(alpha,),2)

    elif body_anim == "feather_fall":
        for i in range(6):
            fall=(frame_idx*(2+i%3)*3+i*19)%55
            fx2=botx-botw//3+i*(botw*2//3//5)+int(math.sin(fall*0.15)*6)
            fy2=boty-fall
            if on(fx2,fy2):
                draw.polygon([int(fx2),int(fy2)-5,int(fx2)+2,int(fy2),int(fx2),int(fy2)+5,int(fx2)-2,int(fy2)],fill=hi+(int(180-fall*2),))
                dot(fx2,fy2,(255,255,255,int(100-fall)),1)

    elif body_anim == "magma_flow":
        for i in range(5):
            cx2=bx-bw//3+i*(bw*2//3//4); cy2=by-10+i*6
            for j in range(int(12+pulse*6)):
                t2=j/(12+pulse*6)
                kx=cx2+math.sin(t2*math.pi*2+t_norm*math.pi*3)*8
                ky=cy2+j*3
                if on(kx,ky): dot(kx,ky,(int(255*(1-t2*0.3)),int(60+80*t2),0,int(200-t2*80)),int(2-t2))

    elif body_anim == "soul_orbs":
        for i in range(5):
            angle=(i/5)*math.pi*2+t_norm*math.pi*1.5
            dist=bw//3+int(math.sin(t_norm*math.pi*3+i*1.2)*8)
            ox=bx+math.cos(angle)*dist; oy=by+math.sin(angle)*22
            if on(ox,oy):
                draw.ellipse([int(ox)-5,int(oy)-8,int(ox)+5,int(oy)+8],fill=pt+(int(120+pulse*80),))
                draw.ellipse([int(ox)-3,int(oy)-5,int(ox)+3,int(oy)+5],fill=(255,255,255,int(80+pulse*60)))
                for t2 in range(1,4):
                    tx=ox+int(math.sin((t_norm*math.pi*2+i)*t2)*t2*2)
                    ty=oy+t2*5
                    if on(tx,ty): dot(tx,ty,ac+(int(100*(1-t2/4)),),2)

    elif body_anim == "pixel_glitch":
        for i in range(10):
            gx=bx-bw//2+random.randint(0,bw)
            gy=by-20+random.randint(0,50)
            if on(gx,gy) and (frame_idx+i)%3<2:
                import colorsys
                hue=random.random(); r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
                draw.rectangle([int(gx),int(gy),int(gx)+random.randint(2,8),int(gy)+2],fill=(int(r2*255),int(g2*255),int(b2*255),int(160+pulse*60)))

    elif body_anim == "chain_lightning":
        pts=[(bx+random.randint(-bw//3,bw//3), by-20+i*12) for i in range(5)]
        for i in range(len(pts)-1):
            x0,y0=pts[i]; x1,y1=pts[i+1]
            steps=max(abs(x1-x0),abs(y1-y0),1)
            for s in range(steps):
                t2=s/steps; px2=int(x0+(x1-x0)*t2); py2=int(y0+(y1-y0)*t2)
                if on(px2,py2): dot(px2,py2,hi+(int(180+pulse*60),),int(1+pulse))
            if on(x1,y1): dot(x1,y1,(255,255,255,int(200+pulse*55)),2)

    elif body_anim == "divine_light":
        for i in range(6):
            a=math.radians(i*60+t_norm*20)
            for r2 in range(5,bw//2,6):
                ox=bx+math.cos(a)*r2; oy=by+math.sin(a)*r2*0.5
                alpha=int(120*(1-r2/(bw//2))*pulse)
                if on(ox,oy) and alpha>10: dot(ox,oy,(255,255,220,alpha),1)
        dot(bx,by-5,(255,255,255,int(180+pulse*60)),int(3+pulse))


def draw_theme_extras(img, mask, fd, theme, frame_idx, total, anim):
    """10 unique cosmetics per theme group, enhancing eyes/face/hands/body/scythe."""
    draw = ImageDraw.Draw(img)
    name = theme["name"]
    ac = theme["ac"]; hi = theme["hi"]; pt = theme["pt"]; fl = theme["fl"]
    pulse  = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 2)
    pulse2 = 0.5 + 0.5 * math.sin(frame_idx / total * math.pi * 4)
    t_norm = frame_idx / max(total - 1, 1)
    W, H = img.width, img.height
    fx,fy = fd["face"]; hfx,hfy = fd.get("hface",fd["face"]); htx,hty = fd["head_top"]; hw = fd["head_w"]
    bx,by = fd["body"]; bw = fd["body_w"]
    botx,boty = fd["bot"]; botw = fd["bot_w"]
    sx,sy = fd["scythe"]; x1,y1,x2,y2 = fd["bbox"]

    def on(x,y): xi,yi=int(x),int(y); return 0<=xi<W and 0<=yi<H and mask[yi,xi]
    def dot(x,y,c,r=1): xi,yi=int(x),int(y); 0<=xi<W and 0<=yi<H and draw.ellipse([xi-r,yi-r,xi+r,yi+r],fill=c)
    def seg(x0,y0,x1_,y1_,c,w=1): draw.line([int(x0),int(y0),int(x1_),int(y1_)],fill=c,width=w)

    # ── HALLOWEEN ─────────────────────────────────────────────────────────
    if name == "Halloween":
        # 1. Jack-o-lantern eyes (triangle eyes on face)
        for ex,ew in [(fx-10,5),(fx+4,5)]:
            if on(ex,fy-6):
                draw.polygon([ex,fy-10, ex+ew,fy-6, ex-ew,fy-6], fill=(255,120,0,220))
        # 2. Stitched mouth on face
        for i in range(4):
            mx = fx-8+i*5; my = fy+2
            if on(mx,my): dot(mx,my,(0,0,0,200),1)
            if on(mx,my+3): seg(mx,my,mx,my+3,(200,200,200,160))
        # 3. Lime green robe glow dots
        for i in range(8):
            angle = (i/8)*math.pi*2 + t_norm*math.pi*2
            gx = botx + math.cos(angle)*botw//3
            gy = boty - 10 + math.sin(angle)*15
            if on(gx,gy): dot(gx,gy,(176,204,41,int(160+pulse*80)),2)
        # 4. Spider web on shoulder
        spx,spy = bx-bw//2+15, by-18
        for a_deg in range(0,360,45):
            a=math.radians(a_deg); ex2=spx+math.cos(a)*10; ey2=spy+math.sin(a)*10
            if on(spx,spy) and on(ex2,ey2): seg(spx,spy,ex2,ey2,(200,200,200,120))
        for r2 in [4,8]:
            for a_deg in range(0,360,45):
                a=math.radians(a_deg); a2=math.radians(a_deg+45)
                if on(spx+math.cos(a)*r2,spy+math.sin(a)*r2):
                    seg(spx+math.cos(a)*r2,spy+math.sin(a)*r2,spx+math.cos(a2)*r2,spy+math.sin(a2)*r2,(180,180,180,100))
        # 5. Bat wings on back (body sides)
        for side in [-1,1]:
            wx=bx+side*(bw//2-5); wy=by-10
            if on(wx,wy):
                draw.polygon([wx,wy, wx+side*15,wy-12, wx+side*8,wy-5, wx+side*20,wy-8, wx+side*12,wy+2],fill=(20,0,30,180))
        # 6. Glowing scythe blade (orange-green)
        for i in range(6):
            t=i/5; rx=int(sx+t*30*0.6); ry=int(sy+t*30*0.35)
            if on(rx,ry):
                c=(int(255*(1-t)+176*t),int(120*(1-t)+204*t),0,int(180+pulse*60))
                dot(rx,ry,c,2)
        # 7. Skull on chest
        skx,sky=bx,by-8
        if on(skx,sky):
            draw.ellipse([skx-5,sky-5,skx+5,sky+3],fill=(220,210,180,180))
            for ex2 in [skx-2,skx+2]:
                if on(ex2,sky): dot(ex2,sky,(0,0,0,200),1)
            if on(skx,sky+2): seg(skx-3,sky+2,skx+3,sky+2,(0,0,0,160))
        # 8. Dripping blood from scythe
        for i in range(3):
            drip=(frame_idx*(3+i)*4+i*15)%25
            dx2=sx-5+i*5; dy2=sy+10+drip
            if on(dx2,dy2): dot(dx2,dy2,(180,0,0,int(200-drip*5)),int(2-drip//15))
        # 10. Pumpkin glow on robe bottom
        for i in range(5):
            px2=botx-botw//3+i*(botw*2//3//4); py2=boty+3
            if on(px2,py2):
                draw.ellipse([px2-4,py2-4,px2+4,py2+4],fill=(255,100,0,int(80+pulse*60)))
                dot(px2,py2,(255,200,0,int(120+pulse*80)),1)

    # ── XMAS ──────────────────────────────────────────────────────────────
    elif name == "Xmas":
        # 1. Santa hat on head
        hat_cx,hat_cy = htx+5,hty+2
        draw.polygon([hat_cx-12,hat_cy+8, hat_cx+12,hat_cy+8, hat_cx+4,hat_cy-18],fill=(180,0,0,200))
        draw.ellipse([hat_cx-13,hat_cy+5,hat_cx+13,hat_cy+11],fill=(255,255,255,220))
        dot(hat_cx+4,hat_cy-18,(255,255,255,230),3)
        # 2. Snowflake on chest
        for a_deg in range(0,360,60):
            a=math.radians(a_deg)
            if on(bx+math.cos(a)*8,by-5+math.sin(a)*8):
                seg(bx,by-5,bx+math.cos(a)*8,by-5+math.sin(a)*8,(200,230,255,int(160+pulse*60)))
        dot(bx,by-5,(255,255,255,220),2)
        # 3. Icicle drips from robe
        for i in range(6):
            ix=botx-botw//3+i*(botw*2//3//5)
            ilen=int(6+pulse2*4+i%3*3)
            if on(ix,boty):
                draw.polygon([ix-2,boty, ix+2,boty, ix,boty+ilen],fill=(180,220,255,int(160+pulse*60)))
        # 4. Glowing star on scythe tip
        for a_deg in range(0,360,72):
            a=math.radians(a_deg+t_norm*360)
            dot(sx+math.cos(a)*8,sy+math.sin(a)*8,(255,255,200,int(120+pulse*80)),2)
        dot(sx,sy,(255,255,255,int(200+pulse*55)),3)
        # 5. Gift bow on belt
        belt_y=by+20
        if on(bx,belt_y):
            draw.polygon([bx-6,belt_y-4, bx,belt_y, bx-6,belt_y+4],fill=(255,0,0,180))
            draw.polygon([bx+6,belt_y-4, bx,belt_y, bx+6,belt_y+4],fill=(255,0,0,180))
            dot(bx,belt_y,(255,200,0,220),2)
        # 6. Falling snowflakes on body
        for i in range(5):
            fall=(frame_idx*(2+i)*3+i*20)%50
            sx2=bx-bw//3+i*(bw*2//3//4); sy2=by-20+fall
            if on(sx2,sy2):
                dot(sx2,sy2,(220,240,255,int(180-fall*2)),2)
                for a_deg in [0,60,120]:
                    a=math.radians(a_deg)
                    if on(sx2+math.cos(a)*3,sy2+math.sin(a)*3): dot(sx2+math.cos(a)*3,sy2+math.sin(a)*3,(255,255,255,100),1)
        # 7. Candy cane stripes on scythe handle
        for i in range(0,30,5):
            t=i/30; hx2=int(sx+t*20); hy2=int(sy+t*10)
            if on(hx2,hy2): dot(hx2,hy2,(255,0,0,180) if i%10==0 else (255,255,255,160),2)
        # 9. Bell on shoulder
        for sdx in [-bw//2+10, bw//2-10]:
            bsx,bsy=bx+sdx,by-18
            if on(bsx,bsy):
                draw.ellipse([bsx-4,bsy-4,bsx+4,bsy+4],fill=(255,200,0,int(180+pulse*60)))
                dot(bsx,bsy+4,(100,60,0,200),1)
        # 10. Wreath on head
        for i in range(10):
            a=math.radians(i*36+t_norm*30)
            hx2=htx+math.cos(a)*13; hy2=hty-2+math.sin(a)*4
            dot(hx2,hy2,(0,140,0,int(160+pulse*40)),2)
            if i%3==0: dot(hx2,hy2,(255,0,0,200),1)

    # ── EASTER ────────────────────────────────────────────────────────────
    elif name == "Easter":
        # 1. Bunny ears on head
        for side,dx in [(-1,-10),(1,6)]:
            ex2,ey2=htx+dx,hty-2
            draw.polygon([ex2-3,ey2, ex2+3,ey2, ex2+2,ey2-18, ex2-2,ey2-18],fill=(255,200,220,200))
            draw.polygon([ex2-1,ey2-2, ex2+1,ey2-2, ex2+1,ey2-14, ex2-1,ey2-14],fill=(255,150,180,180))
        # 2. Easter egg pattern on body
        for i in range(3):
            ex2=bx-10+i*10; ey2=by-5+i*5
            if on(ex2,ey2):
                draw.ellipse([ex2-5,ey2-7,ex2+5,ey2+7],fill=[(255,150,200),(200,255,150),(150,200,255)][i]+(160,))
                seg(ex2-5,ey2,ex2+5,ey2,(255,255,255,120))
        # 3. Flower crown
        for i in range(6):
            a=math.radians(i*60+t_norm*30)
            hx2=htx+math.cos(a)*12; hy2=hty-2+math.sin(a)*4
            dot(hx2,hy2,fl+(int(180+pulse*60),),3)
        dot(htx,hty-2,(255,255,200,220),3)
        # 4. Pastel sparkles on robe
        colors=[(255,150,200),(200,255,150),(150,200,255),(255,255,150)]
        for i in range(8):
            a=(i/8)*math.pi*2+t_norm*math.pi*2
            gx=botx+math.cos(a)*botw//3; gy=boty-10+math.sin(a)*12
            if on(gx,gy): dot(gx,gy,colors[i%4]+(int(140+pulse*80),),2)
        # 5. Chick on shoulder
        for sdx in [bw//2-12]:
            cx2,cy2=bx+sdx,by-20
            if on(cx2,cy2):
                draw.ellipse([cx2-5,cy2-5,cx2+5,cy2+5],fill=(255,220,0,200))
                dot(cx2+3,cy2-1,(255,120,0,220),1)
                dot(cx2+1,cy2-3,(0,0,0,220),1)
        # 6. Rainbow arc on scythe
        rainbow=[(255,0,0),(255,165,0),(255,255,0),(0,200,0),(0,100,255),(150,0,255)]
        for j,rc in enumerate(rainbow):
            r2=8+j*2
            for a_deg in range(-60,60,10):
                a=math.radians(a_deg)
                rx2=sx+math.cos(a)*r2; ry2=sy-math.sin(a)*r2
                dot(rx2,ry2,rc+(int(140+pulse*60),),1)
        # 8. Carrot on belt
        belt_y=by+20
        if on(bx,belt_y):
            draw.polygon([bx-3,belt_y-6, bx+3,belt_y-6, bx,belt_y+4],fill=(255,120,0,200))
            seg(bx,belt_y-6,bx,belt_y-10,(0,180,0,180))
        # 9. Pastel robe trim
        for i in range(14):
            tx=botx-botw//2+int(i*(botw/13)); wave=int(3*math.sin(i*0.8+frame_idx*0.5))
            if on(tx,boty+wave): dot(tx,boty+wave,colors[i%4]+(int(160+pulse*60),),2)
        # 10. Butterfly on back
        bfx,bfy=bx-bw//3,by-5
        if on(bfx,bfy):
            for side in [-1,1]:
                draw.polygon([bfx,bfy, bfx+side*12,bfy-8, bfx+side*10,bfy+5],fill=(255,150,200,int(140+pulse*60)))

    # ── LUNAR ─────────────────────────────────────────────────────────────
    elif name == "Lunar":
        # 1. Dragon scales on body
        for i in range(4):
            for j in range(3):
                sx2=bx-bw//3+i*(bw*2//3//3); sy2=by-15+j*10
                if on(sx2,sy2):
                    draw.ellipse([sx2-4,sy2-3,sx2+4,sy2+3],fill=(200,20,30,int(140+pulse*40)))
                    seg(sx2-4,sy2,sx2+4,sy2,(255,200,0,100))
        # 2. Lantern on scythe tip
        if on(sx,sy):
            draw.ellipse([sx-6,sy-8,sx+6,sy+8],fill=(255,180,0,int(160+pulse*60)))
            draw.ellipse([sx-3,sy-5,sx+3,sy+5],fill=(255,220,100,int(180+pulse*60)))
            dot(sx,sy,(255,255,200,int(200+pulse*55)),2)
            for a_deg in range(0,360,45):
                a=math.radians(a_deg+t_norm*360)
                dot(sx+math.cos(a)*9,sy+math.sin(a)*9,(255,200,0,int(80+pulse*60)),1)
        # 3. Gold dragon horns on head
        for side,dx in [(-1,-8),(1,4)]:
            hx2,hy2=htx+dx,hty+2
            draw.polygon([hx2,hy2, hx2+side*3,hy2-12, hx2+side*6,hy2-8],fill=(255,200,0,200))
        # 4. Red tassel on belt
        belt_y=by+20
        for i in range(5):
            tx=bx-4+i*2; ty=belt_y+3
            tlen=int(8+pulse*4+i%3*3)
            if on(tx,ty): seg(tx,ty,tx,ty+tlen,(200,0,30,int(180+pulse*40)))
        # 5. Firework sparks on body
        for i in range(5):
            a=(i/5)*math.pi*2+t_norm*math.pi*4
            fx2=bx+math.cos(a)*bw//4; fy2=by+math.sin(a)*15
            if on(fx2,fy2): dot(fx2,fy2,(255,200,0,int(120+pulse*80)),int(2+pulse))
        # 7. Cloud pattern on robe
        for i in range(4):
            cx2=botx-botw//3+i*(botw*2//3//3); cy2=boty-5
            if on(cx2,cy2):
                draw.ellipse([cx2-6,cy2-3,cx2+6,cy2+3],fill=(255,255,255,int(80+pulse*40)))
                draw.ellipse([cx2-3,cy2-5,cx2+3,cy2+1],fill=(255,255,255,int(60+pulse*40)))
        # 8. Gold trim on shoulders
        for sdx in [-bw//2+8, bw//2-8]:
            spx,spy=bx+sdx,by-20
            if on(spx,spy):
                draw.ellipse([spx-7,spy-5,spx+7,spy+5],fill=(200,150,0,int(160+pulse*60)))
                draw.ellipse([spx-4,spy-3,spx+4,spy+3],fill=(255,220,50,200))
        # 9. Yin-yang on chest
        if on(bx,by-5):
            draw.ellipse([bx-6,by-11,bx+6,by+1],fill=(200,0,20,180))
            draw.ellipse([bx-6,by-11,bx+6,by+1],outline=(255,200,0,200),width=1)
            dot(bx,by-8,(255,200,0,200),2); dot(bx,by-2,(200,0,20,200),2)
        # 10. Coin sparkles on robe
        for i in range(6):
            a=(i/6)*math.pi*2+t_norm*math.pi*2
            gx=botx+math.cos(a)*botw//3; gy=boty-8+math.sin(a)*10
            if on(gx,gy): dot(gx,gy,(255,200,0,int(160+pulse*80)),int(2+pulse))

    # ── VALENTINES ────────────────────────────────────────────────────────
    elif name == "Valentines":
        # 1. Heart crown
        for i,dx in enumerate([-8,-3,2,7]):
            hx2,hy2=htx+dx,hty+2
            sh=int(8+pulse*4) if i==1 or i==2 else int(5+pulse*3)
            draw.polygon([hx2,hy2-sh, hx2-4,hy2-sh+4, hx2,hy2, hx2+4,hy2-sh+4],fill=(255,60,120,int(200+pulse*40)))
        # 2. Heart particles floating up
        for i in range(5):
            rise=(frame_idx*(2+i)*3+i*20)%50
            hpx=bx-bw//3+i*(bw*2//3//4); hpy=by-rise
            if on(hpx,hpy):
                draw.polygon([hpx,hpy-3, hpx-3,hpy-6, hpx,hpy-4, hpx+3,hpy-6],fill=(255,80,150,int(180-rise*2)))
        # 3. Rose on chest
        if on(bx,by-8):
            draw.ellipse([bx-5,by-13,bx+5,by-3],fill=(200,0,60,200))
            draw.ellipse([bx-3,by-11,bx+3,by-5],fill=(255,60,100,180))
            seg(bx,by-3,bx,by+5,(0,120,0,160),2)
        # 5. Cupid arrow on scythe
        arrow_len=30; a=math.radians(-50)
        ax2=sx+math.cos(a)*arrow_len; ay2=sy+math.sin(a)*arrow_len
        seg(sx,sy,ax2,ay2,(255,100,150,int(180+pulse*60)),2)
        draw.polygon([int(ax2),int(ay2), int(ax2-6),int(ay2+4), int(ax2-4),int(ay2-4)],fill=(255,60,120,220))
        draw.polygon([int(sx),int(sy), int(sx+5),int(sy-3), int(sx+5),int(sy+3)],fill=(255,200,220,200))
        # 6. Lace trim on robe
        for i in range(14):
            tx=botx-botw//2+int(i*(botw/13)); wave=int(3*math.sin(i*0.8+frame_idx*0.5))
            if on(tx,boty+wave):
                dot(tx,boty+wave,(255,150,200,int(160+pulse*60)),2)
                if i%2==0 and on(tx,boty+wave+5): dot(tx,boty+wave+5,(255,200,230,120),1)
        # 7. Ribbon on shoulders
        for sdx in [-bw//2+8, bw//2-8]:
            spx,spy=bx+sdx,by-20
            if on(spx,spy):
                draw.polygon([spx-6,spy-4, spx,spy, spx-6,spy+4],fill=(255,60,120,int(160+pulse*60)))
                draw.polygon([spx+6,spy-4, spx,spy, spx+6,spy+4],fill=(255,60,120,int(160+pulse*60)))
                dot(spx,spy,(255,200,0,220),2)
        # 8. Pink aura on body
        for i in range(6):
            a=(i/6)*math.pi*2+t_norm*math.pi*2
            ox=bx+math.cos(a)*bw//3; oy=by+math.sin(a)*18
            if on(ox,oy): dot(ox,oy,(255,100,160,int(100+pulse*80)),int(2+pulse))
        # 10. Sparkle trail on chain
        chain_cx=x2-20
        for i in range(5):
            cy2=(y1+y2)//2-20+i*10
            if on(chain_cx,cy2): dot(chain_cx,cy2,(255,100,160,int(120+pulse*80)),int(2+pulse))

    # ── PATRICK ───────────────────────────────────────────────────────────
    elif name == "Patrick":
        # 1. Leprechaun top hat
        hat_cx,hat_cy=htx+3,hty+2
        draw.rectangle([hat_cx-10,hat_cy-20,hat_cx+10,hat_cy+2],fill=(20,80,25,220))
        draw.rectangle([hat_cx-13,hat_cy,hat_cx+13,hat_cy+5],fill=(20,80,25,220))
        draw.rectangle([hat_cx-10,hat_cy-12,hat_cx+10,hat_cy-9],fill=(255,220,0,220))
        dot(hat_cx,hat_cy-10,(255,200,0,220),2)
        # 2. Four-leaf clover on chest
        for a_deg in [0,90,180,270]:
            a=math.radians(a_deg)
            cx2=bx+math.cos(a)*6; cy2=by-8+math.sin(a)*6
            if on(cx2,cy2): draw.ellipse([int(cx2)-4,int(cy2)-4,int(cx2)+4,int(cy2)+4],fill=(60,160,60,int(180+pulse*60)))
        if on(bx,by-8): dot(bx,by-8,(40,120,40,220),2)
        seg(bx,by-2,bx,by+6,(40,120,40,180),2)
        # 3. Gold coin sparkles
        for i in range(6):
            a=(i/6)*math.pi*2+t_norm*math.pi*4
            gx=bx+math.cos(a)*bw//4; gy=by+math.sin(a)*15
            if on(gx,gy): dot(gx,gy,(255,220,0,int(160+pulse*80)),int(2+pulse))
        # 4. Rainbow on scythe
        rainbow=[(255,0,0),(255,165,0),(255,255,0),(0,200,0),(0,100,255),(150,0,255)]
        for j,rc in enumerate(rainbow):
            r2=6+j*2
            for a_deg in range(-70,70,12):
                a=math.radians(a_deg)
                rx2=sx+math.cos(a)*r2; ry2=sy-math.sin(a)*r2
                dot(rx2,ry2,rc+(int(140+pulse*60),),1)
        # 6. Shamrock trim on robe
        for i in range(5):
            tx=botx-botw//3+i*(botw*2//3//4); ty=boty+2
            if on(tx,ty):
                for a_deg in [0,90,180,270]:
                    a=math.radians(a_deg)
                    dot(tx+math.cos(a)*3,ty+math.sin(a)*3,(60,160,60,int(160+pulse*60)),2)
        # 7. Gold buckle on belt
        belt_y=by+20
        if on(bx,belt_y):
            draw.rectangle([bx-7,belt_y-4,bx+7,belt_y+4],fill=(200,160,0,220))
            draw.rectangle([bx-4,belt_y-2,bx+4,belt_y+2],fill=(255,220,0,220))
        # 8. Pot of gold on shoulder
        for sdx in [bw//2-12]:
            px2,py2=bx+sdx,by-20
            if on(px2,py2):
                draw.ellipse([px2-6,py2-4,px2+6,py2+4],fill=(40,30,20,200))
                for i in range(3):
                    dot(px2-3+i*3,py2-2,(255,200,0,int(180+pulse*60)),2)
        # 9. Leaf swirl on body
        for i in range(5):
            a=(i/5)*math.pi*2+t_norm*math.pi*2
            ox=bx+math.cos(a)*bw//3; oy=by+math.sin(a)*20
            if on(ox,oy): dot(ox,oy,(80,200,60,int(140+pulse*60)),int(2+pulse))
        # 10. Lucky star sparkles
        for i in range(4):
            a=(i/4)*math.pi*2+t_norm*math.pi*2
            sx2=bx+math.cos(a)*(bw//2-8); sy2=by+math.sin(a)*((y2-y1)//3)
            if on(sx2,sy2):
                dot(sx2,sy2,(255,220,0,int(160+pulse*80)),2)
                for a2 in [0,72,144,216,288]:
                    a3=math.radians(a2)
                    dot(sx2+math.cos(a3)*3,sy2+math.sin(a3)*3,(255,255,150,100),1)









def draw_eyes_and_face(draw, mask, hfx, hfy, theme, pulse, pulse2, t_norm, anim, W, H, eyes=None):
    """
    Draw prominent eyes at exact pixel positions.
    eyes = list of (x,y) tuples from FRAME_DATA.
    Falls back to estimated positions if not provided.
    """
    name = theme["name"]
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme["fl"]

    if not eyes:
        eyes = [(hfx - 40, hfy - 6), (hfx + 40, hfy - 6)]

    def fill(x, y, c, r):
        draw.ellipse([int(x)-r, int(y)-r, int(x)+r, int(y)+r], fill=c)

    def dot(x, y, c, r=1):
        xi,yi=int(x),int(y)
        if 0<=xi<W and 0<=yi<H:
            draw.ellipse([xi-r,yi-r,xi+r,yi+r], fill=c)

    for ex,ey in eyes:
        # ── OUTER GLOW (large, semi-transparent) ──────────────────────────
        glow_r = int(14 + pulse*4)
        draw.ellipse([int(ex)-glow_r,int(ey)-glow_r,int(ex)+glow_r,int(ey)+glow_r],
                     fill=pt+(int(40+pulse*40),))

        # ── BLACKOUT base ─────────────────────────────────────────────────
        fill(ex, ey, (0,0,0,255), 10)

        # ── THEME EYE DESIGN ──────────────────────────────────────────────
        if name in ("Inferno","Crimson","Lava","Magma","Demon"):
            zoom = int(5 + pulse*5)
            fill(ex,ey,(int(180+pulse*60),int(40+pulse*40),0,255), zoom+3)
            fill(ex,ey,(255,int(100+pulse2*80),0,255), zoom)
            fill(ex,ey,(0,0,0,255), max(1,zoom-3))
            dot(ex,ey,(255,220,50,255),2)
            for j in range(8):
                a=math.radians(j*45+t_norm*360)
                dot(ex+math.cos(a)*(zoom+4),ey+math.sin(a)*(zoom+4),pt+(int(180+pulse*60),),2)

        elif name in ("Void","Phantom","Abyssal","Shadow"):
            fill(ex,ey,(5,0,15,255),10)
            for j in range(12):
                a=(j/12)*math.pi*2+t_norm*math.pi*6
                r2=1+j*0.75
                dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(int(40+j*18),0,int(100+j*13),255),1)
            for j in range(10):
                a=(j/10)*math.pi*2+t_norm*math.pi*2
                dot(ex+math.cos(a)*8,ey+math.sin(a)*8,pt+(int(120+pulse*100),),2)
            dot(ex,ey,(255,255,255,255),2)

        elif name in ("Frost","Xmas","Arctic"):
            fill(ex,ey,(0,15,40,255),10)
            fill(ex,ey,(0,int(100+pulse*60),int(200+pulse*40),255),7)
            fill(ex,ey,(int(150+pulse*80),220,255,255),4)
            dot(ex,ey,(255,255,255,255),2)
            for j in range(6):
                a=math.radians(j*60+t_norm*30)
                for r2 in [6,9,12]:
                    dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(200,240,255,int(200-r2*10)),2)

        elif name in ("Toxic","Plague","Nature"):
            fill(ex,ey,(0,int(100+pulse*60),0,255),10)
            fill(ex,ey,(0,int(180+pulse*60),int(40+pulse*40),255),7)
            slit_w=max(1,int(1+pulse2*2))
            draw.rectangle([int(ex)-slit_w,int(ey)-8,int(ex)+slit_w,int(ey)+8],fill=(0,0,0,255))
            dot(ex,ey,(150,255,80,255),2)
            drip=int(t_norm*8)%7
            for d in range(drip):
                dot(ex,ey+10+d,(0,int(200-d*25),0,int(200-d*30)),2)

        elif name in ("Gold","Lunar"):
            fill(ex,ey,(60,40,0,255),10)
            cw=abs(int(math.cos(t_norm*math.pi*2)*8))
            if cw>0:
                draw.ellipse([int(ex)-cw,int(ey)-8,int(ex)+cw,int(ey)+8],fill=(int(200+pulse*40),int(150+pulse*40),0,255))
                draw.ellipse([int(ex)-max(1,cw-2),int(ey)-5,int(ex)+max(1,cw-2),int(ey)+5],fill=(255,int(210+pulse2*40),50,255))
            dot(ex,ey,(255,255,200,255),2)
            # Coin sparkle
            shine_a=t_norm*math.pi*2
            dot(ex+math.cos(shine_a)*4,ey+math.sin(shine_a)*4,(255,255,255,int(200+pulse*55)),2)

        elif name in ("Neon","Specter","Cyber"):
            fill(ex,ey,(0,0,5,255),10)
            scan_y=ey-6+int(t_norm*12)
            draw.rectangle([int(ex)-8,int(scan_y)-1,int(ex)+8,int(scan_y)+1],fill=(0,255,int(150+pulse*80),int(220+pulse*35)))
            fill(ex,ey,(0,int(180+pulse*60),int(120+pulse*40),180),4)
            dot(ex,ey,(0,255,200,255),2)
            for dx2,dy2 in [(-9,-9),(9,-9),(-9,9),(9,9)]:
                dot(ex+dx2,ey+dy2,(0,255,150,int(180+pulse*60)),2)

        elif name in ("Sakura","Valentines","Easter","Prism"):
            fill(ex,ey,(30,0,20,255),10)
            fill(ex,ey,(int(160+pulse*60),int(60+pulse*40),int(140+pulse*40),255),7)
            fill(ex,ey,(255,int(150+pulse*80),220,255),4)
            ray=int(7+pulse*4)
            for j in range(8):
                a=math.radians(j*45+t_norm*45)
                dot(ex+math.cos(a)*ray,ey+math.sin(a)*ray,(255,int(150+pulse*80),220,int(200+pulse*55)),2)
            dot(ex,ey,(255,255,255,255),2)

        elif name=="Halloween":
            fill(ex,ey,(0,0,0,255),10)
            draw.polygon([int(ex),int(ey)-7,int(ex)+7,int(ey)+5,int(ex)-7,int(ey)+5],fill=(255,int(100+pulse*80),0,255))
            dot(ex,ey,(255,int(180+pulse2*60),0,255),2)

        elif name=="Patrick":
            fill(ex,ey,(0,20,0,255),10)
            fill(ex,ey,(0,int(140+pulse*60),0,255),7)
            for j in range(4):
                a=math.radians(j*90+t_norm*90)
                dot(ex+math.cos(a)*5,ey+math.sin(a)*5,(int(60+pulse*60),int(200+pulse*55),int(40+pulse*40),int(220+pulse*35)),3)
            dot(ex,ey,(200,255,100,255),2)

        elif name in ("Galaxy","Celestial","Storm"):
            fill(ex,ey,(0,0,10,255),10)
            for j in range(14):
                t2=j/14; a=t2*math.pi*4+t_norm*math.pi*2; r2=t2*8
                dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(int(80+t2*120),int(40+t2*80),255,int(120+t2*100)),2)
            dot(ex,ey,(220,200,255,255),2)

        elif name in ("Ocean",):
            fill(ex,ey,(0,10,30,255),10)
            for j in range(3):
                phase=(t_norm+j/3)%1.0; r2=int(phase*10); alpha=int(220*(1-phase))
                if r2>0: draw.ellipse([int(ex)-r2,int(ey)-r2,int(ex)+r2,int(ey)+r2],outline=(0,int(150+pulse*80),255,alpha),width=2)
            dot(ex,ey,(100,220,255,255),3)

        else:
            fill(ex,ey,(0,0,0,255),10)
            fill(ex,ey,pt+(220,),7)
            fill(ex,ey,hi+(240,),4)
            dot(ex,ey,(255,255,255,255),2)

    # ── FACE MARKINGS ─────────────────────────────────────────────────────
    for dx,sign in [(-22,-1),(22,1)]:
        mx,my = hfx+dx, hfy+2
        if 0<=int(mx)<W and 0<=int(my)<H:
            for i in range(3):
                dot(mx,my-5+i*5,ac+(int(180+pulse*60),),2)
            dot(mx,my+8,fl+(int(160+pulse2*80),),2)

    if 0<=int(hfx)<W and 0<=int(hfy-14)<H:
        draw.ellipse([int(hfx)-5,int(hfy)-18,int(hfx)+5,int(hfy)-8],fill=pt+(int(200+pulse*55),))
        dot(hfx,hfy-13,(255,255,255,int(220+pulse*35)),2)

    shimmer_x = hfx - 18 + int(t_norm*36)
    face_c = tuple(int(theme["s"][j]*0.6+theme["ac"][j]*0.4) for j in range(3))
    for dy in range(-10,14):
        if 0<=int(shimmer_x)<W and 0<=int(hfy+dy)<H:
            dot(shimmer_x,hfy+dy,face_c+(int(45+pulse*35),),1)
    """
    Draw prominent eyes at the REAL face position (hfx, hfy).
    Eyes are large (r=8), fully opaque, unique per theme.
    Also draws face markings.
    """
    name = theme["name"]
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme["fl"]

    # Real eye positions relative to head face center
    # Face is ~62px wide, eyes are ~20px apart from center
    eyes = [(hfx - 12, hfy - 5), (hfx + 12, hfy - 5)]

    def fill(x, y, c, r):
        draw.ellipse([int(x)-r, int(y)-r, int(x)+r, int(y)+r], fill=c)

    def dot(x, y, c, r=1):
        xi,yi=int(x),int(y)
        if 0<=xi<W and 0<=yi<H:
            draw.ellipse([xi-r,yi-r,xi+r,yi+r], fill=c)

    # ── Blackout both eyes completely ─────────────────────────────────────
    for ex,ey in eyes:
        fill(ex, ey, (0,0,0,255), 9)

    # ── Draw theme eye ─────────────────────────────────────────────────────
    for ex,ey in eyes:
        if name in ("Inferno","Crimson","Lava","Magma","Demon"):
            # ZOOMING FLAME EYE
            zoom = int(4 + pulse*5)
            fill(ex,ey,(int(180+pulse*60),int(40+pulse*40),0,255), zoom+2)
            fill(ex,ey,(255,int(100+pulse2*80),0,255), zoom)
            fill(ex,ey,(0,0,0,255), max(1,zoom-3))
            dot(ex,ey,(255,220,50,255),2)
            for j in range(6):
                a=math.radians(j*60+t_norm*360)
                dot(ex+math.cos(a)*(zoom+2),ey+math.sin(a)*(zoom+2),pt+(int(160+pulse*80),),2)

        elif name in ("Void","Phantom","Abyssal","Shadow"):
            # TORNADO VORTEX EYE
            fill(ex,ey,(5,0,15,255),9)
            for j in range(10):
                a=(j/10)*math.pi*2+t_norm*math.pi*6
                r2=1+j*0.8
                dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(int(40+j*20),0,int(100+j*15),255),1)
            for j in range(8):
                a=(j/8)*math.pi*2+t_norm*math.pi*2
                dot(ex+math.cos(a)*7,ey+math.sin(a)*7,pt+(int(100+pulse*120),),2)
            dot(ex,ey,(255,255,255,255),2)

        elif name in ("Frost","Xmas","Arctic"):
            # CRYSTAL SNOWFLAKE EYE
            fill(ex,ey,(0,15,40,255),9)
            fill(ex,ey,(0,int(100+pulse*60),int(200+pulse*40),255),6)
            fill(ex,ey,(int(150+pulse*80),220,255,255),3)
            dot(ex,ey,(255,255,255,255),2)
            for j in range(6):
                a=math.radians(j*60+t_norm*30)
                for r2 in [5,8]:
                    dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(200,240,255,int(180+pulse*60)),2)

        elif name in ("Toxic","Plague","Nature"):
            # SLIT PUPIL EYE
            fill(ex,ey,(0,int(100+pulse*60),0,255),9)
            fill(ex,ey,(0,int(180+pulse*60),int(40+pulse*40),255),6)
            slit_w=max(1,int(1+pulse2*2))
            draw.rectangle([int(ex)-slit_w,int(ey)-7,int(ex)+slit_w,int(ey)+7],fill=(0,0,0,255))
            dot(ex,ey,(150,255,80,255),2)
            # Toxic drip
            drip=int(t_norm*8)%6
            for d in range(drip):
                dot(ex,ey+8+d,(0,int(200-d*25),0,int(200-d*40)),2)

        elif name in ("Gold","Lunar"):
            # SPINNING COIN EYE
            fill(ex,ey,(60,40,0,255),9)
            cw=abs(int(math.cos(t_norm*math.pi*2)*7))
            if cw>0:
                draw.ellipse([int(ex)-cw,int(ey)-7,int(ex)+cw,int(ey)+7],fill=(int(200+pulse*40),int(150+pulse*40),0,255))
                draw.ellipse([int(ex)-max(1,cw-2),int(ey)-4,int(ex)+max(1,cw-2),int(ey)+4],fill=(255,int(210+pulse2*40),50,255))
            dot(ex,ey,(255,255,200,255),2)

        elif name in ("Neon","Specter","Cyber"):
            # SCAN LINE EYE
            fill(ex,ey,(0,0,5,255),9)
            scan_y=ey-5+int(t_norm*10)
            draw.rectangle([int(ex)-7,int(scan_y)-1,int(ex)+7,int(scan_y)+1],fill=(0,255,int(150+pulse*80),int(220+pulse*35)))
            fill(ex,ey,(0,int(180+pulse*60),int(120+pulse*40),180),3)
            dot(ex,ey,(0,255,200,255),2)
            for dx2,dy2 in [(-7,-7),(7,-7),(-7,7),(7,7)]:
                dot(ex+dx2,ey+dy2,(0,255,150,int(160+pulse*60)),2)

        elif name in ("Sakura","Valentines","Easter","Prism"):
            # STAR BURST EYE
            fill(ex,ey,(30,0,20,255),9)
            fill(ex,ey,(int(160+pulse*60),int(60+pulse*40),int(140+pulse*40),255),6)
            fill(ex,ey,(255,int(150+pulse*80),220,255),3)
            ray=int(5+pulse*4)
            for j in range(8):
                a=math.radians(j*45+t_norm*45)
                dot(ex+math.cos(a)*ray,ey+math.sin(a)*ray,(255,int(150+pulse*80),220,int(200+pulse*55)),2)
            dot(ex,ey,(255,255,255,255),2)

        elif name=="Halloween":
            # JACK-O-LANTERN TRIANGLE EYE
            fill(ex,ey,(0,0,0,255),9)
            draw.polygon([int(ex),int(ey)-6,int(ex)+6,int(ey)+4,int(ex)-6,int(ey)+4],fill=(255,int(100+pulse*80),0,255))
            dot(ex,ey,(255,int(180+pulse2*60),0,255),2)

        elif name=="Patrick":
            # CLOVER EYE
            fill(ex,ey,(0,20,0,255),9)
            fill(ex,ey,(0,int(140+pulse*60),0,255),6)
            for j in range(4):
                a=math.radians(j*90+t_norm*90)
                dot(ex+math.cos(a)*4,ey+math.sin(a)*4,(int(60+pulse*60),int(200+pulse*55),int(40+pulse*40),int(200+pulse*55)),3)
            dot(ex,ey,(200,255,100,255),2)

        elif name in ("Galaxy","Celestial","Storm"):
            # GALAXY SWIRL EYE
            fill(ex,ey,(0,0,10,255),9)
            for j in range(12):
                t2=j/12; a=t2*math.pi*4+t_norm*math.pi*2; r2=t2*7
                dot(ex+math.cos(a)*r2,ey+math.sin(a)*r2,(int(80+t2*120),int(40+t2*80),255,int(120+t2*100)),2)
            dot(ex,ey,(220,200,255,255),2)

        elif name in ("Ocean",):
            # RIPPLE EYE
            fill(ex,ey,(0,10,30,255),9)
            for j in range(3):
                phase=(t_norm+j/3)%1.0; r2=int(phase*8); alpha=int(220*(1-phase))
                if r2>0: draw.ellipse([int(ex)-r2,int(ey)-r2,int(ex)+r2,int(ey)+r2],outline=(0,int(150+pulse*80),255,alpha),width=2)
            dot(ex,ey,(100,220,255,255),3)

        else:
            fill(ex,ey,(0,0,0,255),9)
            fill(ex,ey,pt+(220,),6)
            fill(ex,ey,hi+(240,),3)
            dot(ex,ey,(255,255,255,255),2)

    # ── FACE MARKINGS — prominent war paint ───────────────────────────────
    # Cheek marks
    for dx,sign in [(-18,-1),(18,1)]:
        mx,my = hfx+dx, hfy+2
        if 0<=int(mx)<W and 0<=int(my)<H:
            for i in range(3):
                dot(mx,my-4+i*4,ac+(int(160+pulse*80),),2)
            dot(mx,my+6,fl+(int(140+pulse2*80),),2)

    # Forehead mark
    if 0<=int(hfx)<W and 0<=int(hfy-12)<H:
        draw.ellipse([int(hfx)-4,int(hfy)-16,int(hfx)+4,int(hfy)-8],fill=pt+(int(180+pulse*60),))
        dot(hfx,hfy-12,(255,255,255,int(200+pulse*55)),2)

    # Animated shimmer across face
    shimmer_x = hfx - 15 + int(t_norm*30)
    face_c = tuple(int(theme["s"][j]*0.6+theme["ac"][j]*0.4) for j in range(3))
    for dy in range(-8,12):
        if 0<=int(shimmer_x)<W and 0<=int(hfy+dy)<H:
            dot(shimmer_x,hfy+dy,face_c+(int(40+pulse*30),),1)


def add_cosmetics(img, mask, fd, theme, frame_idx, total, anim):
    draw = ImageDraw.Draw(img)
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme["fl"]
    t_norm=frame_idx/max(total-1,1)
    pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
    pulse2=0.5+0.5*math.sin(t_norm*math.pi*4)
    W,H=img.width,img.height
    fx,fy=fd["face"]; hfx,hfy=fd.get("hface",fd["face"])
    htx,hty=fd["head_top"]; hw=fd["head_w"]
    bx,by=fd["body"]; bw=fd["body_w"]
    botx,boty=fd["bot"]; botw=fd["bot_w"]
    sx,sy=fd["scythe"]; x1,y1,x2,y2=fd["bbox"]

    def on(x,y): xi,yi=int(x),int(y); return 0<=xi<W and 0<=yi<H and mask[yi,xi]
    def dot(x,y,c,r=1):
        xi,yi=int(x),int(y)
        if 0<=xi<W and 0<=yi<H: draw.ellipse([xi-r,yi-r,xi+r,yi+r],fill=c)
    def soft_dot(x,y,c,r=2):
        xi,yi=int(x),int(y)
        if not(0<=xi<W and 0<=yi<H): return
        cr,cg,cb=c[:3]; ca=c[3] if len(c)>3 else 255
        for lr,la in [(r+2,0.25),(r,0.6),(max(1,r-1),1.0)]:
            draw.ellipse([xi-lr,yi-lr,xi+lr,yi+lr],fill=(cr,cg,cb,int(ca*la)))
    def line_on(x0,y0,x1_,y1_,color,w=2):
        steps=max(abs(int(x1_)-int(x0)),abs(int(y1_)-int(y0)),1)*2
        for s in range(steps+1):
            t=s/steps; px_=x0+(x1_-x0)*t; py_=y0+(y1_-y0)*t
            if on(px_,py_): dot(px_,py_,color,w)

    draw_head_anim(draw,mask,htx,hty,hw,theme["head_anim"],ac,hi,pt,fl,frame_idx,total,W,H)
    draw_theme_extras(img,mask,fd,theme,frame_idx,total,anim)
    draw_eyes_and_face(draw,mask,hfx,hfy,theme,pulse,pulse2,t_norm,anim,W,H,eyes=fd.get("eyes"))

    # Collar
    collar_y=hfy+18
    line_on(hfx-10,collar_y,hfx,collar_y+12,hi+(210,),2)
    line_on(hfx,collar_y+12,hfx+10,collar_y,hi+(210,),2)

    # Chest sigil
    for a_deg in range(0,360,8):
        a=math.radians(a_deg+t_norm*60)
        rx=bx+math.cos(a)*18; ry=by-5+math.sin(a)*12
        if on(rx,ry): soft_dot(rx,ry,ac+(int(120+pulse*100),),2)
    for j in range(3):
        a=math.radians(j*120+t_norm*180)
        tx=bx+math.cos(a)*10; ty=by-5+math.sin(a)*7
        if on(tx,ty): soft_dot(tx,ty,hi+(int(180+pulse*60),),3)
    if on(bx,by-5):
        draw.ellipse([bx-5,by-10,bx+5,by],fill=pt+(int(200+pulse*55),))
        draw.ellipse([bx-2,by-8,bx+2,by-2],fill=(255,255,255,int(200+pulse*55)))

    draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,theme["body_anim"],ac,hi,pt,fl,frame_idx,total,W,H)

    # Shoulder pads
    for sdx in [-bw//2+8,bw//2-8]:
        spx,spy=bx+sdx,by-20
        if on(spx,spy):
            draw.ellipse([spx-7,spy-5,spx+7,spy+5],fill=ac+(int(130+pulse*80),))
            draw.ellipse([spx-4,spy-3,spx+4,spy+3],fill=hi+(220,))
            draw.polygon([spx,spy-int(5+pulse*5),spx+4,spy-2,spx-4,spy-2],fill=fl+(int(180+pulse*60),))

    if anim=="flying":
        for i in range(8):
            angle=math.radians(-40+i*10+pulse*20)
            for side in [-1,1]:
                wx=bx+side*(bw//3+math.cos(angle)*int(18+pulse*12)); wy=by-8+math.sin(angle)*14
                if on(wx,wy): soft_dot(wx,wy,hi+(int(80+pulse*80),),2)

    # Belt
    belt_y=by+20
    for beltx in range(bx-bw//3,bx+bw//3,4):
        if on(beltx,belt_y): dot(beltx,belt_y,ac+(160,),2)
    if on(bx,belt_y):
        draw.rectangle([bx-6,belt_y-4,bx+6,belt_y+4],fill=hi+(int(160+pulse*80),))
        draw.rectangle([bx-3,belt_y-2,bx+3,belt_y+2],fill=ac+(255,))

    # Robe trim
    for i in range(16):
        tx=botx-botw//2+int(i*(botw/15)); wave=int(5*math.sin(i*0.7+t_norm*math.pi*2))
        if on(tx,boty+wave): soft_dot(tx,boty+wave,fl+(int(140+pulse*80),),2)
        if on(tx,boty+8+wave): dot(tx,boty+8+wave,ac+(int(100+pulse*60),),2)

    # Robe sparks
    for i in range(5):
        rise_t=(t_norm+i/5)%1.0; rise=int(math.sin(rise_t*math.pi)*35)
        spark_x=botx-botw//3+int(i*(botw*2/3/4)); spark_y=boty-rise
        if on(spark_x,spark_y): soft_dot(spark_x,spark_y,pt+(int(200*math.sin(rise_t*math.pi)),),2)

    draw_weapon(draw,mask,sx,sy,theme["weapon"],ac,hi,pt,frame_idx,total,W,H)

    # Scythe orbit
    for i in range(4):
        angle=(i/4)*math.pi*2+t_norm*math.pi*2
        px2=sx+math.cos(angle)*13; py2=sy+math.sin(angle)*13
        if on(px2,py2): soft_dot(px2,py2,pt+(int(140+80*math.sin(angle)),),2)

    # Chain glow
    chain_cx=x2-20
    for i in range(6):
        cy2=(y1+y2)//2-30+i*12
        phase_i=0.5+0.5*math.sin(t_norm*math.pi*4+i*0.5)
        if on(chain_cx,cy2): soft_dot(chain_cx,cy2,ac+(int(80+phase_i*140),),int(2+phase_i))

    # Heartbeat rings
    for ring_idx in range(2):
        phase=(t_norm*2+ring_idx*0.5)%1.0
        ease=phase/0.15 if phase<0.15 else max(0,1-(phase-0.15)/0.85)
        ring_r=int(ease*bw*0.38); alpha=int(180*ease)
        if alpha<10: continue
        for a_deg in range(0,360,10):
            a=math.radians(a_deg); rx=bx+math.cos(a)*ring_r; ry=by+math.sin(a)*ring_r*0.5
            if on(rx,ry): dot(rx,ry,pt+(alpha,),2)

    # Energy vortex
    for i in range(12):
        spiral_t=(t_norm+i/12)%1.0; angle=spiral_t*math.pi*4; radius=(1-spiral_t)*bw//3
        vx=bx+math.cos(angle)*radius; vy=by+math.sin(angle)*radius*0.5
        if on(vx,vy): soft_dot(vx,vy,hi+(int(200*spiral_t),),max(1,int(2*spiral_t)))

    # Ground glow
    for i in range(9):
        gx=botx-20+i*5; gy=y2-3
        wave=0.5+0.5*math.sin(t_norm*math.pi*2+i*0.5)
        if on(gx,gy): soft_dot(gx,gy,ac+(int(50+wave*130),),int(1+wave*1.5))

def draw_shape_fx(img, mask, fd, theme, frame_idx, total, border_style=None):
    """Draw border effect. border_style overrides theme style if provided."""
    draw = ImageDraw.Draw(img)
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme.get("fl",(200,200,200))
    t_norm=frame_idx/max(total-1,1)
    pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
    W,H=img.width,img.height
    style=border_style or theme.get("style","robe")
    edge=[]
    for row in range(1,H-1):
        for col in range(1,W-1):
            if mask[row,col] and not(mask[row-1,col] and mask[row+1,col] and mask[row,col-1] and mask[row,col+1]):
                edge.append((col,row))
    if not edge: return
    n=len(edge)

    def ep(idx): return edge[int(idx%1.0*n)]

    for idx,(ex,ey) in enumerate(edge):
        pos=idx/n
        wave=math.sin(pos*math.pi*6+t_norm*math.pi*4)
        wave2=math.sin(pos*math.pi*10+t_norm*math.pi*2)

        if style in ("armor","ninja"):
            t_c=(wave+1)/2
            r=int(ac[0]*(1-t_c)+hi[0]*t_c); g=int(ac[1]*(1-t_c)+hi[1]*t_c); b=int(ac[2]*(1-t_c)+hi[2]*t_c)
            draw.point((ex,ey),fill=(r,g,b,int(160+80*abs(wave))))
            if wave>0.7: draw.point((ex,ey),fill=(255,255,255,int(wave*200)))

        elif style in ("royal","suit"):
            t_c=(wave+1)/2
            r=int(fl[0]*(1-t_c)+hi[0]*t_c); g=int(fl[1]*(1-t_c)+hi[1]*t_c); b=int(fl[2]*(1-t_c)+hi[2]*t_c)
            draw.point((ex,ey),fill=(r,g,b,int(140+100*abs(wave))))
            if int(pos*n)%20==0: draw.ellipse([ex-1,ey-1,ex+1,ey+1],fill=(255,255,255,int(180+pulse*60)))

        elif style == "fire_border":
            # Flickering fire edge
            flicker=math.sin(pos*math.pi*8+t_norm*math.pi*6)
            r=255; g=int(80+120*abs(flicker)); b=0
            draw.point((ex,ey),fill=(r,g,b,int(180+60*abs(flicker))))
            if flicker>0.6:
                draw.ellipse([ex-1,ey-2,ex+1,ey],fill=(255,220,0,int(flicker*200)))

        elif style == "ice_border":
            # Crystalline ice edge with sparkles
            t_c=(wave+1)/2
            r=int(140+80*t_c); g=int(200+40*t_c); b=255
            draw.point((ex,ey),fill=(r,g,b,int(160+80*abs(wave))))
            if int(pos*n)%15==0:
                draw.ellipse([ex-2,ey-2,ex+2,ey+2],fill=(255,255,255,int(180+pulse*60)))

        elif style == "void_border":
            # Dark void with purple sparks
            spark=math.sin(pos*math.pi*12+t_norm*math.pi*8)
            r=int(40+80*abs(spark)); g=0; b=int(80+120*abs(spark))
            draw.point((ex,ey),fill=(r,g,b,int(140+100*abs(spark))))
            if spark>0.8: draw.ellipse([ex-1,ey-1,ex+1,ey+1],fill=(200,100,255,int(spark*220)))

        elif style == "gold_border":
            # Shimmering gold with jewel nodes
            t_c=(wave+1)/2
            r=int(200+40*t_c); g=int(150+80*t_c); b=int(20*t_c)
            draw.point((ex,ey),fill=(r,g,b,int(180+60*abs(wave))))
            if int(pos*n)%25==0:
                draw.ellipse([ex-2,ey-2,ex+2,ey+2],fill=(255,220,50,int(200+pulse*55)))

        elif style == "rainbow_border":
            # Full rainbow cycling around edge
            hue_pos=(pos+t_norm*0.5)%1.0
            import colorsys
            r2,g2,b2=colorsys.hsv_to_rgb(hue_pos,1.0,1.0)
            draw.point((ex,ey),fill=(int(r2*255),int(g2*255),int(b2*255),int(180+60*abs(wave))))

        elif style == "electric_border":
            # Electric blue with random zap nodes
            zap=math.sin(pos*math.pi*14+t_norm*math.pi*10)
            r=int(20+40*abs(zap)); g=int(100+100*abs(zap)); b=255
            draw.point((ex,ey),fill=(r,g,b,int(160+80*abs(zap))))
            if zap>0.85 and int(pos*n)%8==0:
                draw.ellipse([ex-2,ey-2,ex+2,ey+2],fill=(255,255,255,220))

        elif style == "nature_border":
            # Green vine with flower nodes
            t_c=(wave+1)/2
            r=int(20+60*t_c); g=int(120+100*t_c); b=int(20+40*t_c)
            draw.point((ex,ey),fill=(r,g,b,int(160+80*abs(wave))))
            if int(pos*n)%30==0:
                draw.ellipse([ex-2,ey-2,ex+2,ey+2],fill=(255,150,200,int(180+pulse*60)))

        else:  # default robe/tattered
            r=min(255,int(ac[0]*(abs(wave)+1)/2+pt[0]*(abs(wave2)+1)/2))
            g=min(255,int(ac[1]*(abs(wave)+1)/2+pt[1]*(abs(wave2)+1)/2))
            b=min(255,int(ac[2]*(abs(wave)+1)/2+pt[2]*(abs(wave2)+1)/2))
            draw.point((ex,ey),fill=(r,g,b,int(120+100*abs(wave))))

    # Traveling nodes on edge
    for i in range(8):
        node_pos=(t_norm+i/8)%1.0
        ex,ey=edge[int(node_pos*n)]
        draw.ellipse([ex-2,ey-2,ex+2,ey+2],fill=hi+(int(180+60*math.sin(t_norm*math.pi*2+i)),))

    # ── WIDE / HIGHLIGHTED BORDER STYLES ──────────────────────────────────
    if style == "flaming_wide":
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; flicker=math.sin(pos*math.pi*8+t_norm*math.pi*6)
            for w in range(4):
                nx,ny=ex+random.randint(-w,w),ey+random.randint(-w,w)
                if 0<=nx<W and 0<=ny<H:
                    draw.point((nx,ny),fill=(255,int(60+120*abs(flicker)),0,int(220-w*40)))
            if flicker>0.5: draw.ellipse([ex-3,ey-5,ex+3,ey+1],fill=(255,220,0,int(flicker*180)))
    elif style == "electric_wide":
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; zap=math.sin(pos*math.pi*14+t_norm*math.pi*10)
            for w in range(3):
                nx,ny=ex+random.randint(-w,w),ey+random.randint(-w,w)
                if 0<=nx<W and 0<=ny<H:
                    draw.point((nx,ny),fill=(int(20+40*abs(zap)),int(100+80*abs(zap)),int(180+60*abs(zap)),int(200-w*50)))
            if zap>0.8: draw.ellipse([ex-3,ey-3,ex+3,ey+3],fill=(255,255,255,int(zap*200)))
    elif style == "gold_wide":
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; wave3=math.sin(pos*math.pi*6+t_norm*math.pi*4)
            for w in range(4):
                nx,ny=ex+random.randint(-w,w),ey+random.randint(-w,w)
                if 0<=nx<W and 0<=ny<H:
                    t_c=(wave3+1)/2
                    draw.point((nx,ny),fill=(int(200+40*t_c),int(150+80*t_c),int(20*t_c),int(200-w*40)))
            if int(pos*n)%18==0: draw.ellipse([ex-4,ey-4,ex+4,ey+4],fill=(255,220,50,int(200+pulse*55)))
    elif style == "rainbow_wide":
        import colorsys
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; hue=(pos+t_norm*0.5)%1.0
            r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
            for w in range(3):
                nx,ny=ex+random.randint(-w,w),ey+random.randint(-w,w)
                if 0<=nx<W and 0<=ny<H:
                    draw.point((nx,ny),fill=(int(r2*255),int(g2*255),int(b2*255),int(200-w*50)))
    elif style == "chaos_wide":
        import colorsys
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; hue=(pos*3+t_norm*2)%1.0
            r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
            for w in range(4):
                nx,ny=ex+random.randint(-w-1,w+1),ey+random.randint(-w-1,w+1)
                if 0<=nx<W and 0<=ny<H:
                    draw.point((nx,ny),fill=(int(r2*255),int(g2*255),int(b2*255),int(180-w*30)))

    elif style == "plasma_border":
        import colorsys
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; hue=(pos*2+t_norm)%1.0
            r2,g2,b2=colorsys.hsv_to_rgb(hue,0.8,1.0)
            wave3=math.sin(pos*math.pi*8+t_norm*math.pi*6)
            draw.point((ex,ey),fill=(int(r2*255),int(g2*255),int(b2*255),int(160+80*abs(wave3))))
            if wave3>0.6: draw.ellipse([ex-1,ey-1,ex+1,ey+1],fill=(255,255,255,int(wave3*180)))

    elif style == "plasma_wide":
        import colorsys
        for idx,(ex,ey) in enumerate(edge):
            pos=idx/n; hue=(pos*2+t_norm)%1.0
            r2,g2,b2=colorsys.hsv_to_rgb(hue,0.8,1.0)
            for w in range(5):
                nx,ny=ex+random.randint(-w,w),ey+random.randint(-w,w)
                if 0<=nx<W and 0<=ny<H:
                    draw.point((nx,ny),fill=(int(r2*255),int(g2*255),int(b2*255),int(200-w*35)))
            if int(pos*n)%12==0:
                draw.ellipse([ex-4,ey-4,ex+4,ey+4],fill=(255,255,255,int(180+pulse*60)))


def draw_special_fx(img, mask, fd, theme, frame_idx, total, special_key):
    """Per-theme special FX always rendered."""
    draw = ImageDraw.Draw(img)
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme.get("fl",(200,200,200))
    t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
    W,H=img.width,img.height
    bx,by=fd["body"]; bw=fd["body_w"]
    htx,hty=fd["head_top"]
    def on(x,y): xi,yi=int(x),int(y); return 0<=xi<W and 0<=yi<H and mask[yi,xi]
    def dot(x,y,c,r=1):
        xi,yi=int(x),int(y)
        if 0<=xi<W and 0<=yi<H: draw.ellipse([xi-r,yi-r,xi+r,yi+r],fill=c)
    if special_key=="sparkle_trail":
        for i in range(12):
            a=(i/12)*math.pi*2+t_norm*math.pi*3
            ox=bx+math.cos(a)*(bw//2); oy=by+math.sin(a)*25
            if on(ox,oy): dot(ox,oy,(255,200,255,int(160+pulse*80)),int(2+pulse))
    elif special_key=="star_burst_fx":
        for i in range(5):
            a=(i/5)*math.pi*2+t_norm*math.pi*2
            for r2 in [8,14,20]:
                ox=htx+math.cos(a)*r2; oy=hty-5+math.sin(a)*r2*0.4
                dot(ox,oy,hi+(int(120+pulse*100),),int(2+pulse*(1-r2/25)))
    elif special_key=="gadget_glow":
        if on(bx,by-5):
            draw.ellipse([bx-10,by-15,bx+10,by+5],fill=(0,180,255,int(80+pulse*60)))
            draw.ellipse([bx-6,by-11,bx+6,by+1],fill=(0,220,255,int(120+pulse*80)))
            dot(bx,by-5,(255,255,255,int(200+pulse*55)),2)
    elif special_key=="pocket_sparkle":
        for i in range(6):
            a=(i/6)*math.pi*2+t_norm*math.pi*4
            ox=bx+math.cos(a)*12; oy=by-5+math.sin(a)*8
            dot(ox,oy,(0,220,255,int(140+pulse*80)),int(1+pulse))
    elif special_key=="troll_grin":
        fx,fy=fd["face"]
        for dx2 in range(-8,9,2):
            if on(fx+dx2,fy+8): dot(fx+dx2,fy+8,(255,255,255,int(180+pulse*60)),1)
        for dx2 in [-6,-3,0,3,6]:
            if on(fx+dx2,fy+10): dot(fx+dx2,fy+10,(0,0,0,220),1)
    elif special_key=="chaos_sparks":
        import colorsys
        for i in range(8):
            a=(i/8)*math.pi*2+t_norm*math.pi*5
            hue=(t_norm+i/8)%1.0; r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
            ox=bx+math.cos(a)*bw//3; oy=by+math.sin(a)*20
            if on(ox,oy): dot(ox,oy,(int(r2*255),int(g2*255),int(b2*255),int(160+pulse*80)),int(2+pulse))
    elif special_key=="freestyle_trail":
        import colorsys
        for i in range(16):
            a=(i/16)*math.pi*2+t_norm*math.pi*2
            hue=(i/16+t_norm*0.3)%1.0; r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
            ox=bx+math.cos(a)*(bw//3+i%4*3); oy=by+math.sin(a)*22
            if on(ox,oy): dot(ox,oy,(int(r2*255),int(g2*255),int(b2*255),int(140+pulse*80)),2)
    elif special_key=="color_burst":
        import colorsys
        for i in range(6):
            phase=(t_norm+i/6)%1.0; r2=int(phase*bw//2)
            hue=(i/6+t_norm*0.5)%1.0; rc,gc,bc=colorsys.hsv_to_rgb(hue,1.0,1.0)
            alpha=int(180*math.sin(phase*math.pi))
            if alpha>20:
                for a_deg in range(0,360,20):
                    a=math.radians(a_deg)
                    ox=bx+math.cos(a)*r2; oy=by+math.sin(a)*r2*0.5
                    if on(ox,oy): dot(ox,oy,(int(rc*255),int(gc*255),int(bc*255),alpha),1)
    elif special_key=="epic_aura":
        for i in range(3):
            phase=(t_norm*2+i/3)%1.0; ease=max(0,math.sin(phase*math.pi))
            ring_r=int(ease*bw*0.45); alpha=int(200*ease)
            if alpha>20:
                for a_deg in range(0,360,8):
                    a=math.radians(a_deg)
                    ox=bx+math.cos(a)*ring_r; oy=by+math.sin(a)*ring_r*0.5
                    if on(ox,oy): dot(ox,oy,ac+(alpha,),2)
    elif special_key=="power_surge":
        for i in range(4):
            a=(i/4)*math.pi*2+t_norm*math.pi*4
            for r2 in [10,18,26]:
                ox=bx+math.cos(a)*r2; oy=by+math.sin(a)*r2*0.5
                if on(ox,oy): dot(ox,oy,hi+(int(100+pulse*120*(1-r2/30)),),int(2-r2//20))
    elif special_key=="legendary_crown":
        for i in range(8):
            a=math.radians(i*45+t_norm*360)
            for r2 in [14,20]:
                ox=htx+math.cos(a)*r2; oy=hty-3+math.sin(a)*r2*0.35
                dot(ox,oy,(255,220,0,int(160+pulse*80*(1-r2/25))),int(2+pulse*(1-r2/25)))
    elif special_key=="void_rift":
        # Void rift tear on chest
        rift_w=int(8+pulse*6); rift_h=int(14+pulse*4)
        draw.ellipse([bx-rift_w,by-10-rift_h,bx+rift_w,by-10+rift_h],fill=(0,0,0,220))
        for i in range(8):
            a=math.radians(i*45+t_norm*180)
            dot(bx+math.cos(a)*(rift_w+2),by-10+math.sin(a)*(rift_h+2)*0.5,pt+(int(160+pulse*80),),2)
        dot(bx,by-10,(180,0,255,int(200+pulse*55)),3)

    elif special_key=="solar_flare":
        for i in range(8):
            a=math.radians(i*45+t_norm*360)
            ray_len=int(15+pulse*12)
            for r2 in range(0,ray_len,2):
                ox=bx+math.cos(a)*r2; oy=by-5+math.sin(a)*r2*0.4
                alpha=int(220*(1-r2/ray_len))
                if on(ox,oy): dot(ox,oy,(255,int(180+40*(1-r2/ray_len)),0,alpha),int(2*(1-r2/ray_len))+1)
        dot(bx,by-5,(255,255,200,int(220+pulse*35)),int(4+pulse))

    elif special_key=="divine_rays":
        for i in range(6):
            a=math.radians(i*60+t_norm*30); ray_len=int(20+pulse*10)
            for r2 in range(0,ray_len,3):
                ox=htx+math.cos(a)*r2; oy=hty-5+math.sin(a)*r2*0.3
                dot(ox,oy,hi+(int(200*(1-r2/ray_len)),),1)


def draw_overlay_group(img, mask, fd, theme, frame_idx, total, anim, group):
    """Draw only one cosmetic group onto a transparent image."""
    draw = ImageDraw.Draw(img)
    ac=theme["ac"]; hi=theme["hi"]; pt=theme["pt"]; fl=theme["fl"]
    t_norm=frame_idx/max(total-1,1)
    pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
    pulse2=0.5+0.5*math.sin(t_norm*math.pi*4)
    W,H=img.width,img.height
    fx,fy=fd["face"]; hfx,hfy=fd.get("hface",fd["face"]); htx,hty=fd["head_top"]; hw=fd["head_w"]
    bx,by=fd["body"]; bw=fd["body_w"]
    botx,boty=fd["bot"]; botw=fd["bot_w"]
    sx,sy=fd["scythe"]; x1,y1,x2,y2=fd["bbox"]

    def on(x,y): xi,yi=int(x),int(y); return 0<=xi<W and 0<=yi<H and mask[yi,xi]
    def dot(x,y,c,r=1):
        xi,yi=int(x),int(y)
        if 0<=xi<W and 0<=yi<H: draw.ellipse([xi-r,yi-r,xi+r,yi+r],fill=c)
    def soft_dot(x,y,c,r=2):
        xi,yi=int(x),int(y)
        if not(0<=xi<W and 0<=yi<H): return
        cr,cg,cb=c[:3]; ca=c[3] if len(c)>3 else 255
        for lr,la in [(r+2,0.25),(r,0.6),(max(1,r-1),1.0)]:
            draw.ellipse([xi-lr,yi-lr,xi+lr,yi+lr],fill=(cr,cg,cb,int(ca*la)))

    if group == "head":
        draw_head_anim(draw,mask,htx,hty,hw,theme["head_anim"],ac,hi,pt,fl,frame_idx,total,W,H)
        # Crown collar
        collar_y=fy+18
        for pts in [((fx-10,collar_y),(fx,collar_y+12)),((fx,collar_y+12),(fx+10,collar_y))]:
            (x0,y0),(x1_,y1_)=pts
            steps=max(abs(int(x1_)-int(x0)),abs(int(y1_)-int(y0)),1)*2
            for s in range(steps+1):
                t=s/steps; px_=x0+(x1_-x0)*t; py_=y0+(y1_-y0)*t
                if on(px_,py_): dot(px_,py_,hi+(210,),2)

    elif group == "eyes":
        draw_eyes_and_face(draw,mask,hfx,hfy,theme,pulse,pulse2,t_norm,anim,W,H,eyes=fd.get("eyes"))

    elif group == "body":
        draw_theme_extras(img,mask,fd,theme,frame_idx,total,anim)
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,theme["body_anim"],ac,hi,pt,fl,frame_idx,total,W,H)
        # ── CHEST SIGIL — large glowing symbol on chest ───────────────────
        # Outer ring
        for a_deg in range(0,360,8):
            a=math.radians(a_deg+t_norm*60)
            rx=bx+math.cos(a)*18; ry=by-5+math.sin(a)*12
            if on(rx,ry): soft_dot(rx,ry,ac+(int(120+pulse*100),),2)
        # Inner spinning triangle
        for j in range(3):
            a=math.radians(j*120+t_norm*180)
            tx=bx+math.cos(a)*10; ty=by-5+math.sin(a)*7
            if on(tx,ty): soft_dot(tx,ty,hi+(int(180+pulse*60),),3)
        # Center gem
        if on(bx,by-5):
            draw.ellipse([bx-5,by-10,bx+5,by],fill=pt+(int(200+pulse*55),))
            draw.ellipse([bx-2,by-8,bx+2,by-2],fill=(255,255,255,int(200+pulse*55)))
        # ── SHOULDER PADS ─────────────────────────────────────────────────
        for sdx in [-bw//2+8,bw//2-8]:
            spx,spy=bx+sdx,by-20
            if on(spx,spy):
                draw.ellipse([spx-7,spy-5,spx+7,spy+5],fill=ac+(int(130+pulse*80),))
                draw.ellipse([spx-4,spy-3,spx+4,spy+3],fill=hi+(220,))
                draw.polygon([spx,spy-int(5+pulse*5),spx+4,spy-2,spx-4,spy-2],fill=fl+(int(180+pulse*60),))
        # ── BELT ──────────────────────────────────────────────────────────
        belt_y=by+20
        for beltx in range(bx-bw//3,bx+bw//3,4):
            if on(beltx,belt_y): dot(beltx,belt_y,ac+(160,),2)
        if on(bx,belt_y):
            draw.rectangle([bx-6,belt_y-4,bx+6,belt_y+4],fill=hi+(int(160+pulse*80),))
            draw.rectangle([bx-3,belt_y-2,bx+3,belt_y+2],fill=ac+(255,))
        # ── ENERGY VORTEX spiraling into chest ────────────────────────────
        for i in range(14):
            spiral_t=(t_norm+i/14)%1.0
            angle=spiral_t*math.pi*4; radius=(1-spiral_t)*bw//3
            vx=bx+math.cos(angle)*radius; vy=by-5+math.sin(angle)*radius*0.5
            if on(vx,vy): soft_dot(vx,vy,hi+(int(200*spiral_t),),max(1,int(2.5*spiral_t)))
        # ── HEARTBEAT RINGS ───────────────────────────────────────────────
        for ring_idx in range(2):
            phase=(t_norm*2+ring_idx*0.5)%1.0
            ease=phase/0.15 if phase<0.15 else max(0,1-(phase-0.15)/0.85)
            ring_r=int(ease*bw*0.4); alpha=int(200*ease)
            if alpha<10: continue
            for a_deg in range(0,360,8):
                a=math.radians(a_deg)
                rx=bx+math.cos(a)*ring_r; ry=by+math.sin(a)*ring_r*0.5
                if on(rx,ry): dot(rx,ry,pt+(alpha,),2)
        # ── DNA HELIX on body ─────────────────────────────────────────────
        for dy2 in range(-28,28,3):
            t_pos=(dy2+28)/56
            w1x=bx+int(math.sin(t_pos*math.pi*3+t_norm*math.pi*2)*14)
            w2x=bx+int(math.sin(t_pos*math.pi*3+t_norm*math.pi*2+math.pi)*14)
            py2=by+dy2
            if on(w1x,py2): soft_dot(w1x,py2,ac+(int(160+60*math.sin(t_pos*math.pi)),),2)
            if on(w2x,py2): soft_dot(w2x,py2,fl+(int(160+60*math.sin(t_pos*math.pi+math.pi)),),2)
            if dy2%9==0 and on((w1x+w2x)//2,py2): dot((w1x+w2x)//2,py2,hi+(100,),2)
        # ── RUNE CIRCLE ───────────────────────────────────────────────────
        for i in range(6):
            angle=(i/6)*math.pi*2+t_norm*math.pi*2
            rx=bx+math.cos(angle)*(bw//2-5); ry=by+math.sin(angle)*(bw//2-5)*0.45
            if on(rx,ry):
                bright=int(100+140*math.sin(angle+t_norm*math.pi*2))
                draw.polygon([int(rx),int(ry)-5,int(rx)+4,int(ry),int(rx),int(ry)+5,int(rx)-4,int(ry)],fill=ac+(bright,))

    elif group == "robe":
        for i in range(16):
            tx=botx-botw//2+int(i*(botw/15)); wave=int(5*math.sin(i*0.7+t_norm*math.pi*2))
            if on(tx,boty+wave): soft_dot(tx,boty+wave,fl+(int(140+pulse*80),),2)
            if on(tx,boty+8+wave): dot(tx,boty+8+wave,ac+(int(100+pulse*60),),2)
        for i in range(5):
            rise_t=(t_norm+i/5)%1.0; rise=int(math.sin(rise_t*math.pi)*35)
            spark_x=botx-botw//3+int(i*(botw*2/3/4)); spark_y=boty-rise
            if on(spark_x,spark_y): soft_dot(spark_x,spark_y,pt+(int(200*math.sin(rise_t*math.pi)),),2)
        for i in range(9):
            gx=botx-20+i*5; gy=y2-3
            wave=0.5+0.5*math.sin(t_norm*math.pi*2+i*0.5)
            if on(gx,gy): soft_dot(gx,gy,ac+(int(50+wave*130),),int(1+wave*1.5))
        if anim=="flying":
            for i in range(8):
                angle=math.radians(-40+i*10+pulse*20)
                for side in [-1,1]:
                    wx=bx+side*(bw//3+math.cos(angle)*int(18+pulse*12)); wy=by-8+math.sin(angle)*14
                    if on(wx,wy): soft_dot(wx,wy,hi+(int(80+pulse*80),),2)

    elif group == "scythe":
        draw_weapon(draw,mask,sx,sy,theme["weapon"],ac,hi,pt,frame_idx,total,W,H)
        for i in range(4):
            angle=(i/4)*math.pi*2+t_norm*math.pi*2
            px2=sx+math.cos(angle)*13; py2=sy+math.sin(angle)*13
            if on(px2,py2): soft_dot(px2,py2,pt+(int(140+80*math.sin(angle)),),2)
        chain_cx=x2-20
        for i in range(6):
            cy2=(y1+y2)//2-30+i*12
            phase_i=0.5+0.5*math.sin(t_norm*math.pi*4+i*0.5)
            if on(chain_cx,cy2): soft_dot(chain_cx,cy2,ac+(int(80+phase_i*140),),int(2+phase_i))

    elif group == "shape":
        border_style = theme.get("border", None)
        draw_shape_fx(img,mask,fd,theme,frame_idx,total,border_style)

    elif group.startswith("shape_"):
        draw_shape_fx(img,mask,fd,theme,frame_idx,total,group[6:])

    elif group == "meteor":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"meteor_shower",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "iceshatter":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"ice_shatter",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "darktendrils":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"dark_tendrils",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "neonpulse":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"neon_pulse",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "feather":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"feather_fall",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "magma":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"magma_flow",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "soulorbs":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"soul_orbs",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "pixelglitch":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"pixel_glitch",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "chainlightning":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"chain_lightning",ac,hi,pt,fl,frame_idx,total,W,H)
    elif group == "divinelight":
        draw_body_anim(draw,mask,bx,by,bw,botx,boty,botw,"divine_light",ac,hi,pt,fl,frame_idx,total,W,H)

    elif group == "aurora":
        # Aurora wave overlay — independent of body_anim
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        colors=[ac,hi,pt,fl,(255,255,255)]
        for band in range(5):
            phase=(t_norm+band/5)%1.0
            wave_y=int(boty-phase*(boty-(by-30)))
            width=int(bw*0.6*math.sin(phase*math.pi))
            for dx2 in range(-width//2,width//2,2):
                c=colors[band%len(colors)]; alpha=int(180*math.sin(phase*math.pi))
                if on(bx+dx2,wave_y): dot(bx+dx2,wave_y,c+(alpha,),2)
        for i in range(8):
            angle=(i/8)*math.pi*2+t_norm*math.pi*3
            ox=bx+math.cos(angle)*bw//3; oy=by+math.sin(angle)*22
            if on(ox,oy): dot(ox,oy,hi+(int(100+pulse*120),),int(1+pulse))

    elif group == "hellfire":
        # Hellfire columns overlay
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(6):
            col_x=botx-botw//3+i*(botw*2//3//5)
            height=int(20+math.sin(t_norm*math.pi*2+i*1.1)*12)
            for dy2 in range(height):
                t=dy2/height; c=(int(255*(1-t*0.3)),int(40+80*t),0)
                if on(col_x,boty-dy2): dot(col_x,boty-dy2,c+(int(200-t*80),),int(2-t))
            spark_rise=(frame_idx*(3+i)*4+i*17)%40
            if on(col_x,boty-height-spark_rise): dot(col_x,boty-height-spark_rise,pt+(int(200-spark_rise*4),),2)
        for dx2 in range(-botw//2,botw//2,3):
            wave=int(3*math.sin(dx2*0.3+t_norm*math.pi*4))
            if on(botx+dx2,boty+wave): dot(botx+dx2,boty+wave,ac+(int(120+pulse*80),),2)

    elif group == "crystal":
        import colorsys
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(8):
            angle=(i/8)*math.pi*2+t_norm*math.pi*1.2
            dist=bw//3+int(math.sin(t_norm*math.pi*2+i*0.8)*10)
            ox=bx+math.cos(angle)*dist; oy=by+math.sin(angle)*22
            if on(ox,oy):
                r=int(5+pulse*3)
                draw.ellipse([int(ox)-r-3,int(oy)-r-3,int(ox)+r+3,int(oy)+r+3],fill=(100,180,255,int(60+pulse*40)))
                draw.polygon([int(ox),int(oy)-r,int(ox)+r,int(oy),int(ox),int(oy)+r,int(ox)-r,int(oy)],fill=(120,200,255,int(200+pulse*40)))
                hue=(i/8+t_norm*0.3)%1.0; rc,gc,bc=colorsys.hsv_to_rgb(hue,0.4,1.0)
                draw.polygon([int(ox),int(oy)-r,int(ox)+r,int(oy),int(ox),int(oy)],fill=(int(rc*255),int(gc*255),int(bc*255),int(140+pulse*60)))
                dot(ox-1,oy-r+1,(255,255,255,int(220+pulse*35)),1)
        for i in range(4):
            cx2=bx-bw//3+i*(bw*2//3//3); cy2=by-15+i*10
            crack_len=int(14+pulse*6); angle=math.radians(50+i*25)
            for j in range(crack_len):
                kx=cx2+math.cos(angle)*j; ky=cy2+math.sin(angle)*j
                if on(kx,ky):
                    t2=j/crack_len
                    dot(kx,ky,(int(80+120*t2),int(160+80*t2),255,int(200-t2*80)),1)
                    if j%3==0: dot(kx-1,ky-1,(255,255,255,int(120-t2*80)),1)
        for i in range(5):
            a=(i/5)*math.pi*2+t_norm*math.pi*2
            fx2=bx+math.cos(a)*bw//4; fy2=by+math.sin(a)*14
            if on(fx2,fy2): dot(fx2,fy2,(220,240,255,int(140+pulse*80)),int(2+pulse))

    elif group == "lightning":
        # Lightning bolts striking down the body
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for bolt in range(3):
            bx2=bx-bw//3+bolt*(bw//3)
            if (frame_idx+bolt*2)%5==0:  # flash every few frames
                y_cur=by-30
                x_cur=bx2
                while y_cur<boty:
                    x_cur+=random.randint(-4,4)
                    x_cur=max(bx-bw//2,min(bx+bw//2,x_cur))
                    if on(x_cur,y_cur):
                        dot(x_cur,y_cur,(220,220,255,220),2)
                        dot(x_cur,y_cur,(255,255,255,180),1)
                    y_cur+=3
        # Persistent glow dots
        for i in range(6):
            a=(i/6)*math.pi*2+t_norm*math.pi*4
            ox=bx+math.cos(a)*bw//4; oy=by+math.sin(a)*16
            if on(ox,oy): dot(ox,oy,ac+(int(80+pulse*140),),int(1+pulse))

    elif group == "smoke":
        # Smoke tendrils rising from body
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(5):
            base_x=botx-botw//3+i*(botw*2//3//4)
            for step in range(12):
                rise=(frame_idx*2+i*7+step*3)%50
                sx2=base_x+int(math.sin((rise+i*20)*0.25)*8)
                sy2=boty-rise
                alpha=int(180*(1-rise/50))
                if on(sx2,sy2): dot(sx2,sy2,ac+(alpha,),int(3-rise//20))

    elif group == "blood":
        # Blood drip effect
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(7):
            drip=(frame_idx*(2+i%3)*3+i*13)%55
            dx2=botx-botw//3+i*(botw*2//3//6)
            # Drip trail
            for d in range(min(drip,15)):
                alpha=int(220-d*12)
                if on(dx2,boty+d): dot(dx2,boty+d,(180,0,0,alpha),2)
            # Drip head
            if on(dx2,boty+drip%15): dot(dx2,boty+drip%15,(220,0,0,int(200+pulse*40)),3)
        # Splatter on robe
        for i in range(4):
            sx2=bx-bw//4+i*(bw//3); sy2=by+10+i*5
            if on(sx2,sy2) and (frame_idx+i)%8<2:
                dot(sx2,sy2,(160,0,0,int(140+pulse*60)),int(2+pulse))

    elif group == "sand":
        # Sand vortex swirling around body
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(20):
            angle=(i/20)*math.pi*2+t_norm*math.pi*3
            height_frac=i/20
            radius=int((bw//3)*(0.5+0.5*math.sin(height_frac*math.pi)))
            ox=bx+math.cos(angle)*radius
            oy=by-20+int(height_frac*50)
            if on(ox,oy):
                alpha=int(120+80*math.sin(angle))
                dot(ox,oy,ac+(alpha,),int(1+pulse))
                if i%4==0: dot(ox+1,oy-1,hi+(int(alpha*0.6),),1)

    elif group == "wisps":
        # Ghost wisps floating around body
        t_norm=frame_idx/max(total-1,1); pulse=0.5+0.5*math.sin(t_norm*math.pi*2)
        for i in range(4):
            phase=(t_norm+i/4)%1.0
            wx=bx+int(math.sin(phase*math.pi*2+i*1.5)*(bw//2-8))
            wy=by-25+int(phase*60)
            alpha=int(200*math.sin(phase*math.pi))
            if alpha>20 and on(wx,wy):
                draw.ellipse([wx-5,wy-8,wx+5,wy+8],fill=hi+(alpha,))
                draw.ellipse([wx-3,wy-5,wx+3,wy+5],fill=(255,255,255,int(alpha*0.6)))
                # Wisp tail
                for t2 in range(1,5):
                    tx=wx+int(math.sin((phase-t2*0.02)*math.pi*2+i*1.5)*t2*2)
                    ty=wy+t2*4
                    if on(tx,ty): dot(tx,ty,ac+(int(alpha*(1-t2/5)),),2)


def generate_skin(theme_name=None, seed=None, shape_fx=False):
    if seed is not None: random.seed(seed)
    theme = next((t for t in THEMES if t["name"]==theme_name), None) if theme_name else None
    if not theme: theme = random.choice(THEMES)
    variation = random.uniform(-0.2, 0.2)
    skin_id = f"{theme['name'].lower()}_{random.randint(1000,9999)}"
    skin_dir = os.path.join(OUTPUT_DIR, skin_id)
    frames_b64 = {}      # full cosmetics
    base_b64   = {}      # recolor only (no cosmetics)

    # Named overlay groups — each is a transparent RGBA layer
    # Keys match what the sidebar toggles
    BORDER_STYLES = ["armor","fire_border","ice_border","void_border","gold_border","rainbow_border","electric_border","nature_border","royal","flaming_wide","electric_wide","gold_wide","rainbow_wide","chaos_wide","plasma_border","plasma_wide"]
    overlay_groups = ["head", "eyes", "body", "scythe", "robe", "shape", "aurora", "hellfire", "crystal", "lightning", "smoke", "blood", "sand", "wisps", "meteor", "iceshatter", "darktendrils", "neonpulse", "feather", "magma", "soulorbs", "pixelglitch", "chainlightning", "divinelight"] + ["shape_"+b for b in BORDER_STYLES]
    overlays_b64 = {g: {} for g in overlay_groups}

    for anim in ["attack","flying","idle"]:
        src_dir = os.path.join(BLACK_SKIN, anim)
        dst_dir = os.path.join(skin_dir, anim)
        os.makedirs(dst_dir, exist_ok=True)
        frames_b64[anim] = []; base_b64[anim] = []
        for g in overlay_groups: overlays_b64[g][anim] = []

        fnames = sorted([f for f in os.listdir(src_dir) if f.endswith(".png")])
        total = len(fnames)
        fd_list = FRAME_DATA[anim]

        for idx, fname in enumerate(fnames):
            fd = fd_list[idx] if idx < len(fd_list) else fd_list[-1]
            src_path = os.path.join(src_dir, fname)
            mask = get_mask(src_path)
            base_img = recolor(src_path, theme, variation)

            # Full frame
            full = base_img.copy()
            add_cosmetics(full, mask, fd, theme, idx, total, anim)
            if shape_fx: draw_shape_fx(full, mask, fd, theme, idx, total, theme.get("border"))
            # Draw special FX (always on, not toggleable)
            for sfx_key in [theme.get("special1"), theme.get("special2")]:
                if sfx_key: draw_special_fx(full, mask, fd, theme, idx, total, sfx_key)
            full.save(os.path.join(dst_dir, fname), "PNG")
            buf = io.BytesIO(); full.save(buf,"PNG")
            frames_b64[anim].append(base64.b64encode(buf.getvalue()).decode())

            # Base (no cosmetics)
            buf = io.BytesIO(); base_img.save(buf,"PNG")
            base_b64[anim].append(base64.b64encode(buf.getvalue()).decode())

            # Per-group overlays (transparent background, only that group drawn)
            W, H = base_img.size
            for g in overlay_groups:
                ov = Image.new("RGBA", (W,H), (0,0,0,0))
                draw_overlay_group(ov, mask, fd, theme, idx, total, anim, g)
                buf = io.BytesIO(); ov.save(buf,"PNG")
                overlays_b64[g][anim].append(base64.b64encode(buf.getvalue()).decode())

    return skin_id, theme["name"], base_b64, overlays_b64

def create_zip(skin_id):
    skin_dir = os.path.join(OUTPUT_DIR, skin_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for anim in ["attack","flying","idle"]:
            d = os.path.join(skin_dir, anim)
            if os.path.exists(d):
                for f in sorted(os.listdir(d)):
                    zf.write(os.path.join(d,f), f"{skin_id}/{anim}/{f}")
    buf.seek(0)
    return buf
