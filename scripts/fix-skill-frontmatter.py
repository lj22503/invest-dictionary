#!/usr/bin/env python3
"""补齐 WorkBuddy 开放平台要求的 SKILL.md frontmatter 字段。

平台必填：name / display_name / display_name_en / description /
          description_zh / description_en / version / author

本地已有：name / slug / description / displayName / summary / tags / version ...
映射：displayName -> display_name, summary -> description_zh
新增：display_name_en / description_en / author（若缺）

用法：python scripts/fix-skill-frontmatter.py [--check]
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skill" / "skills"

EN = {
    "mangofolio-symptom-lookup": (
        "Money Triage",
        "Describe a money problem in plain words and get the 3-5 dictionary terms you should read first, in a recommended reading order. Explains and helps you tell things apart, never advises.",
    ),
    "mangofolio-question-probe": (
        "Pitch Interrogator",
        "Turn a product name or a sales pitch into 3-5 questions to ask before buying, each with why it matters and how the seller may dodge it, plus red flags.",
    ),
    "mangofolio-duel-compare": (
        "Head to Head",
        "Compare an A-or-B money choice inside one scenario across worst case, liquidity, return source and who it suits, with a break-even line and on-the-spot math.",
    ),
    "mangofolio-decision-mosaic": (
        "Decision Mosaic",
        "Break a personal money decision into the variables it really depends on, map each variable to a dictionary term, and list actions you can take today.",
    ),
    "mangofolio-combo-narrative": (
        "News Translator",
        "Translate a piece of financial news, macro data or policy text into its core concepts and a causal chain from what happened to what it means for you, without predicting prices.",
    ),
    "mangofolio-daily-hotword": (
        "Daily Buzzwords",
        "Pick 3-5 must-know investing terms from today's hot topic, explain each in plain language, then tie them into one story you can retell to someone else.",
    ),
    "mangofolio-concept-combinator": (
        "Concept Chain",
        "Turn complex material into a six-screen mobile web narrative a non-expert can finish reading, built from linked dictionary terms.",
    ),
    "mangofolio-generator": (
        "Term Writer",
        "Write a plain-language Chinese finance dictionary entry in a fixed structure (one-line definition, why it matters, how to use it, common traps) as Markdown or a dictionary-style HTML page.",
    ),
}

REQUIRED = [
    "name",
    "display_name",
    "display_name_en",
    "description",
    "description_zh",
    "description_en",
    "version",
    "author",
]


def parse(text):
    """返回 (frontmatter dict, body)。只处理简单 key: value 与 key: [..] 形式。"""
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    end = text.index("\n---", 3)
    fm_raw = text[3:end].strip("\n")
    body = text[end + 4 :]
    fm = {}
    order = []
    for line in fm_raw.splitlines():
        if not line.strip() or line.startswith(" ") or line.startswith("- "):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        fm[k] = v.strip()
        order.append(k)
    return fm, body, order


def render(fm, order, body):
    out = ["---"]
    for k in order:
        out.append(f"{k}: {fm[k]}")
    out.append("---")
    return "\n".join(out) + "\n" + body.lstrip("\n")


def main():
    check_only = "--check" in sys.argv
    missing_report = []
    for d in sorted(SKILLS.iterdir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        fm, body, order = parse(text)

        if "display_name" not in fm and "displayName" in fm:
            fm["display_name"] = fm["displayName"]
            order.insert(order.index("displayName") + 1, "display_name")
        if "description_zh" not in fm and "summary" in fm:
            fm["description_zh"] = fm["summary"]
            order.insert(order.index("summary") + 1, "description_zh")
        en_name, en_desc = EN.get(d.name, ("", ""))
        if en_name and "display_name_en" not in fm:
            fm["display_name_en"] = en_name
            order.insert(order.index("display_name") + 1, "display_name_en")
        if en_desc and "description_en" not in fm:
            fm["description_en"] = en_desc
            order.insert(order.index("description_zh") + 1, "description_en")
        if "author" not in fm:
            fm["author"] = "Mangofolio"
            order.insert(order.index("version") + 1, "author")

        miss = [k for k in REQUIRED if k not in fm]
        if miss:
            missing_report.append((d.name, miss))
        if check_only:
            continue
        new = render(fm, order, body)
        if new != text:
            f.write_text(new, encoding="utf-8")
            print(f"updated {d.name}")

    if missing_report:
        print("MISSING:")
        for n, m in missing_report:
            print(f"  {n}: {m}")
        return 1
    print("all required fields present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
