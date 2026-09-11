---
name: jielibang
description: 本地任务进度接力技能。用户说“接力棒”“保存会话进度”“接着上次继续”“列出可以继续的任务”，或需要防止 Codex 会话崩溃、上下文耗尽、重开会话后丢失工作进度时使用。把目标、完成项、文件变更、测试、阻塞和下一步原子写入当前工作区的 .codex-handoff，并在新会话核对真实文件后恢复执行。
---

# 接力棒

把每个工作区的任务进度保存成可恢复的本地检查点。检查点是辅助记忆，不代替真实文件、Git 状态和测试结果。

## 固定脚本

```powershell
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" <命令>
```

数据保存在当前工作区的 `.codex-handoff/`：

- `index.json`：任务列表和当前任务书签。
- `tasks/<id>.md`：每个任务的最新进度。
- `history/<id>/`：旧版本快照。

脚本会尽量把 `.codex-handoff/` 加入本地 Git exclude，避免污染提交。

## 触发口令

- `接力棒，保存` / `保存会话进度`：保存当前任务。
- `接力棒，继续` / `接着上次继续`：恢复当前工作区最近任务。
- `接力棒，列出` / `列出可以继续的任务`：列出任务。
- `继续“任务名”`：恢复指定任务。
- `接力棒，归档当前任务`：归档但不删除历史。

## 自动留档规则

对需要操作文件、运行命令或持续多轮的具体任务，不等待用户手动要求：

1. 接受任务并确定目标后，创建首次检查点。
2. 完成一个计划步骤、修改一批文件、跑完测试、发现关键错误后更新检查点。
3. 执行长时间、易失败或可能中断的动作前先更新一次。
4. 给出任务阶段性或最终回复前更新一次。
5. 纯问答、闲聊、翻译和未落地的简单咨询不创建检查点。

崩溃发生后无法保存“尚未写盘”的内容，因此要靠上述关键节点自动留档，把损失限制在最后一个检查点之后。

## 保存流程

先生成临时 JSON 文件，字段见 `references/checkpoint-schema.md`，然后执行：

```powershell
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" save --workspace "<工作区绝对路径>" --input "<JSON绝对路径>"
```

保存成功后删除临时 JSON。不得把密码、Token、Cookie、私钥、完整个人隐私或其他秘密写进检查点；只写“需要某密钥”而不写值。

## 恢复流程

读取当前任务：

```powershell
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" show --workspace "<工作区绝对路径>"
```

读取指定任务：

```powershell
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" show --workspace "<工作区绝对路径>" --task "<任务名>"
```

恢复后必须：

1. 检查检查点列出的文件是否存在。
2. 查看当前 Git 状态或相关文件内容。
3. 必要时重跑最近的测试。
4. 明确说明“记录内容”和“实际文件”是否一致。
5. 从 `下一步` 继续，不重复已完成工作。

## 列出与归档

```powershell
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" list --workspace "<工作区绝对路径>"
python "C:\Users\win10\.codex\skills\jielibang\scripts\handoff.py" archive --workspace "<工作区绝对路径>" --task "<任务名或ID>"
```

如果没有检查点，直接说明当前工作区尚无可恢复任务，然后按用户的新目标创建任务，不要假装恢复成功。
