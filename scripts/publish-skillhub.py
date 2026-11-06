#!/usr/bin/env python3
"""把 skill/skills/ 下的 Skill 逐个发布到 SkillHub。

用法:
    export SKILLHUB_TOKEN=skh_xxx
    python scripts/publish-skillhub.py            # 先预检再发布
    python scripts/publish-skillhub.py --dry-run  # 只预检
    python scripts/publish-skillhub.py --only mangofolio-daily-hotword

Token 获取: 登录 https://skillhub.cn → 个人设置 → API Token。
脚本只从环境变量读取 token，不写盘、不落日志。
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skill" / "skills"

# Windows 下 ~/.local/bin/skillhub 是 bash wrapper，subprocess 无法直接执行；
# 优先调用底层的 Python CLI，跨平台一致。
_CLI_PY = Path.home() / ".skillhub" / "skills_store_cli.py"
CLI = [sys.executable, str(_CLI_PY)] if _CLI_PY.exists() else ["skillhub"]

CHANGELOG = "首发：芒果词库理财科普方法论 v1.0"


def run(args, token=None):
    env = os.environ.copy()
    if token:
        env["SKILLHUB_TOKEN"] = token
    # skillhub 默认装在 ~/.local/bin
    home_bin = str(Path.home() / ".local" / "bin")
    env["PATH"] = home_bin + os.pathsep + env.get("PATH", "")
    return subprocess.run(args, capture_output=True, text=True, env=env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只做本地预检，不联网")
    ap.add_argument("--only", help="只发布指定的 slug")
    ap.add_argument("--changelog", default=CHANGELOG)
    args = ap.parse_args()

    token = os.environ.get("SKILLHUB_TOKEN", "").strip()

    if not args.dry_run:
        if not token:
            print("缺少 SKILLHUB_TOKEN 环境变量（skh_ 开头）", file=sys.stderr)
            print("获取: https://skillhub.cn → 个人设置 → API Token", file=sys.stderr)
            return 2
        who = run(CLI + ["auth", "whoami"], token)
        if who.returncode != 0:
            print("登录失败:", (who.stderr or who.stdout).strip()[:300], file=sys.stderr)
            return 2

    dirs = sorted(p for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").exists())
    if args.only:
        dirs = [p for p in dirs if p.name == args.only]
        if not dirs:
            print("找不到 skill:", args.only, file=sys.stderr)
            return 2

    ok, fail = [], []
    for d in dirs:
        print("-" * 60)
        print("[%s]" % d.name)
        cmd = CLI + ["publish", str(d), "--changelog", args.changelog, "--json"]
        if args.dry_run:
            cmd.append("--dry-run")
        r = run(cmd, token)
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        if r.returncode == 0:
            print("  OK  ", out[:200])
            ok.append(d.name)
        else:
            print("  FAIL", (err or out)[:300])
            fail.append(d.name)

    print("-" * 60)
    print("成功 %d / 失败 %d" % (len(ok), len(fail)))
    if fail:
        print("失败列表:", ", ".join(fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
