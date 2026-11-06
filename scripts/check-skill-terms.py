# -*- coding: utf-8 -*-
"""校验 Skill 里点名的词条是否真实存在于词库

检查三类"点名词条"的结构：
  1. 表格里「关键概念 / 候选词条簇」列的顿号分隔项
  2. 【最该先看】后的词
  3. 【关键概念】段落里「- 词条名 ——」的条目

用法：
    python scripts/check-skill-terms.py          # 检查
    python scripts/check-skill-terms.py --strict # 有缺失即非 0 退出（供门禁）

已接入 sync-site.py 之后的手工检查清单；词库有增删时请一并跑。
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skill", "skills")


def load_titles(skill_dir):
    p = os.path.join(skill_dir, "references", "term-index.txt")
    if not os.path.exists(p):
        return None
    titles = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" in line:
                titles.append(line.split("\t", 1)[0])
    return titles


def clean(word):
    """去掉括注部分，便于「IRR（内部收益率）」匹配「IRR（内部收益率 / 分期真实利率）」"""
    return re.split(r"[（(]", word, maxsplit=1)[0].strip()


def hit(word, titles):
    w = word.strip()
    if not w:
        return True
    cw = clean(w)
    for t in titles:
        if w in t or t in w:
            return True
        ct = clean(t)
        if cw and ct and (cw == ct or cw in ct or ct in cw):
            return True
    return False


def extract_table_terms(text, header_kw):
    """提取表头含 header_kw 的表格，返回最后一列拆分出的词"""
    out = []
    lines = text.splitlines()
    in_table = False
    for line in lines:
        s = line.strip()
        if s.startswith("|") and header_kw in s:
            in_table = True
            continue
        if in_table:
            if not s.startswith("|"):
                in_table = False
                continue
            if set(s) <= set("| :-"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not cells:
                continue
            for w in cells[-1].split("、"):
                w = w.strip()
                if w:
                    out.append(w)
    return out


def extract_priority(text):
    out = []
    for m in re.finditer(r"【最该先看】([^\n—]+?)\s*——", text):
        w = m.group(1).strip()
        if w not in PLACEHOLDERS:
            out.append(w)
    return out


def extract_example_terms(text):
    """示例段里 `1. 词条 ——` 形式的词条名（排除问题式句子）"""
    out = []
    block = re.search(r"## 示例\n(.*?)(?:\n## |\Z)", text, re.S)
    if not block:
        return out
    body = block.group(1)
    # 变量清单不是词条，先剔除
    body = re.sub(r"【这个决策取决于这[^】]*】.*?(?=\n【|\Z)", "", body, flags=re.S)
    for line in body.splitlines():
        m = re.match(r"\s*\d+\.\s*([^—]+?)\s*——", line)
        if not m:
            continue
        w = m.group(1).strip()
        if w in PLACEHOLDERS:
            continue
        if any(ch in w for ch in ['"', "“", "？", "?", "：", ":"]):
            continue
        if "填" in w or "让用户" in w:
            continue
        if len(w) > 14:
            continue
        out.append(w)
    return out


CONCEPT_BLOCKS = ["【关键概念】", "【里面的几个概念】", "【今天必须懂的热词】", "【再看这几条】"]
PLACEHOLDERS = {"词条名", "概念名", "热词名", "词条A", "词条B", "概念1", "概念2"}


def extract_concept_list(text):
    out = []
    for name in CONCEPT_BLOCKS:
        block = re.search(re.escape(name) + r"\n(.*?)(?:\n【|\Z)", text, re.S)
        if not block:
            continue
        for line in block.group(1).splitlines():
            m = re.match(r"\s*(?:[-*]|\d+\.)\s*([^—]+?)\s*——", line)
            if m:
                w = m.group(1).strip()
                if w not in PLACEHOLDERS:
                    out.append(w)
    return out


def main():
    strict = "--strict" in sys.argv
    total_missing = 0
    for name in sorted(os.listdir(SKILLS)):
        d = os.path.join(SKILLS, name)
        md = os.path.join(d, "SKILL.md")
        if not os.path.isfile(md):
            continue
        titles = load_titles(d)
        if titles is None:
            print("%-34s [FAIL] 缺 references/term-index.txt" % name)
            total_missing += 1
            continue
        text = open(md, encoding="utf-8").read()
        cands = []
        cands += extract_table_terms(text, "关键概念")
        cands += extract_table_terms(text, "候选词条簇")
        cands += extract_priority(text)
        cands += extract_concept_list(text)
        cands += extract_example_terms(text)
        seen = list(dict.fromkeys(cands))
        miss = [w for w in seen if not hit(w, titles)]
        if miss:
            print("%-34s 提及 %2d 个，缺失 %d：%s" % (name, len(seen), len(miss), "、".join(miss)))
            total_missing += len(miss)
        else:
            print("%-34s 提及 %2d 个，全部命中" % (name, len(seen)))

    print("\n合计缺失：%d" % total_missing)
    if strict and total_missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
