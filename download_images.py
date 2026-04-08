import os
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


ROOT = "F:\\Code\\luokewguo"
HTML_PATH = os.path.join(ROOT, "完整页面.html")
SAVE_DIR = os.path.join(ROOT, "images")
NAME_LIST_PATH = os.path.join(ROOT, "精灵姓名列表.txt")


with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
matches = []
for a in soup.select('a[title][href^="/rocom/"]'):
    img = a.find("img", class_=lambda c: c and "rocom_prop_icon" in c)
    if not img:
        continue
    src = img.get("src") or img.get("data-src") or ""
    if not src:
        continue
    matches.append((a.get("title", "").strip(), src.strip()))

print(f"匹配到 {len(matches)} 个精灵候选")

os.makedirs(SAVE_DIR, exist_ok=True)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://wiki.biligame.com/rocom/",
}

exclude = {
    "首页", "图鉴", "技能", "道具", "地图", "用户", "帮助", "编辑", "历史", "页面", "最近更改"
}

seen_names = set()
saved_count = 0

for raw_name, img_url in matches:
    name = re.sub(r"\(.*?\)|（.*?）|\|.*", "", raw_name).strip()
    if not name or any(k in name for k in exclude):
        continue

    if img_url.startswith("//"):
        img_url = "https:" + img_url
    if not img_url.startswith("http"):
        continue

    safe_name = "".join(c for c in name if c not in r'\\/:*?"<>|').strip()
    if not safe_name or safe_name in seen_names:
        continue

    path = urlparse(img_url).path
    ext = os.path.splitext(path)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        ext = ".png"

    img_path = os.path.join(SAVE_DIR, f"{safe_name}{ext}")

    try:
        r = requests.get(img_url, headers=headers, timeout=20)
        if r.status_code != 200 or not r.content:
            continue

        with open(img_path, "wb") as f:
            f.write(r.content)

        seen_names.add(safe_name)
        saved_count += 1
        if saved_count % 50 == 0:
            print(f"已下载 {saved_count} 张...")
        time.sleep(0.05)
    except Exception:
        continue

with open(NAME_LIST_PATH, "w", encoding="utf-8") as f:
    for idx, name in enumerate(sorted(seen_names), 1):
        f.write(f"{idx}. {name}\n")

print("\n下载完成")
print(f"成功保存图片: {saved_count} 张")
print(f"图片目录: {SAVE_DIR}")
print(f"姓名列表: {NAME_LIST_PATH}")
