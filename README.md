# i-have-adhd-installer

把 [i-have-adhd](https://github.com/ayghri/i-have-adhd) 的 ADHD 友好沟通规则，加上本地扩展（决策点必须给推荐+优劣比较、禁用未解释的编码和内部管理术语），一键写入任意项目的根目录 `AGENTS.md`。写入后，任何会读取项目 `AGENTS.md` 的编码助手在本项目工作时都会遵守这些规则。

## 在任何项目中的用法

在目标项目里，对编码助手粘贴下面这句话（把路径/仓库地址换成实际位置）：

```text
Install the i-have-adhd skill/plugin from /home/ubuntu/zlorange/zl_ubuntu/01-Project/i-have-adhd-installer, refer to the repo's AGENTS.md for instructions.
```

如果本项目已推送到 GitHub：

```text
Install the i-have-adhd skill/plugin from https://github.com/<你的用户名>/i-have-adhd-installer, refer to the repo's AGENTS.md for instructions.
```

助手读本项目 `AGENTS.md` 后会执行：

```bash
# 1) 预览（不写入）
python3 scripts/install_adhd_rules.py /path/to/目标项目

# 2) 确认后写入
python3 scripts/install_adhd_rules.py /path/to/目标项目 --write

# 可选：同时把技能装进目标项目 .codex/skills/
python3 scripts/install_adhd_rules.py /path/to/目标项目 --write --with-skill
```

不通过助手、手动安装也一样：在目标项目根目录运行 `python3 <本项目>/scripts/install_adhd_rules.py . --write`。

## 它会改动什么

| 文件 | 行为 |
|---|---|
| `<目标项目>/AGENTS.md` | 不存在则创建；存在则在 `<!-- i-have-adhd:begin/end -->` 标记块内写入/更新规则，原有内容保留；修改前自动备份为 `AGENTS.md.bak-时间戳` |
| `<目标项目>/.codex/skills/i-have-adhd/SKILL.md` | 仅 `--with-skill` 时复制；内容变化才覆盖，覆盖前备份 |

安全性质：默认只预览；`--write` 才写入；幂等（重复运行显示 `unchanged`，不重复追加）；不删除、不覆盖标记块以外的任何内容。

## 规则内容

规则正文在 `assets/agents-block.md`（安装进目标项目的就是这份），技能副本在 `skills/i-have-adhd/SKILL.md`。内容 = 上游 10 条 ADHD 友好规则 + 本地 3 项扩展：决策点先给推荐方案和原因、每个方案比较好处/代价或风险/适合情况、不使用未解释的编码和项目管理术语（冻结、启动门、证据链、回退、合同/契约等都给日常说法替代）。

## 验证

```bash
python3 -m unittest discover -s tests -v
```

## 卸载/回退

1. 删除目标项目 `AGENTS.md` 中 `<!-- i-have-adhd:begin -->` 到 `<!-- i-have-adhd:end -->` 的整块（含标记行）；
2. 或恢复安装前自动生成的 `AGENTS.md.bak-时间戳`；
3. `--with-skill` 安装的技能删除 `<目标项目>/.codex/skills/i-have-adhd/` 即可。

## 许可

MIT，见 `LICENSE`。规则改编自上游 [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)（MIT）。
