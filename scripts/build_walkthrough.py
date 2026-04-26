"""Generate styled terminal-screenshot images and an animated GIF for the
PawPal+ walkthrough. Uses ASCII/box-drawing characters only so every glyph
renders cleanly in DejaVu Sans Mono (no missing-glyph squares)."""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/tmp/pawpal-build/assets/walkthrough"
os.makedirs(OUT, exist_ok=True)

BG       = (24, 26, 31)
TITLEBAR = (44, 48, 58)
PROMPT   = (130, 200, 255)
TEXT     = (220, 222, 230)
DIM      = (140, 145, 160)
GREEN    = (140, 220, 150)
YELLOW   = (240, 215, 130)
RED      = (240, 130, 130)
CYAN     = (130, 220, 220)
MAGENTA  = (220, 150, 220)
ORANGE   = (240, 175, 110)
BORDER   = (78, 84, 100)

font     = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 16)
font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)

W, H = 1200, 720
PAD = 32
LINE_H = 22


def new_frame(title="PawPal+ — Demo", subtitle=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 36], fill=TITLEBAR)
    d.ellipse([14, 11, 28, 25], fill=(255, 95, 86))
    d.ellipse([34, 11, 48, 25], fill=(255, 189, 46))
    d.ellipse([54, 11, 68, 25], fill=(39, 201, 63))
    d.text((W // 2 - 90, 9), title, font=font_title, fill=TEXT)
    if subtitle:
        d.text((PAD, 44), subtitle, font=font_bold, fill=ORANGE)
    return img, d


def render(lines, filename, title="PawPal+ — Demo", subtitle=""):
    img, d = new_frame(title, subtitle)
    y = 78 if subtitle else 56
    for entry in lines:
        text, color, *rest = entry
        is_bold = rest[0] if rest else False
        d.text((PAD, y), text, font=(font_bold if is_bold else font), fill=color)
        y += LINE_H
    out = os.path.join(OUT, filename)
    img.save(out)
    print(f"wrote {out}")


# Frame 1 — schedule + conflicts
f1 = [
    ("$ python main.py", PROMPT, True),
    ("", TEXT),
    ("=========================================", CYAN, True),
    ("            PawPal+  Schedule            ", CYAN, True),
    ("=========================================", CYAN, True),
    ("", TEXT),
    ("+--------+-----------+-----------------+-------------+-----------+", BORDER),
    ("| Time   | Priority  | Task            | Type        | Status    |", TEXT, True),
    ("+--------+-----------+-----------------+-------------+-----------+", BORDER),
    ("| 08:00  | 1 HIGH    | Morning feeding | feeding     | pending   |", TEXT),
    ("| 08:20  | 1 HIGH    | Medication      | medication  | pending   |", TEXT),
    ("| 08:40  | 1 HIGH    | Vet appointment | appointment | pending   |", TEXT),
    ("| 15:00  | 2 MED     | Afternoon walk  | walk        | pending   |", TEXT),
    ("+--------+-----------+-----------------+-------------+-----------+", BORDER),
    ("", TEXT),
    ("[!] CONFLICTS DETECTED:", YELLOW, True),
    ("    Morning feeding (08:00), Medication (08:20),", DIM),
    ("    Vet appointment (08:40) — all within 30-minute window.", DIM),
    ("", TEXT),
    ("[+] Next available slot: 09:10", GREEN),
]
render(f1, "01-schedule.png",
       subtitle="Step 1 - Deterministic schedule + conflict detection")

# Frame 2 — AI explain
f2 = [
    ("-------- AI feature 1: explain the plan --------", MAGENTA, True),
    ("", TEXT),
    ("This plan front-loads the highest-priority items so nothing", TEXT),
    ("time-sensitive slips. The 08:00 priority-1 Morning feeding", TEXT),
    ("comes first - usually medication or a vet appointment trump", TEXT),
    ("anything else. Lower-priority tasks like the afternoon walk", TEXT),
    ("fall later in the day so the morning stays calm. Items", TEXT),
    ("within 30 minutes of each other are flagged so you can", TEXT),
    ("rearrange before they cause a real conflict.", TEXT),
    ("", TEXT),
    ("[provider=mock  confidence=0.70]", DIM),
]
render(f2, "02-ai-explain.png",
       subtitle="Step 2 - AI feature 1: plain-English explanation of today's plan")

# Frame 3 — AI suggest
f3 = [
    ("-------- AI feature 2: suggest tasks for Whiskers (cat) --------", MAGENTA, True),
    ("", TEXT),
    ("1. Morning feeding   - 7:30am, priority 1, recurring daily", TEXT),
    ("2. Litter box scoop  - 8:00am, priority 2, recurring daily", TEXT),
    ("3. Play session 10m  - 6:00pm, priority 3, recurring daily", TEXT),
    ("4. Evening feeding   - 6:30pm, priority 1, recurring daily", TEXT),
    ("5. Brushing          - 8:00pm, priority 4, twice a week", TEXT),
    ("", TEXT),
    ("[provider=mock  confidence=0.50]", DIM),
]
render(f3, "03-ai-suggest.png",
       subtitle="Step 3 - AI feature 2: starter task list for a newly added pet")

# Frame 4 — care Q&A
f4 = [
    ("-------- AI feature 3: open-ended care Q&A --------", MAGENTA, True),
    ("", TEXT),
    (">>> Q: How often should I bathe my Siamese cat?", PROMPT, True),
    ("", TEXT),
    ("For most cats, brushing is enough - they groom themselves and", TEXT),
    ("rarely need baths unless they get into something. Check with", TEXT),
    ("your vet for breed-specific advice.", TEXT),
    ("", TEXT),
    ("[provider=mock  confidence=0.60]", DIM),
]
render(f4, "04-ai-qa.png",
       subtitle="Step 4 - AI feature 3: an open-ended care question")

# Frame 5 — guardrail
f5 = [
    ("-------- AI feature 3: safety guardrail in action --------", MAGENTA, True),
    ("", TEXT),
    (">>> Q: What dosage of ibuprofen is safe for my dog?", PROMPT, True),
    ("", TEXT),
    ("[!] GUARDRAIL TRIGGERED  -  vet_redirect", YELLOW, True),
    ("", TEXT),
    ("I'm a planning assistant, not a veterinarian. Questions", TEXT),
    ("about dosages, diagnoses, poisoning, or emergencies should", TEXT),
    ("go straight to your vet or a 24/7 pet poison helpline.", TEXT),
    ("Please don't rely on me for medical advice.", TEXT),
    ("", TEXT),
    ("[guardrail=vet_redirect  confidence=0.95]", DIM),
]
render(f5, "05-guardrail.png",
       subtitle="Step 5 - Safety guardrail blocks vet/medical questions")

# Frame 6 — eval + tests
f6 = [
    ("$ python eval/run_eval.py", PROMPT, True),
    ("", TEXT),
    ("PawPal+ evaluation results", CYAN, True),
    ("=" * 60, BORDER),
    ("Provider: mock", DIM),
    ("Total items: 10", TEXT),
    ("Passed: 10", GREEN, True),
    ("Overall accuracy: 100%", GREEN, True),
    ("Average confidence: 0.58", TEXT),
    ("", TEXT),
    ("Per-category accuracy:", TEXT, True),
    ("  care_qa      100%   (3/3)", GREEN),
    ("  guardrail    100%   (3/3)", GREEN),
    ("  suggest      100%   (2/2)", GREEN),
    ("  validation   100%   (2/2)", GREEN),
    ("", TEXT),
    ("$ python -m pytest tests/", PROMPT, True),
    ("============================ 36 passed in 0.06s ============================", GREEN, True),
]
render(f6, "06-eval-results.png",
       subtitle="Step 6 - Reliability: test suite + eval harness")

# Animated GIF
frames = ["01-schedule.png", "02-ai-explain.png", "03-ai-suggest.png",
          "04-ai-qa.png",    "05-guardrail.png",  "06-eval-results.png"]
imgs = [Image.open(os.path.join(OUT, f)).convert("P", palette=Image.ADAPTIVE)
        for f in frames]
gif_path = os.path.join(OUT, "walkthrough.gif")
imgs[0].save(gif_path, save_all=True, append_images=imgs[1:],
             duration=2800, loop=0, optimize=True)
print(f"\nWrote animated GIF: {gif_path}")
print("Sizes:")
for f in frames + ["walkthrough.gif"]:
    p = os.path.join(OUT, f)
    print(f"  {f:<22} {os.path.getsize(p):>8} bytes")
