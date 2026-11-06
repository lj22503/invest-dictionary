#!/usr/bin/env python3
"""按 WorkBuddy 开放平台结构，把 skill/skills/ 下的每个 Skill 打成独立上传包。

平台结构（https://open.workbuddy.cn/docs/skill）：
    {skill-name}/
        ├── SKILL.md      ★ 必须，位于包根
        ├── references/   可选
        ├── scripts/      可选
        └── templates/    可选

输出：
    dist/workbuddy/<skill-name>.zip          单个技能包（默认带一层同名目录）
    dist/workbuddy/UPLOAD.md                 逐个技能的填表文案

用法：
    python scripts/build-workbuddy.py             # 全部
    python scripts/build-workbuddy.py --only mangofolio-symptom-lookup
    python scripts/build-workbuddy.py --flat      # zip 根直接放 SKILL.md（无外层目录）
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skill" / "skills"
OUT = REPO / "dist" / "workbuddy"
ICON = REPO / "skill" / "assets" / "logo-512.png"

# 包内允许的子目录（平台白名单 + 本地已有的 examples）
ALLOWED_DIRS = ("references", "scripts", "templates", "examples")

# 上架顺序：先易后难，先传最简单的验证解析
ORDER = [
    "mangofolio-symptom-lookup",
    "mangofolio-question-probe",
    "mangofolio-duel-compare",
    "mangofolio-decision-mosaic",
    "mangofolio-daily-hotword",
    "mangofolio-combo-narrative",
    "mangofolio-concept-combinator",
    "mangofolio-generator",
]

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


def read_fm(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"{path}: 缺少 YAML frontmatter")
    end = text.index("\n---", 3)
    fm = {}
    for line in text[3:end].strip("\n").splitlines():
        if ":" in line and not line.startswith((" ", "\t", "- ")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text


def build(name, flat=False):
    src = SKILLS / name
    skill_md = src / "SKILL.md"
    if not skill_md.is_file():
        raise SystemExit(f"{name}: 找不到 SKILL.md")

    fm, _ = read_fm(skill_md)
    miss = [k for k in REQUIRED if not fm.get(k)]
    if miss:
        raise SystemExit(f"{name}: frontmatter 缺 {miss}")
    if fm["name"] != name:
        raise SystemExit(f"{name}: frontmatter name={fm['name']} 与目录名不一致")

    files = [skill_md]
    for sub in ALLOWED_DIRS:
        d = src / sub
        if d.is_dir():
            files += [p for p in sorted(d.rglob("*")) if p.is_file()]
    # 过滤掉常见垃圾
    files = [p for p in files if p.suffix.lower() not in {".bak", ".png", ".jpg", ".zip"} or p == skill_md]

    prefix = "" if flat else f"{name}/"
    zip_path = OUT / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, prefix + p.relative_to(src).as_posix())
    return zip_path, fm, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只打一个 skill 名")
    ap.add_argument("--flat", action="store_true", help="zip 根目录直接放 SKILL.md")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    names = [args.only] if args.only else ORDER
    rows = []
    for n in names:
        zp, fm, cnt = build(n, flat=args.flat)
        size = zp.stat().st_size / 1024
        print(f"{n:34s} {cnt:2d} files  {size:6.1f} KB")
        rows.append((n, fm, zp, size, cnt))

    lines = [
        "# WorkBuddy 上架清单 · Mangofolio",
        "",
        "> 平台是「一个技能一个包」，逐个创建。图标统一用 `skill/assets/logo-512.png`。",
        "> 上传顺序按下面表格从上到下，第一个包结构最简，先验证解析能过。",
        "",
        "| # | 技能 | 中文名 | 英文名 | 版本 | 包 |",
        "| :- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for i, (n, fm, zp, size, cnt) in enumerate(rows, 1):
        lines.append(
            f"| {i} | `{n}` | {fm.get('display_name','')} | {fm.get('display_name_en','')} "
            f"| {fm.get('version','')} | `{zp.name}`（{size:.0f} KB） |"
        )
    lines += ["", "## 逐个填表文案", ""]
    for n, fm, zp, size, cnt in rows:
        lines += [
            f"### {fm.get('display_name','')}（`{n}`）",
            "",
            f"- **技能标识**：`{n}`",
            f"- **中文名**：{fm.get('display_name','')}",
            f"- **英文名**：{fm.get('display_name_en','')}",
            f"- **版本**：{fm.get('version','')}",
            f"- **作者**：{fm.get('author','')}",
            f"- **包**：`dist/workbuddy/{zp.name}`",
            "",
            f"**一句话介绍（中文）**  ",
            fm.get("description_zh", ""),
            "",
            "**英文介绍**  ",
            fm.get("description_en", ""),
            "",
            "**用途与触发词（description）**  ",
            fm.get("description", ""),
            "",
            f"**官网** {fm.get('homepage','https://dictionary.mangofolio.com/')}",
            "",
        ]
    (OUT / "UPLOAD.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n清单已写入 {OUT / 'UPLOAD.md'}")
    print(f"图标：{ICON}（{ICON.stat().st_size/1024:.0f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
