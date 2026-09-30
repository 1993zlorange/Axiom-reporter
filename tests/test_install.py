"""install_adhd_rules 的最小验证：创建、幂等、追加、替换、备份、预览、技能复制。"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import install_adhd_rules as mod  # noqa: E402


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_agents_md(self):
        r = mod.install(self.target, write=True)
        self.assertEqual(r["agents_action"], "create")
        text = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(mod.BEGIN), 1)
        self.assertIn("决策点表达", text)
        self.assertTrue(r["verified"])

    def test_second_run_is_idempotent(self):
        mod.install(self.target, write=True)
        first = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        r = mod.install(self.target, write=True)
        second = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(r["agents_action"], "unchanged")
        self.assertEqual(first, second)
        self.assertIsNone(r["backup"])

    def test_appends_without_destroying_existing_content(self):
        agents = self.target / "AGENTS.md"
        agents.write_text("# 已有项目说明\n\n保留我原来的内容。\n", encoding="utf-8")
        mod.install(self.target, write=True)
        text = agents.read_text(encoding="utf-8")
        self.assertIn("保留我原来的内容。", text)
        self.assertIn(mod.BEGIN, text)
        self.assertEqual(text.index("保留我原来的内容。") < text.index(mod.BEGIN), True)

    def test_replaces_stale_marked_block(self):
        agents = self.target / "AGENTS.md"
        old = f"前言\n{mod.BEGIN}\n旧规则\n{mod.END}\n结尾\n"
        agents.write_text(old, encoding="utf-8")
        mod.install(self.target, write=True)
        text = agents.read_text(encoding="utf-8")
        self.assertNotIn("旧规则", text)
        self.assertIn("i-have-adhd 用户沟通规则", text)
        self.assertIn("前言", text)
        self.assertIn("结尾", text)

    def test_backup_created_when_modifying(self):
        agents = self.target / "AGENTS.md"
        agents.write_text("旧内容\n", encoding="utf-8")
        r = mod.install(self.target, write=True)
        backup = Path(r["backup"])
        self.assertTrue(backup.is_file())
        self.assertEqual(backup.read_text(encoding="utf-8"), "旧内容\n")

    def test_dry_run_writes_nothing(self):
        r = mod.install(self.target, write=False)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual(r["agents_action"], "create")
        self.assertFalse(r["verified"])

    def test_with_skill_copies_skill(self):
        r = mod.install(self.target, write=True, with_skill=True)
        dst = self.target / ".codex" / "skills" / "i-have-adhd" / "SKILL.md"
        self.assertTrue(dst.is_file())
        self.assertEqual(
            dst.read_text(encoding="utf-8"),
            mod.SKILL_SRC.read_text(encoding="utf-8"),
        )
        self.assertTrue(r["verified"])

    def test_skill_stays_in_sync_with_rules_block(self):
        """技能正文必须包含规则模板的全部标题，防止两份文件漂移。"""
        block = mod.read_block()
        skill = mod.SKILL_SRC.read_text(encoding="utf-8")
        for heading in ("# i-have-adhd 用户沟通规则", "## 回答方式", "## 决策点表达", "## 语言和编码", "## 交付前检查"):
            self.assertIn(heading, block)
            self.assertIn(heading, skill)


if __name__ == "__main__":
    unittest.main()
