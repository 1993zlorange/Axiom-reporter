# Axiom-reporter

一套可直接安装到任意项目的对话规则：结论和下一步动作先行、多步骤编号、每轮重申进度、一次只处理一个主要问题、决策点先给推荐方案并比较优劣、不使用未解释的编码和内部管理术语。安装后，任何会读取项目 `AGENTS.md` 的编码助手在该项目中工作时都会遵守这些规则。

## 在任何项目中的用法

在目标项目里，对编码助手粘贴下面这句话：

```text
把 Axiom-reporter 技能安装到当前项目，来源：/home/ubuntu/zlorange/zl_ubuntu/01-Project/Axiom-reporter，先读该仓库的 AGENTS.md 并按说明执行。
```

如果本项目已推送到 GitHub，把来源换成仓库地址即可：

```text
把 Axiom-reporter 技能安装到当前项目，来源：https://github.com/<你的用户名>/Axiom-reporter，先读该仓库的 AGENTS.md 并按说明执行。
```

助手会按本仓库 `AGENTS.md` 的流程执行，等价于：

```bash
# 1) 预览（不写入）
python3 scripts/install_rules.py /path/to/目标项目

# 2) 确认后写入
python3 scripts/install_rules.py /path/to/目标项目 --write

# 可选：同时把技能装进目标项目 .codex/skills/
python3 scripts/install_rules.py /path/to/目标项目 --write --with-skill
```

手动安装也一样：在目标项目根目录运行 `python3 <本仓库>/scripts/install_rules.py . --write`。

## 它会改动什么

| 文件 | 行为 |
|---|---|
| `<目标项目>/AGENTS.md` | 不存在则创建；存在则在 `<!-- Axiom-reporter:begin/end -->` 标记块内写入/更新规则，原有内容保留；修改前自动备份为 `AGENTS.md.bak-时间戳` |
| `<目标项目>/.codex/skills/Axiom-reporter/SKILL.md` | 仅 `--with-skill` 时复制；内容变化才覆盖，覆盖前备份 |

安全性质：默认只预览；`--write` 才写入；幂等（重复运行显示 `unchanged`，不重复追加）；不删除、不覆盖标记块以外的任何内容。

## 规则内容

规则正文在 `assets/agents-block.md`（安装进目标项目的就是这份），技能副本在 `skills/Axiom-reporter/SKILL.md`，共 5 个部分：

1. 回答方式：结论先行、编号步骤、重申进度、压制旁支、具体时间估计、让进展可见、报错按“现象/原因/处理办法”、每组列表不超过 5 项、不写客套。
2. 决策点表达：先说要决定什么 → 给推荐方案 → 说明原因 → 比较 2–3 个真实方案的好处、代价或风险、适合情况 → 给出下一步；数据不足时明说，不把猜测写成结论。
3. 语言和编码：只用当前专业领域常用词；不使用未解释的缩写、代号或内部编号；专业必需术语第一次出现时用一句话解释。
4. 常见内部说法的日常替代：冻结、启动门、证据链、回退、合同/契约、工作包、基线等词均给出日常说法。
5. 交付前检查：第一行是否直接给出结论或下一步、决策点是否完整、是否还有未解释术语、是否把猜测写成结论。

两份文件由测试保证标题同步，改规则先改 `assets/agents-block.md`，再同步技能副本。

## 验证

```bash
python3 -m unittest discover -s tests -v
```

共 9 项测试：创建、幂等、追加不破坏原文、替换旧块、旧标记原地升级、备份、预览不写入、技能复制、两份规则文件同步检查。

## 卸载/回退

1. 删除目标项目 `AGENTS.md` 中 `<!-- Axiom-reporter:begin -->` 到 `<!-- Axiom-reporter:end -->` 的整块（含标记行）；
2. 或恢复安装前自动生成的 `AGENTS.md.bak-时间戳`；
3. `--with-skill` 安装的技能删除 `<目标项目>/.codex/skills/Axiom-reporter/` 即可。

## 许可

MIT，见 `LICENSE`。
