# 检查点 JSON 格式

最小示例：

```json
{
  "task": "开发个人网站",
  "objective": "完成可运行的个人网站",
  "status": "in_progress",
  "completed": ["创建项目", "完成首页"],
  "next": ["制作作品展示区域"],
  "files": ["src/App.tsx", "src/index.css"],
  "tests": ["npm test：通过"],
  "blockers": [],
  "decisions": ["使用现有 React 项目，不重建脚手架"],
  "notes": ["新会话恢复时先检查 git status"]
}
```

字段：

- `task`：稳定、易认的任务名，必填。
- `objective`：最终要交付什么，必填。
- `status`：`in_progress`、`blocked`、`complete` 或 `paused`。
- `completed`：已确认完成的事项。
- `next`：按顺序列出下一步，至少一项（完成任务可为空）。
- `files`：改动或关键文件，尽量使用工作区相对路径。
- `tests`：执行过的验证与结果，不能把未运行写成通过。
- `blockers`：真实阻塞。
- `decisions`：重要选择及原因。
- `notes`：恢复时需要注意的信息。

禁止记录秘密值。每次保存应反映真实状态，不能只复制旧内容。
