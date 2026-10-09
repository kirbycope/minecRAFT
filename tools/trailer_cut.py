"""Cuts the takes filmed by tools/trailer.py into the minecRAFT trailer, with the trailer skill's titles.py and
assemble.py (../.claude/skills/trailer/): shots measured in beats of the music, the game's own sound under it, the
music ducked beneath that and the mix levelled to -14 LUFS.

    python tools/trailer_cut.py            # writes trailer/minecRAFT-trailer.mp4

First each take is cut down to what the edit uses: the 16:9 middle of the Mac's fullscreen frame (below the camera
notch's black bar), 1920x1080 at 30 fps, and sped up for the shots that show time passing (named <take>_x<speed>,
without sound, since sped up it would chirp). Then the cards: the title and the end card with the minecRAFT wordmark
in the game's own fonts, as minecRAFT-bedrock's trailer has it (Minecraft Ten is capitals only, so the pun is in the
colour: MINEC white, RAFT plank orange), and the captions from trailer/titles.json through titles.py. Last,
trailer/edit.json goes to assemble.py. The music and the fonts are not in the repository: trailer/takes/music.wav
(A Beautiful Discovery, from the Fantasy Adventure & Exploration Music pack) and trailer/takes/fonts/.
"""

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAILER = os.path.join(ROOT, "trailer")
TAKES = os.path.join(TRAILER, "takes")
CUT = os.path.join(TAKES, "cut")
CARDS = os.path.join(TAKES, "cards")
SKILL = os.path.join(os.path.dirname(ROOT), ".claude", "skills", "trailer")
OUT = os.path.join(TRAILER, "minecRAFT-trailer.mp4")
FRAME = "crop=2592:1458:0:134"   # the 16:9 middle of a 2592x1674 take, below the notch's 52-pixel bar and centred
W, H = 1920, 1080
WHITE, PLANK, SEA = (255, 255, 255, 255), (236, 164, 74, 255), (16, 44, 78, 255)


def normalise(take: str, speed: float = 1.0) -> str:
    name = take if speed == 1 else f"{take}_x{speed:g}"
    out = os.path.join(CUT, f"{name}.mp4")
    source = os.path.join(TAKES, f"{take}.mp4")
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(source):
        return name
    video = f"{FRAME},scale={W}:{H}:flags=lanczos,setpts=PTS/{speed},fps=30"
    audio = ["-c:a", "aac", "-b:a", "256k"] if speed == 1 else ["-an"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", source, "-vf", video, *audio, "-c:v", "libx264", "-preset", "medium",
                    "-crf", "14", "-pix_fmt", "yuv420p", out], check=True)
    return name


def wordmark(size: int) -> Image.Image:
    ten = ImageFont.truetype(os.path.join(TAKES, "fonts", "ten.otf"), size)
    parts = [("MINEC", WHITE), ("RAFT", PLANK)]
    width = int(sum(ten.getlength(t) for t, _ in parts)) + size // 3
    img = Image.new("RGBA", (width, int(size * 1.4)), (0, 0, 0, 0))
    draw, x = ImageDraw.Draw(img), size // 6
    for text, colour in parts:
        draw.text((x, size // 8), text, font=ten, fill=colour, stroke_width=max(4, size // 22), stroke_fill=SEA)
        x += ten.getlength(text)
    return img


def card(name: str, lines: list[tuple[str, int, tuple]], field=None, mark_y: int = 330, mark_size: int = 190) -> None:
    """A wordmark card: the wordmark centred at mark_y, lines of Minecraft Seven under it, a soft shadow behind all."""
    seven = lambda size: ImageFont.truetype(os.path.join(TAKES, "fonts", "seven.ttf"), size)
    im = Image.new("RGBA", (W, H), field or (0, 0, 0, 0))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mark = wordmark(mark_size)
    layer.alpha_composite(mark, (W // 2 - mark.width // 2, mark_y))
    draw = ImageDraw.Draw(layer)
    y = mark_y + mark.height + 30
    for text, size, colour in lines:
        draw.text((W // 2, y), text, font=seven(size), fill=colour, anchor="mt", stroke_width=3, stroke_fill=SEA)
        y += int(size * 1.5)
    shade = layer.copy().filter(ImageFilter.GaussianBlur(10))
    shade.putalpha(shade.getchannel("A").point(lambda v: v * 150 // 255))
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    black.putalpha(shade.getchannel("A"))
    im.alpha_composite(black, (6, 8))
    im.alpha_composite(layer)
    im.save(os.path.join(CARDS, f"{name}.png"))
    preview = Image.new("RGBA", (W, H), (70, 110, 160, 255))
    preview.alpha_composite(im)
    preview.convert("RGB").resize((960, 540)).save(os.path.join(CARDS, f"{name}_preview.png"))


def main() -> int:
    os.makedirs(CUT, exist_ok=True)
    os.makedirs(CARDS, exist_ok=True)
    edit = json.load(open(os.path.join(TRAILER, "edit.json"), encoding="utf-8"))
    for shot in edit["shots"]:
        take, _, speed = shot["take"].partition("_x")
        normalise(take, float(speed) if speed else 1.0)
    card("title", [("Raft, in Minecraft: Java Edition", 58, WHITE)])
    card("end", [("Free for Minecraft: Java Edition", 58, WHITE), ("github.com/kirbycope/minecRAFT", 44, (220, 230, 240, 255))],
         field=(8, 18, 34, 170), mark_y=300)
    subprocess.run([sys.executable, os.path.join(SKILL, "titles.py"), os.path.join(TRAILER, "titles.json"), "--out", CARDS, "--preview"], check=True, cwd=ROOT)
    edit["music"]["file"] = os.path.join(TAKES, "music.wav")
    resolved = os.path.join(TAKES, "edit.resolved.json")
    json.dump(edit, open(resolved, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(SKILL, "assemble.py"), resolved, "--takes", CUT, "--cards", CARDS, "--out", OUT], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
