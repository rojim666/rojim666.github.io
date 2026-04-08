from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = ROOT / "rojim666.github.io"
ROOT_IMAGES = ROOT / "images"
SITE_IMAGES = SITE_ROOT / "source" / "images"
LAYOUT_FILE = SITE_ROOT / "themes" / "landscape" / "layout" / "layout.ejs"

KEEP_FILES = {"logo_rocom.png", "season-banner.png", "season-banner.webp"}


def js_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def sync_images() -> list[str]:
    SITE_IMAGES.mkdir(parents=True, exist_ok=True)

    # Remove old sprite images in site folder, keep branding assets.
    for f in SITE_IMAGES.iterdir():
        if not f.is_file():
            continue
        if f.name in KEEP_FILES:
            continue
        if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            f.unlink()

    copied = []
    for f in ROOT_IMAGES.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        target = SITE_IMAGES / f.name
        shutil.copy2(f, target)
        copied.append(f.stem)

    # Keep site logo from root if present.
    root_logo = ROOT / "logo_rocom.png"
    if root_logo.exists():
        shutil.copy2(root_logo, SITE_IMAGES / "logo_rocom.png")

    return sorted(set(copied))


def rebuild_sprites(names: list[str]) -> None:
    rows = []
    for name in names:
        ext = ".png"
        image_path = f"images/{name}{ext}"
        rows.append(f"    {{ name: '{js_escape(name)}', image: '{js_escape(image_path)}' }},")

    sprites_block = "const sprites = [\n" + "\n".join(rows) + "\n];\n\n        function normalizeSprites"

    text = LAYOUT_FILE.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"const sprites = \[(?:.|\n)*?\];\n\n\s*function normalizeSprites",
        sprites_block,
        text,
        count=1,
    )

    if n != 1:
        raise RuntimeError("Failed to replace sprites block in layout.ejs")

    LAYOUT_FILE.write_text(new_text, encoding="utf-8")


def main() -> None:
    names = sync_images()
    rebuild_sprites(names)
    print(f"Synced images from root: {len(names)}")


if __name__ == "__main__":
    main()
