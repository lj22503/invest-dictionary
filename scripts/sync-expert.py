#!/usr/bin/env python3
"""把仓库里的专家源同步到 WorkBuddy 专家目录。

仓库是源，专家目录是产物：
    expert/                          专家元文件（plugin.json / agents / avatars / README）
    skill/skills/                    8 个 Skill
        ↓  scripts/sync-expert.py
    $WORKBUDDY_CONFIG_DIR/plugins/marketplaces/my-experts/plugins/mango/

改了 plugin.json、agents/mango.md 或任一 Skill 之后跑一次，否则本地专家是旧版。

用法：
    python scripts/sync-expert.py            # 同步
    python scripts/sync-expert.py --check    # 只比对，有差异返回 1
"""
import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPERT_SRC = REPO / "expert"
SKILLS_SRC = REPO / "skill" / "skills"
CONFIG = os.environ.get("WORKBUDDY_CONFIG_DIR") or str(Path.home() / ".workbuddy")
EXPERT_DST = Path(CONFIG) / "plugins" / "marketplaces" / "my-experts" / "plugins" / "mango"


def diff_dirs(a, b):
    only_a, only_b, differ = [], [], []
    for p in sorted(a.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(a)
        q = b / rel
        if not q.exists():
            only_a.append(str(rel))
        elif not filecmp.cmp(p, q, shallow=False):
            differ.append(str(rel))
    if b.is_dir():
        for q in sorted(b.rglob("*")):
            if q.is_file() and not (a / q.relative_to(b)).exists():
                only_b.append(str(q.relative_to(b)))
    return only_a, only_b, differ


def sync_meta(dry):
    """expert/ 下的元文件 → 专家目录（skills/ 由 skill/skills 单独同步）。"""
    changed = 0
    for rel in (".codebuddy-plugin/plugin.json", "agents/mango.md", "avatars/expert.png", "README.md"):
        src = EXPERT_SRC / rel
        dst = EXPERT_DST / rel
        if not src.exists():
            print(f"  ⚠ 源缺 {rel}")
            continue
        same = dst.exists() and filecmp.cmp(src, dst, shallow=False)
        if not same:
            changed += 1
            print(f"  ~ {rel}")
            if not dry:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    return changed


def sync_skills(dry):
    names = sorted(d.name for d in SKILLS_SRC.iterdir() if d.is_dir())
    dst = EXPERT_DST / "skills"
    only_a, only_b, differ = diff_dirs(SKILLS_SRC, dst)
    if only_a or only_b or differ:
        print(f"  ~ skills：新增 {len(only_a)} / 变更 {len(differ)} / 多余 {len(only_b)}")
        for f in (only_a + differ)[:6]:
            print(f"      ~ {f}")
        if not dry:
            if dst.exists():
                shutil.rmtree(dst)
            dst.mkdir(parents=True)
            for n in names:
                shutil.copytree(SKILLS_SRC / n, dst / n)
        return len(only_a) + len(differ) + len(only_b)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not EXPERT_SRC.is_dir():
        sys.exit(f"找不到专家源目录 {EXPERT_SRC}")
    if not SKILLS_SRC.is_dir():
        sys.exit(f"找不到技能目录 {SKILLS_SRC}")
    if not EXPERT_DST.is_dir():
        sys.exit(
            f"找不到本地专家包 {EXPERT_DST}\n"
            "先跑 init_expert.py 初始化：\n"
            '  python scripts/init_expert.py mango --type agent --path "$WORKBUDDY_CONFIG_DIR/plugins/marketplaces/my-experts/plugins"'
        )

    print(f"仓库源：{EXPERT_SRC}")
    print(f"专家包：{EXPERT_DST}")
    changed = sync_meta(args.check)
    changed += sync_skills(args.check)

    if not changed:
        print("✅ 已一致，无需同步")
        return 0
    if args.check:
        print("⚠ 有差异，跑 python scripts/sync-expert.py 同步")
        return 1
    print(f"✅ 已同步 {changed} 项")
    print("下一步：校验 + 注册 + 打包")
    print("  python scripts/validate_expert.py <expert-dir>")
    print("  python scripts/register_expert.py <expert-dir>")
    print("  python scripts/package_expert.py <expert-dir> dist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
