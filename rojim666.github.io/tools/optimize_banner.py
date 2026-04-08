from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'source' / 'images' / 'season-banner.png'
out = ROOT / 'source' / 'images' / 'season-banner.webp'

img = Image.open(src).convert('RGB')
max_width = 1280
if img.width > max_width:
    new_height = round(img.height * max_width / img.width)
    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

img.save(out, 'WEBP', quality=78, method=6)
print(f'saved {out} {out.stat().st_size}')
