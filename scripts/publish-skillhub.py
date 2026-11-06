#!/usr/bin/env python3
"""把 skill/skills/ 下的 Skill 逐个发布到 SkillHub。

用法:
    export SKILLHUB_TOKEN=skh_xxx
    python scripts/publish-skillhub.py                 # 逐个发布（默认间隔 12s 防限流）
    python scripts/publish-skillhub.py --dry-run       # 只预检
    python scripts/publish-skillhub.py --only <slug>   # 只发一个
    python scripts/publish-skillhub.py --delay 20      # 调整间隔

Token 获取: 登录 https://skillhub.cn → 个人设置 → API Token。
脚本只从环境变量读取 token，不写盘、不落日志。

平台行为备注:
- 同 slug 同 version 不可重复发布（409 VERSION_EXISTS）→ 视为已发布，跳过
- 连续发布触发限流（429 RATE_LIMITED）→ 退避重试
"""
import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skill" / "skills"

# Windows 下 ~/.local/bin/skillhub 是 bash wrapper，subprocess 无法直接执行；
# 优先调用底层 Python CLI，跨平台一致。
_CLI_PY = Path.home() / ".skillhub" / "skills_store_cli.py"
CLI = [sys.executable, str(_CLI_PY)] if _CLI_PY.exists() else ["skillhub"]

DEFAULT_CHANGELOG = "词条真实性修正、新增词条索引校验、触发词收敛去重"


def run(args, token=None):
    env = os.environ.copy()
    if token:
        env["SKILLHUB_TOKEN"] = token
    env["PATH"] = str(Path.home() / ".local" / "bin") + os.pathsep + env.get("PATH", "")
    return subprocess.run(args, capture_output=True, text=True, env=env)


def classify(err_text):
    """从失败输出里判断错误类型。"""
    if "VERSION_EXISTS" in err_text or "已存在" in err_text:
        return "exists"
    if "RATE_LIMITED" in err_text or "频率过高" in err_text or "429" in err_text:
        return "rate"
    return "other"


def publish_one(d, token, changelog, dry_run=False, retries=4, backoff=25):
    cmd = CLI + ["publish", str(d), "--changelog", changelog, "--json"]
    if dry_run:
        cmd.append("--dry-run")

    for attempt in range(retries + 1):
        r = run(cmd, token)
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        if r.returncode == 0:
            return "ok", out
        kind = classify(err + out)
        if kind == "exists":
            return "exists", err or out
        if kind == "rate" and attempt < retries:
            wait = backoff * (attempt + 1)
            print("  429 限流，%ds 后重试（第 %d/%d 次）" % (wait, attempt + 1, retries))
            time.sleep(wait)
            continue
        return "fail", err or out
    return "fail", "已达最大重试次数"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只做本地预检，不联网")
    ap.add_argument("--only", help="只发布指定的 slug")
    ap.add_argument("--changelog", default=DEFAULT_CHANGELOG)
    ap.add_argument("--delay", type=int, default=12, help="每个 Skill 之间的间隔秒数")
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

    buckets = {"ok": [], "exists": [], "fail": []}
    for i, d in enumerate(dirs):
        print("-" * 60)
        print("[%s]" % d.name)
        status, detail = publish_one(d, token, args.changelog, args.dry_run)
        buckets[status].append(d.name)
        if status == "ok":
            m = re.search(r'"fileCount":\s*(\d+)', detail)
            extra = "（%s 个文件）" % m.group(1) if m else ""
            print("  已发布 %s" % extra)
        elif status == "exists":
            print("  跳过：该版本已发布过")
        else:
            print("  失败：", detail[:300])

        if not args.dry_run and i < len(dirs) - 1:
            time.sleep(args.delay)

    print("=" * 60)
    print("新发布 %d / 已存在 %d / 失败 %d" % (len(buckets["ok"]), len(buckets["exists"]), len(buckets["fail"])))
    if buckets["fail"]:
        print("失败列表:", ", ".join(buckets["fail"]))
    return 0 if not buckets["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
