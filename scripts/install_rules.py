#!/usr/bin/env python3
"""把 Axiom-reporter 用户沟通规则安装到任意目标项目根目录的 AGENTS.md。

默认只预览，不写入；提供 --write 才真正修改。幂等：重复安装不产生重复内容，
已存在的用户内容只追加不覆盖，修改前自动备份。退出码见 main()。
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

BEGIN = "<!-- Axiom-reporter:begin -->"
END = "<!-- Axiom-reporter:end -->"
# 旧版本安装器留下的标记；升级时原地替换，避免重复追加
LEGACY_BEGIN = "<!-- i-have-adhd:begin -->"
LEGACY_END = "<!-- i-have-adhd:end -->"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BLOCK_PATH = PROJECT_ROOT / "assets" / "agents-block.md"
SKILL_SRC = PROJECT_ROOT / "skills" / "Axiom-reporter" / "SKILL.md"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_block() -> str:
    if not BLOCK_PATH.is_file():
        raise FileNotFoundError(f"规则模板不存在：{BLOCK_PATH}")
    return BLOCK_PATH.read_text(encoding="utf-8").strip() + "\n"


def render(block: str) -> str:
    return f"{BEGIN}\n{block.strip()}\n{END}\n"


def _find_block(text: str) -> tuple[int, int, str] | None:
    """定位当前或旧版标记块，返回 (起始下标, 结束下标, 块内容)。"""
    candidates = []
    for b, e in ((BEGIN, END), (LEGACY_BEGIN, LEGACY_END)):
        if b in text and e in text:
            bi = text.index(b)
            ei = text.index(e) + len(e)
            if ei > bi:
                inner = text[bi + len(b): text.index(e)]
                candidates.append((bi, ei, inner.strip()))
    return min(candidates, key=lambda c: c[0]) if candidates else None


def extract_marked(text: str) -> str | None:
    """返回现有标记块内容（不含标记行）；无标记或标记不完整时返回 None。"""
    found = _find_block(text)
    return found[2] if found else None


def _backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.bak-{stamp}")
    counter = 1
    while backup.exists():
        backup = path.with_name(f"{path.name}.bak-{stamp}-{counter}")
        counter += 1
    shutil.copy2(path, backup)
    return backup


def install(target: Path, *, write: bool = False, with_skill: bool = False) -> dict:
    """执行安装并返回结果字典。write=False 时只预览。"""
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise NotADirectoryError(f"目标不是有效目录：{target}")

    block = read_block()
    rendered = render(block)
    agents = target / "AGENTS.md"
    result: dict = {
        "target": str(target),
        "agents_path": str(agents),
        "agents_action": None,
        "backup": None,
        "skill_action": None,
        "skill_path": None,
        "verified": False,
        "write": write,
    }

    # 1) 计算目标 AGENTS.md 的新内容
    if agents.exists():
        old = agents.read_text(encoding="utf-8")
        found = _find_block(old)
        if found is not None:
            begin_idx, end_idx, inner = found
            if inner == block.strip() and old[begin_idx: begin_idx + len(BEGIN)] == BEGIN:
                result["agents_action"] = "unchanged"
                new_text = old
            else:
                suffix = old[end_idx:].lstrip("\n")
                new_text = old[:begin_idx] + rendered.rstrip("\n") + ("\n" + suffix if suffix else "\n")
                result["agents_action"] = "replace-marked-block"
        else:
            separator = "" if old.endswith("\n\n") else ("\n" if old.endswith("\n") else "\n\n")
            new_text = old + separator + rendered
            result["agents_action"] = "append-marked-block"
    else:
        new_text = rendered
        result["agents_action"] = "create"

    # 2) 技能复制计划（可选）
    skill_dst = target / ".codex" / "skills" / "Axiom-reporter" / "SKILL.md"
    if with_skill:
        result["skill_path"] = str(skill_dst)
        if skill_dst.exists() and skill_dst.read_text(encoding="utf-8") == SKILL_SRC.read_text(encoding="utf-8"):
            result["skill_action"] = "unchanged"
        else:
            result["skill_action"] = "create-or-update"

    if not write:
        return result

    # 3) 写入 AGENTS.md（变更前备份）
    if result["agents_action"] != "unchanged":
        if agents.exists():
            result["backup"] = str(_backup(agents))
        agents.write_text(new_text, encoding="utf-8")

    # 4) 写入技能副本（可选，变更前备份）
    if with_skill and result["skill_action"] == "create-or-update":
        skill_dst.parent.mkdir(parents=True, exist_ok=True)
        if skill_dst.exists():
            result["skill_backup"] = str(_backup(skill_dst))
        shutil.copy2(SKILL_SRC, skill_dst)

    # 5) 写入后验证
    written = agents.read_text(encoding="utf-8")
    ok = (
        written.count(BEGIN) == 1
        and written.count(END) == 1
        and extract_marked(written) is not None
        and extract_marked(written).strip() == block.strip()
    )
    if with_skill:
        ok = ok and skill_dst.is_file() and skill_dst.read_text(encoding="utf-8") == SKILL_SRC.read_text(encoding="utf-8")
    result["verified"] = bool(ok)
    if not ok:
        raise RuntimeError("写入后验证失败：标记块或技能副本与模板不一致")
    return result


def _print_result(r: dict) -> None:
    mode = "已写入" if r["write"] else "预览（未写入）"
    print(f"结论：{mode}。AGENTS.md 动作：{r['agents_action']}。")
    print(f"目标：{r['agents_path']}")
    if r.get("backup"):
        print(f"备份：{r['backup']}")
    if r.get("skill_action"):
        print(f"技能副本：{r['skill_action']} -> {r['skill_path']}")
    if r["write"]:
        print(f"验证：{'通过' if r['verified'] else '失败'}")
    print("下一步：" + ("重新运行可确认幂等（应显示 unchanged）。" if r["write"] else "确认无误后加 --write 执行。"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把 Axiom-reporter 用户沟通规则写入目标项目根目录 AGENTS.md（默认预览，--write 才写入）"
    )
    parser.add_argument("target", nargs="?", default=".", help="目标项目路径，默认当前目录")
    parser.add_argument("--write", action="store_true", help="实际写入（默认只预览）")
    parser.add_argument("--with-skill", action="store_true", help="同时复制 skills/Axiom-reporter 到目标项目 .codex/skills/")
    args = parser.parse_args(argv)

    try:
        result = install(Path(args.target), write=args.write, with_skill=args.with_skill)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(f"无法安装：{exc}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 2
    _print_result(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
