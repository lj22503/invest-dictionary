# -*- coding: utf-8 -*-
"""生成 skill 包内的词条索引（term-index.txt）

背景：8 个 Skill 都要求"输出的词条必须能在词典里查到"，但上架后包里没有
dictionary.json，AI 无从校验，只能凭记忆编。这里把 title + filename 压成
一份只读索引，随每个 Skill 分发，供输出前核对。

格式：每行 `词条名<TAB>文件名`，UTF-8，无表头。
体积：1115 条约 45 KB。

用法：
    python scripts/sync-skill-term-index.py

注意：词库变更后必须重跑（已接入 sync-site.py 链路），否则 Skill 会校验失败。
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(ROOT, "web", "dictionary.json")
SKILLS_DIR = os.path.join(ROOT, "skill", "skills")
MARKER = "<!-- term-index:auto -->"


def build_index():
    with open(DICT_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    lines = []
    for e in entries:
        title = (e.get("title") or "").strip()
        filename = (e.get("filename") or "").strip()
        if not title or not filename:
            continue
        # 制表符/换行会破坏行结构，理论上不会出现，兜底替换
        title = title.replace("\t", " ").replace("\n", " ")
        lines.append("%s\t%s" % (title, filename))
    lines.sort()
    return lines


def main():
    lines = build_index()
    payload = "\n".join(lines) + "\n"

    if not os.path.isdir(SKILLS_DIR):
        print("[ERROR] 找不到 %s，请先确认 skill 目录结构" % SKILLS_DIR)
        return 1

    written, skipped = [], []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(skill_dir):
            continue
        ref_dir = os.path.join(skill_dir, "references")
        out = os.path.join(ref_dir, "term-index.txt")

        # 技能正文不查本地索引时，不要往里塞一份 50KB 的死重（包体积白涨，agent 还可能去读）
        md = os.path.join(skill_dir, "SKILL.md")
        body = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
        if "term-index.txt" not in body:
            if os.path.exists(out):
                os.remove(out)
                skipped.append((name, "已删除旧索引"))
            else:
                skipped.append((name, "不需要"))
            continue

        os.makedirs(ref_dir, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(payload)
        written.append((name, len(payload.encode("utf-8"))))

    print("词条数：%d" % len(lines))
    print("单份大小：%.1f KB" % (len(payload.encode("utf-8")) / 1024.0))
    for name, size in written:
        print("  OK  %-34s %.1f KB" % (name, size / 1024.0))
    for name, why in skipped:
        print("  --  %-34s %s" % (name, why))
    print("共写入 %d 个 Skill，跳过 %d 个" % (len(written), len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
