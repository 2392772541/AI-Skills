# 技能库整理迁移执行计划 (Migration Plan)

统一技能总库目标路径：`D:\AI-Skills`

## 迁移规则概要
1. **保留唯一及推荐技能**：直接复制到 `D:\AI-Skills\<技能类型>\<技能文件夹>` 下，原名保持不变。
2. **归档重复及废弃版本**：统一复制到 `D:\AI-Skills\archived\<技能类型>\<技能名_来自_父目录名>` 目录下，确保完全不覆盖任何同名冲突文件，且原文件不被删除。
3. **保留原始来源说明**：迁移完成后将在日志中保存所有原始路径，保证数据安全与溯源。

## 详细迁移路径比对表

| 技能名称 | 技能类型 | 处理动作 | 修改时间 | 原始路径 | 目标路径 | 备注说明 |
| --- | --- | --- | --- | --- | --- | --- |
| find-skills | 其他 | ⭐ 保留 (Keep) | 2026-06-19 13:28:08 | `C:\Users\win10\.cc-switch\skills\find-skills\SKILL.md` | `D:\AI-Skills\其他\find-skills` | 推荐保留版本（修改时间最新） |
| find-skills | 其他 | 📦 归档 (Archive) | 2026-06-19 13:28:08 | `C:\Users\win10\.claude\skills\find-skills\SKILL.md` | `D:\AI-Skills\archived\其他\find-skills_from_skills` | 重复或旧版本，移动到 archived |
| find-skills | 其他 | 📦 归档 (Archive) | 2026-06-19 13:28:08 | `C:\Users\win10\.hermes\skills\find-skills\SKILL.md` | `D:\AI-Skills\archived\其他\find-skills_from_skills` | 重复或旧版本，移动到 archived |
| find-skills | 其他 | 📦 归档 (Archive) | 2026-06-03 11:15:33 | `C:\Users\win10\.agents\skills\find-skills\SKILL.md` | `D:\AI-Skills\archived\其他\find-skills_from_skills` | 重复或旧版本，移动到 archived |
| gsap-core | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:09 | `C:\Users\win10\.cc-switch\skills\gsap-core\SKILL.md` | `D:\AI-Skills\设计\gsap-core` | 推荐保留版本（修改时间最新） |
| gsap-core | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:09 | `C:\Users\win10\.hermes\skills\gsap-core\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-core_from_skills` | 重复或旧版本，移动到 archived |
| gsap-core | 设计 | 📦 归档 (Archive) | 2026-06-03 11:13:00 | `C:\Users\win10\.agents\skills\gsap-core\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-core_from_skills` | 重复或旧版本，移动到 archived |
| gsap-performance | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:09 | `C:\Users\win10\.cc-switch\skills\gsap-performance\SKILL.md` | `D:\AI-Skills\设计\gsap-performance` | 推荐保留版本（修改时间最新） |
| gsap-performance | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:09 | `C:\Users\win10\.hermes\skills\gsap-performance\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-performance_from_skills` | 重复或旧版本，移动到 archived |
| gsap-performance | 设计 | 📦 归档 (Archive) | 2026-06-03 11:13:00 | `C:\Users\win10\.agents\skills\gsap-performance\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-performance_from_skills` | 重复或旧版本，移动到 archived |
| gsap-react | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:10 | `C:\Users\win10\.cc-switch\skills\gsap-react\SKILL.md` | `D:\AI-Skills\设计\gsap-react` | 推荐保留版本（修改时间最新） |
| gsap-react | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:10 | `C:\Users\win10\.hermes\skills\gsap-react\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-react_from_skills` | 重复或旧版本，移动到 archived |
| gsap-react | 设计 | 📦 归档 (Archive) | 2026-06-03 11:13:00 | `C:\Users\win10\.agents\skills\gsap-react\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-react_from_skills` | 重复或旧版本，移动到 archived |
| gsap-scrolltrigger | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:10 | `C:\Users\win10\.cc-switch\skills\gsap-scrolltrigger\SKILL.md` | `D:\AI-Skills\设计\gsap-scrolltrigger` | 推荐保留版本（修改时间最新） |
| gsap-scrolltrigger | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:10 | `C:\Users\win10\.hermes\skills\gsap-scrolltrigger\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-scrolltrigger_from_skills` | 重复或旧版本，移动到 archived |
| gsap-scrolltrigger | 设计 | 📦 归档 (Archive) | 2026-06-03 11:13:00 | `C:\Users\win10\.agents\skills\gsap-scrolltrigger\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-scrolltrigger_from_skills` | 重复或旧版本，移动到 archived |
| gsap-timeline | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:11 | `C:\Users\win10\.cc-switch\skills\gsap-timeline\SKILL.md` | `D:\AI-Skills\设计\gsap-timeline` | 推荐保留版本（修改时间最新） |
| gsap-timeline | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:11 | `C:\Users\win10\.hermes\skills\gsap-timeline\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-timeline_from_skills` | 重复或旧版本，移动到 archived |
| gsap-timeline | 设计 | 📦 归档 (Archive) | 2026-06-03 11:13:00 | `C:\Users\win10\.agents\skills\gsap-timeline\SKILL.md` | `D:\AI-Skills\archived\设计\gsap-timeline_from_skills` | 重复或旧版本，移动到 archived |
| lark-approval | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:12 | `C:\Users\win10\.cc-switch\skills\lark-approval\SKILL.md` | `D:\AI-Skills\知识库\lark-approval` | 推荐保留版本（修改时间最新） |
| lark-approval | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:12 | `C:\Users\win10\.claude\skills\lark-approval\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-approval_from_skills` | 重复或旧版本，移动到 archived |
| lark-approval | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:12 | `C:\Users\win10\.hermes\skills\lark-approval\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-approval_from_skills` | 重复或旧版本，移动到 archived |
| lark-approval | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-approval\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-approval_from_skills` | 重复或旧版本，移动到 archived |
| lark-approval | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-approval\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-approval_from_skills` | 重复或旧版本，移动到 archived |
| lark-apps | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:14 | `C:\Users\win10\.cc-switch\skills\lark-apps\SKILL.md` | `D:\AI-Skills\知识库\lark-apps` | 推荐保留版本（修改时间最新） |
| lark-apps | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:14 | `C:\Users\win10\.claude\skills\lark-apps\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-apps_from_skills` | 重复或旧版本，移动到 archived |
| lark-apps | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:14 | `C:\Users\win10\.hermes\skills\lark-apps\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-apps_from_skills` | 重复或旧版本，移动到 archived |
| lark-apps | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-apps\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-apps_from_skills` | 重复或旧版本，移动到 archived |
| lark-apps | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-apps\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-apps_from_skills` | 重复或旧版本，移动到 archived |
| lark-attendance | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:16 | `C:\Users\win10\.cc-switch\skills\lark-attendance\SKILL.md` | `D:\AI-Skills\知识库\lark-attendance` | 推荐保留版本（修改时间最新） |
| lark-attendance | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:16 | `C:\Users\win10\.claude\skills\lark-attendance\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-attendance_from_skills` | 重复或旧版本，移动到 archived |
| lark-attendance | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:16 | `C:\Users\win10\.hermes\skills\lark-attendance\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-attendance_from_skills` | 重复或旧版本，移动到 archived |
| lark-attendance | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-attendance\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-attendance_from_skills` | 重复或旧版本，移动到 archived |
| lark-attendance | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-attendance\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-attendance_from_skills` | 重复或旧版本，移动到 archived |
| lark-base | 工作流 | ⭐ 保留 (Keep) | 2026-06-19 13:28:17 | `C:\Users\win10\.cc-switch\skills\lark-base\SKILL.md` | `D:\AI-Skills\工作流\lark-base` | 推荐保留版本（修改时间最新） |
| lark-base | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:17 | `C:\Users\win10\.claude\skills\lark-base\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-base_from_skills` | 重复或旧版本，移动到 archived |
| lark-base | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:17 | `C:\Users\win10\.hermes\skills\lark-base\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-base_from_skills` | 重复或旧版本，移动到 archived |
| lark-base | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-base\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-base_from_skills` | 重复或旧版本，移动到 archived |
| lark-base | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-base\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-base_from_skills` | 重复或旧版本，移动到 archived |
| lark-calendar | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:19 | `C:\Users\win10\.cc-switch\skills\lark-calendar\SKILL.md` | `D:\AI-Skills\知识库\lark-calendar` | 推荐保留版本（修改时间最新） |
| lark-calendar | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:19 | `C:\Users\win10\.claude\skills\lark-calendar\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-calendar_from_skills` | 重复或旧版本，移动到 archived |
| lark-calendar | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:19 | `C:\Users\win10\.hermes\skills\lark-calendar\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-calendar_from_skills` | 重复或旧版本，移动到 archived |
| lark-calendar | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-calendar\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-calendar_from_skills` | 重复或旧版本，移动到 archived |
| lark-calendar | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-calendar\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-calendar_from_skills` | 重复或旧版本，移动到 archived |
| lark-contact | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:21 | `C:\Users\win10\.cc-switch\skills\lark-contact\SKILL.md` | `D:\AI-Skills\知识库\lark-contact` | 推荐保留版本（修改时间最新） |
| lark-contact | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:21 | `C:\Users\win10\.claude\skills\lark-contact\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-contact_from_skills` | 重复或旧版本，移动到 archived |
| lark-contact | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:21 | `C:\Users\win10\.hermes\skills\lark-contact\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-contact_from_skills` | 重复或旧版本，移动到 archived |
| lark-contact | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-contact\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-contact_from_skills` | 重复或旧版本，移动到 archived |
| lark-contact | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-contact\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-contact_from_skills` | 重复或旧版本，移动到 archived |
| lark-doc | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:22 | `C:\Users\win10\.cc-switch\skills\lark-doc\SKILL.md` | `D:\AI-Skills\知识库\lark-doc` | 推荐保留版本（修改时间最新） |
| lark-doc | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:22 | `C:\Users\win10\.claude\skills\lark-doc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-doc_from_skills` | 重复或旧版本，移动到 archived |
| lark-doc | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:22 | `C:\Users\win10\.hermes\skills\lark-doc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-doc_from_skills` | 重复或旧版本，移动到 archived |
| lark-doc | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-doc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-doc_from_skills` | 重复或旧版本，移动到 archived |
| lark-doc | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-doc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-doc_from_skills` | 重复或旧版本，移动到 archived |
| lark-drive | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:24 | `C:\Users\win10\.cc-switch\skills\lark-drive\SKILL.md` | `D:\AI-Skills\设计\lark-drive` | 推荐保留版本（修改时间最新） |
| lark-drive | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:24 | `C:\Users\win10\.claude\skills\lark-drive\SKILL.md` | `D:\AI-Skills\archived\设计\lark-drive_from_skills` | 重复或旧版本，移动到 archived |
| lark-drive | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:24 | `C:\Users\win10\.hermes\skills\lark-drive\SKILL.md` | `D:\AI-Skills\archived\设计\lark-drive_from_skills` | 重复或旧版本，移动到 archived |
| lark-drive | 设计 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-drive\SKILL.md` | `D:\AI-Skills\archived\设计\lark-drive_from_skills` | 重复或旧版本，移动到 archived |
| lark-drive | 设计 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-drive\SKILL.md` | `D:\AI-Skills\archived\设计\lark-drive_from_skills` | 重复或旧版本，移动到 archived |
| lark-event | 设计 | ⭐ 保留 (Keep) | 2026-06-19 13:28:26 | `C:\Users\win10\.cc-switch\skills\lark-event\SKILL.md` | `D:\AI-Skills\设计\lark-event` | 推荐保留版本（修改时间最新） |
| lark-event | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:26 | `C:\Users\win10\.claude\skills\lark-event\SKILL.md` | `D:\AI-Skills\archived\设计\lark-event_from_skills` | 重复或旧版本，移动到 archived |
| lark-event | 设计 | 📦 归档 (Archive) | 2026-06-19 13:28:26 | `C:\Users\win10\.hermes\skills\lark-event\SKILL.md` | `D:\AI-Skills\archived\设计\lark-event_from_skills` | 重复或旧版本，移动到 archived |
| lark-event | 设计 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-event\SKILL.md` | `D:\AI-Skills\archived\设计\lark-event_from_skills` | 重复或旧版本，移动到 archived |
| lark-event | 设计 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052826_lark-event\skill\SKILL.md` | `D:\AI-Skills\archived\设计\skill_from_20260619_052826_lark-event` | 重复或旧版本，移动到 archived |
| lark-im | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:28 | `C:\Users\win10\.cc-switch\skills\lark-im\SKILL.md` | `D:\AI-Skills\知识库\lark-im` | 推荐保留版本（修改时间最新） |
| lark-im | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:28 | `C:\Users\win10\.claude\skills\lark-im\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-im_from_skills` | 重复或旧版本，移动到 archived |
| lark-im | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:28 | `C:\Users\win10\.hermes\skills\lark-im\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-im_from_skills` | 重复或旧版本，移动到 archived |
| lark-im | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-im\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-im_from_skills` | 重复或旧版本，移动到 archived |
| lark-im | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052828_lark-im\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052828_lark-im` | 重复或旧版本，移动到 archived |
| lark-im | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-im\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-im_from_skills` | 重复或旧版本，移动到 archived |
| lark-mail | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:30 | `C:\Users\win10\.cc-switch\skills\lark-mail\SKILL.md` | `D:\AI-Skills\知识库\lark-mail` | 推荐保留版本（修改时间最新） |
| lark-mail | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:30 | `C:\Users\win10\.claude\skills\lark-mail\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-mail_from_skills` | 重复或旧版本，移动到 archived |
| lark-mail | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:30 | `C:\Users\win10\.hermes\skills\lark-mail\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-mail_from_skills` | 重复或旧版本，移动到 archived |
| lark-mail | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-mail\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-mail_from_skills` | 重复或旧版本，移动到 archived |
| lark-mail | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052830_lark-mail\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052830_lark-mail` | 重复或旧版本，移动到 archived |
| lark-mail | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-mail\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-mail_from_skills` | 重复或旧版本，移动到 archived |
| lark-markdown | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:31 | `C:\Users\win10\.cc-switch\skills\lark-markdown\SKILL.md` | `D:\AI-Skills\知识库\lark-markdown` | 推荐保留版本（修改时间最新） |
| lark-markdown | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:31 | `C:\Users\win10\.claude\skills\lark-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-markdown_from_skills` | 重复或旧版本，移动到 archived |
| lark-markdown | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:31 | `C:\Users\win10\.hermes\skills\lark-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-markdown_from_skills` | 重复或旧版本，移动到 archived |
| lark-markdown | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-markdown_from_skills` | 重复或旧版本，移动到 archived |
| lark-markdown | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052832_lark-markdown\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052832_lark-markdown` | 重复或旧版本，移动到 archived |
| lark-markdown | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-markdown_from_skills` | 重复或旧版本，移动到 archived |
| lark-minutes | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:33 | `C:\Users\win10\.cc-switch\skills\lark-minutes\SKILL.md` | `D:\AI-Skills\知识库\lark-minutes` | 推荐保留版本（修改时间最新） |
| lark-minutes | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:33 | `C:\Users\win10\.claude\skills\lark-minutes\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-minutes_from_skills` | 重复或旧版本，移动到 archived |
| lark-minutes | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:33 | `C:\Users\win10\.hermes\skills\lark-minutes\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-minutes_from_skills` | 重复或旧版本，移动到 archived |
| lark-minutes | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-minutes\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-minutes_from_skills` | 重复或旧版本，移动到 archived |
| lark-minutes | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052833_lark-minutes\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052833_lark-minutes` | 重复或旧版本，移动到 archived |
| lark-minutes | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-minutes\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-minutes_from_skills` | 重复或旧版本，移动到 archived |
| lark-okr | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:35 | `C:\Users\win10\.cc-switch\skills\lark-okr\SKILL.md` | `D:\AI-Skills\知识库\lark-okr` | 推荐保留版本（修改时间最新） |
| lark-okr | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:35 | `C:\Users\win10\.claude\skills\lark-okr\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-okr_from_skills` | 重复或旧版本，移动到 archived |
| lark-okr | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:35 | `C:\Users\win10\.hermes\skills\lark-okr\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-okr_from_skills` | 重复或旧版本，移动到 archived |
| lark-okr | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-okr\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-okr_from_skills` | 重复或旧版本，移动到 archived |
| lark-okr | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052835_lark-okr\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052835_lark-okr` | 重复或旧版本，移动到 archived |
| lark-okr | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-okr\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-okr_from_skills` | 重复或旧版本，移动到 archived |
| lark-openapi-explorer | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:37 | `C:\Users\win10\.cc-switch\skills\lark-openapi-explorer\SKILL.md` | `D:\AI-Skills\知识库\lark-openapi-explorer` | 推荐保留版本（修改时间最新） |
| lark-openapi-explorer | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:37 | `C:\Users\win10\.claude\skills\lark-openapi-explorer\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-openapi-explorer_from_skills` | 重复或旧版本，移动到 archived |
| lark-openapi-explorer | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:37 | `C:\Users\win10\.hermes\skills\lark-openapi-explorer\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-openapi-explorer_from_skills` | 重复或旧版本，移动到 archived |
| lark-openapi-explorer | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-openapi-explorer\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-openapi-explorer_from_skills` | 重复或旧版本，移动到 archived |
| lark-openapi-explorer | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052837_lark-openapi-explorer\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052837_lark-openapi-explorer` | 重复或旧版本，移动到 archived |
| lark-openapi-explorer | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-openapi-explorer\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-openapi-explorer_from_skills` | 重复或旧版本，移动到 archived |
| lark-shared | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:38 | `C:\Users\win10\.cc-switch\skills\lark-shared\SKILL.md` | `D:\AI-Skills\知识库\lark-shared` | 推荐保留版本（修改时间最新） |
| lark-shared | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:38 | `C:\Users\win10\.claude\skills\lark-shared\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-shared_from_skills` | 重复或旧版本，移动到 archived |
| lark-shared | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:38 | `C:\Users\win10\.hermes\skills\lark-shared\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-shared_from_skills` | 重复或旧版本，移动到 archived |
| lark-shared | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-shared\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-shared_from_skills` | 重复或旧版本，移动到 archived |
| lark-shared | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052838_lark-shared\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052838_lark-shared` | 重复或旧版本，移动到 archived |
| lark-shared | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-shared\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-shared_from_skills` | 重复或旧版本，移动到 archived |
| lark-sheets | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:40 | `C:\Users\win10\.cc-switch\skills\lark-sheets\SKILL.md` | `D:\AI-Skills\知识库\lark-sheets` | 推荐保留版本（修改时间最新） |
| lark-sheets | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:40 | `C:\Users\win10\.claude\skills\lark-sheets\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-sheets_from_skills` | 重复或旧版本，移动到 archived |
| lark-sheets | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:40 | `C:\Users\win10\.hermes\skills\lark-sheets\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-sheets_from_skills` | 重复或旧版本，移动到 archived |
| lark-sheets | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-sheets\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-sheets_from_skills` | 重复或旧版本，移动到 archived |
| lark-sheets | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052840_lark-sheets\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052840_lark-sheets` | 重复或旧版本，移动到 archived |
| lark-sheets | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-sheets\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-sheets_from_skills` | 重复或旧版本，移动到 archived |
| lark-skill-maker | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:42 | `C:\Users\win10\.cc-switch\skills\lark-skill-maker\SKILL.md` | `D:\AI-Skills\知识库\lark-skill-maker` | 推荐保留版本（修改时间最新） |
| lark-skill-maker | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:42 | `C:\Users\win10\.claude\skills\lark-skill-maker\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-skill-maker_from_skills` | 重复或旧版本，移动到 archived |
| lark-skill-maker | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:42 | `C:\Users\win10\.hermes\skills\lark-skill-maker\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-skill-maker_from_skills` | 重复或旧版本，移动到 archived |
| lark-skill-maker | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-skill-maker\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-skill-maker_from_skills` | 重复或旧版本，移动到 archived |
| lark-skill-maker | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052842_lark-skill-maker\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052842_lark-skill-maker` | 重复或旧版本，移动到 archived |
| lark-skill-maker | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-skill-maker\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-skill-maker_from_skills` | 重复或旧版本，移动到 archived |
| lark-slides | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:44 | `C:\Users\win10\.cc-switch\skills\lark-slides\SKILL.md` | `D:\AI-Skills\知识库\lark-slides` | 推荐保留版本（修改时间最新） |
| lark-slides | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:44 | `C:\Users\win10\.claude\skills\lark-slides\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-slides_from_skills` | 重复或旧版本，移动到 archived |
| lark-slides | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:44 | `C:\Users\win10\.hermes\skills\lark-slides\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-slides_from_skills` | 重复或旧版本，移动到 archived |
| lark-slides | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-slides\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-slides_from_skills` | 重复或旧版本，移动到 archived |
| lark-slides | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052844_lark-slides\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052844_lark-slides` | 重复或旧版本，移动到 archived |
| lark-slides | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-slides\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-slides_from_skills` | 重复或旧版本，移动到 archived |
| lark-task | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:46 | `C:\Users\win10\.cc-switch\skills\lark-task\SKILL.md` | `D:\AI-Skills\知识库\lark-task` | 推荐保留版本（修改时间最新） |
| lark-task | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:46 | `C:\Users\win10\.claude\skills\lark-task\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-task_from_skills` | 重复或旧版本，移动到 archived |
| lark-task | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:46 | `C:\Users\win10\.hermes\skills\lark-task\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-task_from_skills` | 重复或旧版本，移动到 archived |
| lark-task | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-task\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-task_from_skills` | 重复或旧版本，移动到 archived |
| lark-task | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052846_lark-task\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052846_lark-task` | 重复或旧版本，移动到 archived |
| lark-task | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-task\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-task_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:50 | `C:\Users\win10\.cc-switch\skills\lark-vc\SKILL.md` | `D:\AI-Skills\知识库\lark-vc` | 推荐保留版本（修改时间最新） |
| lark-vc | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:50 | `C:\Users\win10\.claude\skills\lark-vc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:50 | `C:\Users\win10\.hermes\skills\lark-vc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-vc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052850_lark-vc\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052850_lark-vc` | 重复或旧版本，移动到 archived |
| lark-vc | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-vc\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc-agent | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:52 | `C:\Users\win10\.cc-switch\skills\lark-vc-agent\SKILL.md` | `D:\AI-Skills\知识库\lark-vc-agent` | 推荐保留版本（修改时间最新） |
| lark-vc-agent | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:52 | `C:\Users\win10\.claude\skills\lark-vc-agent\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc-agent_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc-agent | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:52 | `C:\Users\win10\.hermes\skills\lark-vc-agent\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc-agent_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc-agent | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-vc-agent\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc-agent_from_skills` | 重复或旧版本，移动到 archived |
| lark-vc-agent | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052852_lark-vc-agent\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052852_lark-vc-agent` | 重复或旧版本，移动到 archived |
| lark-vc-agent | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-vc-agent\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-vc-agent_from_skills` | 重复或旧版本，移动到 archived |
| lark-whiteboard | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:54 | `C:\Users\win10\.cc-switch\skills\lark-whiteboard\SKILL.md` | `D:\AI-Skills\知识库\lark-whiteboard` | 推荐保留版本（修改时间最新） |
| lark-whiteboard | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:54 | `C:\Users\win10\.claude\skills\lark-whiteboard\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-whiteboard_from_skills` | 重复或旧版本，移动到 archived |
| lark-whiteboard | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:54 | `C:\Users\win10\.hermes\skills\lark-whiteboard\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-whiteboard_from_skills` | 重复或旧版本，移动到 archived |
| lark-whiteboard | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-whiteboard\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-whiteboard_from_skills` | 重复或旧版本，移动到 archived |
| lark-whiteboard | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052854_lark-whiteboard\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052854_lark-whiteboard` | 重复或旧版本，移动到 archived |
| lark-whiteboard | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-whiteboard\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-whiteboard_from_skills` | 重复或旧版本，移动到 archived |
| lark-wiki | 知识库 | ⭐ 保留 (Keep) | 2026-06-19 13:28:56 | `C:\Users\win10\.cc-switch\skills\lark-wiki\SKILL.md` | `D:\AI-Skills\知识库\lark-wiki` | 推荐保留版本（修改时间最新） |
| lark-wiki | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:56 | `C:\Users\win10\.claude\skills\lark-wiki\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-wiki_from_skills` | 重复或旧版本，移动到 archived |
| lark-wiki | 知识库 | 📦 归档 (Archive) | 2026-06-19 13:28:56 | `C:\Users\win10\.hermes\skills\lark-wiki\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-wiki_from_skills` | 重复或旧版本，移动到 archived |
| lark-wiki | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-wiki\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-wiki_from_skills` | 重复或旧版本，移动到 archived |
| lark-wiki | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052856_lark-wiki\skill\SKILL.md` | `D:\AI-Skills\archived\知识库\skill_from_20260619_052856_lark-wiki` | 重复或旧版本，移动到 archived |
| lark-wiki | 知识库 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-wiki\SKILL.md` | `D:\AI-Skills\archived\知识库\lark-wiki_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-meeting-summary | 工作流 | ⭐ 保留 (Keep) | 2026-06-19 13:28:57 | `C:\Users\win10\.cc-switch\skills\lark-workflow-meeting-summary\SKILL.md` | `D:\AI-Skills\工作流\lark-workflow-meeting-summary` | 推荐保留版本（修改时间最新） |
| lark-workflow-meeting-summary | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:57 | `C:\Users\win10\.claude\skills\lark-workflow-meeting-summary\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-meeting-summary_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-meeting-summary | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:57 | `C:\Users\win10\.hermes\skills\lark-workflow-meeting-summary\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-meeting-summary_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-meeting-summary | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-workflow-meeting-summary\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-meeting-summary_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-meeting-summary | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052857_lark-workflow-meeting-summary\skill\SKILL.md` | `D:\AI-Skills\archived\工作流\skill_from_20260619_052857_lark-workflow-meeting-summary` | 重复或旧版本，移动到 archived |
| lark-workflow-meeting-summary | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-workflow-meeting-summary\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-meeting-summary_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-standup-report | 工作流 | ⭐ 保留 (Keep) | 2026-06-19 13:28:59 | `C:\Users\win10\.cc-switch\skills\lark-workflow-standup-report\SKILL.md` | `D:\AI-Skills\工作流\lark-workflow-standup-report` | 推荐保留版本（修改时间最新） |
| lark-workflow-standup-report | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:59 | `C:\Users\win10\.claude\skills\lark-workflow-standup-report\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-standup-report_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-standup-report | 工作流 | 📦 归档 (Archive) | 2026-06-19 13:28:59 | `C:\Users\win10\.hermes\skills\lark-workflow-standup-report\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-standup-report_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-standup-report | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.agents\skills\lark-workflow-standup-report\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-standup-report_from_skills` | 重复或旧版本，移动到 archived |
| lark-workflow-standup-report | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052859_lark-workflow-standup-report\skill\SKILL.md` | `D:\AI-Skills\archived\工作流\skill_from_20260619_052859_lark-workflow-standup-report` | 重复或旧版本，移动到 archived |
| lark-workflow-standup-report | 工作流 | 📦 归档 (Archive) | 2026-06-09 11:23:13 | `C:\Users\win10\.qoder\skills\lark-workflow-standup-report\SKILL.md` | `D:\AI-Skills\archived\工作流\lark-workflow-standup-report_from_skills` | 重复或旧版本，移动到 archived |
| remotion | Remotion | ⭐ 保留 (Keep) | 2026-06-19 13:29:00 | `C:\Users\win10\.cc-switch\skills\remotion\SKILL.md` | `D:\AI-Skills\Remotion\remotion` | 推荐保留版本（修改时间最新） |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-19 13:29:00 | `C:\Users\win10\.claude\skills\remotion\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion_from_skills` | 重复或旧版本，移动到 archived |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-19 13:29:00 | `C:\Users\win10\.codex\skills\remotion\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion_from_skills` | 重复或旧版本，移动到 archived |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-19 13:29:00 | `C:\Users\win10\.hermes\skills\remotion\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion_from_skills` | 重复或旧版本，移动到 archived |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:32 | `C:\Users\win10\.agents\skills\remotion\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion_from_skills` | 重复或旧版本，移动到 archived |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:32 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052900_remotion\skill\SKILL.md` | `D:\AI-Skills\archived\Remotion\skill_from_20260619_052900_remotion` | 重复或旧版本，移动到 archived |
| remotion | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:32 | `C:\Users\win10\.qoder\skills\remotion\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion_from_skills` | 重复或旧版本，移动到 archived |
| remotion-best-practices | Remotion | ⭐ 保留 (Keep) | 2026-06-20 11:34:57 | `C:\Users\win10\.agents\skills\remotion-best-practices\SKILL.md` | `D:\AI-Skills\Remotion\remotion-best-practices` | 推荐保留版本（修改时间最新） |
| remotion-best-practices | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:15 | `C:\Users\win10\.cc-switch\skills\remotion-best-practices\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-best-practices_from_skills` | 重复或旧版本，移动到 archived |
| remotion-best-practices | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:15 | `C:\Users\win10\.hermes\skills\remotion-best-practices\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-best-practices_from_skills` | 重复或旧版本，移动到 archived |
| remotion-bits | Remotion | ⭐ 保留 (Keep) | 2026-06-20 12:12:18 | `C:\Users\win10\.agents\skills\remotion-bits\SKILL.md` | `D:\AI-Skills\Remotion\remotion-bits` | 推荐保留版本（修改时间最新） |
| remotion-bits | Remotion | 📦 归档 (Archive) | 2026-06-09 16:20:59 | `C:\Users\win10\.cc-switch\skills\remotion-bits\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-bits_from_skills` | 重复或旧版本，移动到 archived |
| remotion-bits | Remotion | 📦 归档 (Archive) | 2026-06-09 16:20:59 | `C:\Users\win10\.codex\skills\remotion-bits\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-bits_from_skills` | 重复或旧版本，移动到 archived |
| remotion-bits | Remotion | 📦 归档 (Archive) | 2026-06-09 16:20:59 | `C:\Users\win10\.hermes\skills\remotion-bits\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-bits_from_skills` | 重复或旧版本，移动到 archived |
| remotion-to-hyperframes | Remotion | ⭐ 保留 (Keep) | 2026-06-19 13:29:09 | `C:\Users\win10\.cc-switch\skills\remotion-to-hyperframes\SKILL.md` | `D:\AI-Skills\Remotion\remotion-to-hyperframes` | 推荐保留版本（修改时间最新） |
| remotion-to-hyperframes | Remotion | 📦 归档 (Archive) | 2026-06-19 13:29:09 | `C:\Users\win10\.claude\skills\remotion-to-hyperframes\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-to-hyperframes_from_skills` | 重复或旧版本，移动到 archived |
| remotion-to-hyperframes | Remotion | 📦 归档 (Archive) | 2026-06-19 13:29:09 | `C:\Users\win10\.hermes\skills\remotion-to-hyperframes\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-to-hyperframes_from_skills` | 重复或旧版本，移动到 archived |
| remotion-to-hyperframes | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:24 | `C:\Users\win10\.agents\skills\remotion-to-hyperframes\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-to-hyperframes_from_skills` | 重复或旧版本，移动到 archived |
| remotion-to-hyperframes | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:24 | `C:\Users\win10\.cc-switch\skill-backups\20260619_052909_remotion-to-hyperframes\skill\SKILL.md` | `D:\AI-Skills\archived\Remotion\skill_from_20260619_052909_remotion-to-hyperframes` | 重复或旧版本，移动到 archived |
| remotion-to-hyperframes | Remotion | 📦 归档 (Archive) | 2026-06-17 18:37:24 | `C:\Users\win10\.qoder\skills\remotion-to-hyperframes\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-to-hyperframes_from_skills` | 重复或旧版本，移动到 archived |
| remotion-video | Remotion | ⭐ 保留 (Keep) | 2026-06-20 12:12:15 | `C:\Users\win10\.agents\skills\remotion-video\SKILL.md` | `D:\AI-Skills\Remotion\remotion-video` | 推荐保留版本（修改时间最新） |
| remotion-video | Remotion | 📦 归档 (Archive) | 2026-06-20 12:12:15 | `C:\Users\win10\.cc-switch\skills\remotion-video\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-video_from_skills` | 重复或旧版本，移动到 archived |
| bggg-creator-image2psd | 图片提示词 | ⭐ 保留 (Keep) | 2026-05-15 09:34:01 | `C:\Users\win10\.cc-switch\skills\bggg-creator-image2psd\SKILL.md` | `D:\AI-Skills\图片提示词\bggg-creator-image2psd` | 推荐保留版本（修改时间最新） |
| bggg-creator-image2psd | 图片提示词 | 📦 归档 (Archive) | 2026-05-15 09:34:01 | `C:\Users\win10\.codex\skills\bggg-creator-image2psd\SKILL.md` | `D:\AI-Skills\archived\图片提示词\bggg-creator-image2psd_from_skills` | 重复或旧版本，移动到 archived |
| bggg-creator-image2psd | 图片提示词 | 📦 归档 (Archive) | 2026-05-15 09:34:01 | `C:\Users\win10\.hermes\skills\bggg-creator-image2psd\SKILL.md` | `D:\AI-Skills\archived\图片提示词\bggg-creator-image2psd_from_skills` | 重复或旧版本，移动到 archived |
| codex-ppt | 设计 | ⭐ 保留 (Keep) | 2026-06-04 11:53:54 | `C:\Users\win10\.cc-switch\skills\codex-ppt\SKILL.md` | `D:\AI-Skills\设计\codex-ppt` | 推荐保留版本（修改时间最新） |
| codex-ppt | 设计 | 📦 归档 (Archive) | 2026-06-04 11:53:54 | `C:\Users\win10\.codex\skills\codex-ppt\SKILL.md` | `D:\AI-Skills\archived\设计\codex-ppt_from_skills` | 重复或旧版本，移动到 archived |
| codex-ppt | 设计 | 📦 归档 (Archive) | 2026-06-04 11:53:54 | `C:\Users\win10\.hermes\skills\codex-ppt\SKILL.md` | `D:\AI-Skills\archived\设计\codex-ppt_from_skills` | 重复或旧版本，移动到 archived |
| defuddle | 代码 | ⭐ 保留 (Keep) | 2026-03-30 11:15:24 | `C:\Users\win10\.cc-switch\skills\defuddle\SKILL.md` | `D:\AI-Skills\代码\defuddle` | 推荐保留版本（修改时间最新） |
| defuddle | 代码 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.codex\skills\defuddle\SKILL.md` | `D:\AI-Skills\archived\代码\defuddle_from_skills` | 重复或旧版本，移动到 archived |
| defuddle | 代码 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.hermes\skills\defuddle\SKILL.md` | `D:\AI-Skills\archived\代码\defuddle_from_skills` | 重复或旧版本，移动到 archived |
| defuddle | 代码 | 📦 归档 (Archive) | 2026-03-26 11:50:18 | `C:\Users\win10\.codex\skills\obsidian-skills\skills\defuddle\SKILL.md` | `D:\AI-Skills\archived\代码\defuddle_from_skills` | 重复或旧版本，移动到 archived |
| docx-to-md | 知识库 | ⭐ 保留 (Keep) | 2026-05-14 14:42:23 | `C:\Users\win10\.cc-switch\skills\docx-to-md\SKILL.md` | `D:\AI-Skills\知识库\docx-to-md` | 推荐保留版本（修改时间最新） |
| docx-to-md | 知识库 | 📦 归档 (Archive) | 2026-05-14 14:42:23 | `C:\Users\win10\.claude\skills\docx-to-md\SKILL.md` | `D:\AI-Skills\archived\知识库\docx-to-md_from_skills` | 重复或旧版本，移动到 archived |
| docx-to-md | 知识库 | 📦 归档 (Archive) | 2026-05-14 14:42:23 | `C:\Users\win10\.hermes\skills\docx-to-md\SKILL.md` | `D:\AI-Skills\archived\知识库\docx-to-md_from_skills` | 重复或旧版本，移动到 archived |
| guizang-ppt-skill | 设计 | ⭐ 保留 (Keep) | 2026-04-28 15:30:39 | `C:\Users\win10\.cc-switch\skills\guizang-ppt-skill\SKILL.md` | `D:\AI-Skills\设计\guizang-ppt-skill` | 推荐保留版本（修改时间最新） |
| guizang-ppt-skill | 设计 | 📦 归档 (Archive) | 2026-04-28 15:30:39 | `C:\Users\win10\.codex\skills\guizang-ppt-skill\SKILL.md` | `D:\AI-Skills\archived\设计\guizang-ppt-skill_from_skills` | 重复或旧版本，移动到 archived |
| guizang-ppt-skill | 设计 | 📦 归档 (Archive) | 2026-04-28 15:30:39 | `C:\Users\win10\.hermes\skills\guizang-ppt-skill\SKILL.md` | `D:\AI-Skills\archived\设计\guizang-ppt-skill_from_skills` | 重复或旧版本，移动到 archived |
| hv-analysis | 文案 | ⭐ 保留 (Keep) | 2026-04-22 15:22:03 | `C:\Users\win10\.codex\skills\hv-analysis\SKILL.md` | `D:\AI-Skills\文案\hv-analysis` | 推荐保留版本（修改时间最新） |
| hv-analysis | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.cc-switch\skills\hv-analysis\SKILL.md` | `D:\AI-Skills\archived\文案\hv-analysis_from_skills` | 重复或旧版本，移动到 archived |
| hv-analysis | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.claude\skills\hv-analysis\SKILL.md` | `D:\AI-Skills\archived\文案\hv-analysis_from_skills` | 重复或旧版本，移动到 archived |
| hv-analysis | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.hermes\skills\hv-analysis\SKILL.md` | `D:\AI-Skills\archived\文案\hv-analysis_from_skills` | 重复或旧版本，移动到 archived |
| ian-xiaohei-illustrations | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-08 10:02:46 | `C:\Users\win10\.cc-switch\skills\ian-xiaohei-illustrations\SKILL.md` | `D:\AI-Skills\图片提示词\ian-xiaohei-illustrations` | 推荐保留版本（修改时间最新） |
| ian-xiaohei-illustrations | 图片提示词 | 📦 归档 (Archive) | 2026-06-08 10:02:46 | `C:\Users\win10\.codex\skills\ian-xiaohei-illustrations\SKILL.md` | `D:\AI-Skills\archived\图片提示词\ian-xiaohei-illustrations_from_skills` | 重复或旧版本，移动到 archived |
| ian-xiaohei-illustrations | 图片提示词 | 📦 归档 (Archive) | 2026-06-08 10:02:46 | `C:\Users\win10\.hermes\skills\ian-xiaohei-illustrations\SKILL.md` | `D:\AI-Skills\archived\图片提示词\ian-xiaohei-illustrations_from_skills` | 重复或旧版本，移动到 archived |
| json-canvas | 设计 | ⭐ 保留 (Keep) | 2026-03-30 11:15:24 | `C:\Users\win10\.cc-switch\skills\json-canvas\SKILL.md` | `D:\AI-Skills\设计\json-canvas` | 推荐保留版本（修改时间最新） |
| json-canvas | 设计 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.codex\skills\json-canvas\SKILL.md` | `D:\AI-Skills\archived\设计\json-canvas_from_skills` | 重复或旧版本，移动到 archived |
| json-canvas | 设计 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.hermes\skills\json-canvas\SKILL.md` | `D:\AI-Skills\archived\设计\json-canvas_from_skills` | 重复或旧版本，移动到 archived |
| json-canvas | 设计 | 📦 归档 (Archive) | 2026-03-26 11:50:18 | `C:\Users\win10\.codex\skills\obsidian-skills\skills\json-canvas\SKILL.md` | `D:\AI-Skills\archived\设计\json-canvas_from_skills` | 重复或旧版本，移动到 archived |
| khazix-writer | 文案 | ⭐ 保留 (Keep) | 2026-04-22 15:22:03 | `C:\Users\win10\.codex\skills\khazix-writer\SKILL.md` | `D:\AI-Skills\文案\khazix-writer` | 推荐保留版本（修改时间最新） |
| khazix-writer | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.cc-switch\skills\khazix-writer\SKILL.md` | `D:\AI-Skills\archived\文案\khazix-writer_from_skills` | 重复或旧版本，移动到 archived |
| khazix-writer | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.claude\skills\khazix-writer\SKILL.md` | `D:\AI-Skills\archived\文案\khazix-writer_from_skills` | 重复或旧版本，移动到 archived |
| khazix-writer | 文案 | 📦 归档 (Archive) | 2026-04-17 14:46:27 | `C:\Users\win10\.hermes\skills\khazix-writer\SKILL.md` | `D:\AI-Skills\archived\文案\khazix-writer_from_skills` | 重复或旧版本，移动到 archived |
| lark-illustration-inserter | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-08 10:25:29 | `C:\Users\win10\.cc-switch\skills\lark-illustration-inserter\SKILL.md` | `D:\AI-Skills\图片提示词\lark-illustration-inserter` | 推荐保留版本（修改时间最新） |
| lark-illustration-inserter | 图片提示词 | 📦 归档 (Archive) | 2026-06-08 10:25:29 | `C:\Users\win10\.codex\skills\lark-illustration-inserter\SKILL.md` | `D:\AI-Skills\archived\图片提示词\lark-illustration-inserter_from_skills` | 重复或旧版本，移动到 archived |
| lark-illustration-inserter | 图片提示词 | 📦 归档 (Archive) | 2026-06-08 10:25:29 | `C:\Users\win10\.hermes\skills\lark-illustration-inserter\SKILL.md` | `D:\AI-Skills\archived\图片提示词\lark-illustration-inserter_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-bases | 知识库 | ⭐ 保留 (Keep) | 2026-03-30 11:15:24 | `C:\Users\win10\.cc-switch\skills\obsidian-bases\SKILL.md` | `D:\AI-Skills\知识库\obsidian-bases` | 推荐保留版本（修改时间最新） |
| obsidian-bases | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.codex\skills\obsidian-bases\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-bases_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-bases | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.hermes\skills\obsidian-bases\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-bases_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-bases | 知识库 | 📦 归档 (Archive) | 2026-03-26 11:50:18 | `C:\Users\win10\.codex\skills\obsidian-skills\skills\obsidian-bases\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-bases_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-cli | 知识库 | ⭐ 保留 (Keep) | 2026-03-30 11:15:24 | `C:\Users\win10\.cc-switch\skills\obsidian-cli\SKILL.md` | `D:\AI-Skills\知识库\obsidian-cli` | 推荐保留版本（修改时间最新） |
| obsidian-cli | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.codex\skills\obsidian-cli\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-cli_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-cli | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.hermes\skills\obsidian-cli\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-cli_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-cli | 知识库 | 📦 归档 (Archive) | 2026-03-26 11:50:18 | `C:\Users\win10\.codex\skills\obsidian-skills\skills\obsidian-cli\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-cli_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-markdown | 知识库 | ⭐ 保留 (Keep) | 2026-03-30 11:15:24 | `C:\Users\win10\.cc-switch\skills\obsidian-markdown\SKILL.md` | `D:\AI-Skills\知识库\obsidian-markdown` | 推荐保留版本（修改时间最新） |
| obsidian-markdown | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.codex\skills\obsidian-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-markdown_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-markdown | 知识库 | 📦 归档 (Archive) | 2026-03-30 11:15:24 | `C:\Users\win10\.hermes\skills\obsidian-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-markdown_from_skills` | 重复或旧版本，移动到 archived |
| obsidian-markdown | 知识库 | 📦 归档 (Archive) | 2026-03-26 11:50:18 | `C:\Users\win10\.codex\skills\obsidian-skills\skills\obsidian-markdown\SKILL.md` | `D:\AI-Skills\archived\知识库\obsidian-markdown_from_skills` | 重复或旧版本，移动到 archived |
| remotion-video-builder | Remotion | ⭐ 保留 (Keep) | 2026-05-19 15:02:30 | `C:\Users\win10\.cc-switch\skills\remotion-video-builder\SKILL.md` | `D:\AI-Skills\Remotion\remotion-video-builder` | 推荐保留版本（修改时间最新） |
| remotion-video-builder | Remotion | 📦 归档 (Archive) | 2026-05-19 15:02:30 | `C:\Users\win10\.codex\skills\remotion-video-builder\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-video-builder_from_skills` | 重复或旧版本，移动到 archived |
| remotion-video-builder | Remotion | 📦 归档 (Archive) | 2026-05-19 15:02:30 | `C:\Users\win10\.hermes\skills\remotion-video-builder\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-video-builder_from_skills` | 重复或旧版本，移动到 archived |
| remotion-video-replica | Remotion | ⭐ 保留 (Keep) | 2026-06-09 17:40:06 | `C:\Users\win10\.cc-switch\skills\remotion-video-replica\SKILL.md` | `D:\AI-Skills\Remotion\remotion-video-replica` | 推荐保留版本（修改时间最新） |
| remotion-video-replica | Remotion | 📦 归档 (Archive) | 2026-06-09 17:40:06 | `C:\Users\win10\.codex\skills\remotion-video-replica\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-video-replica_from_skills` | 重复或旧版本，移动到 archived |
| remotion-video-replica | Remotion | 📦 归档 (Archive) | 2026-06-09 17:40:06 | `C:\Users\win10\.hermes\skills\remotion-video-replica\SKILL.md` | `D:\AI-Skills\archived\Remotion\remotion-video-replica_from_skills` | 重复或旧版本，移动到 archived |
| plugin-creator | 知识库 | ⭐ 保留 (Keep) | 2026-06-21 10:54:19 | `C:\Users\win10\.codex\skills\.system\plugin-creator\SKILL.md` | `D:\AI-Skills\知识库\plugin-creator` | 推荐保留版本（修改时间最新） |
| plugin-creator | 知识库 | 📦 归档 (Archive) | 2026-06-19 12:59:44 | `C:\Users\win10\.codex\.tmp\plugins\.agents\skills\plugin-creator\SKILL.md` | `D:\AI-Skills\archived\知识库\plugin-creator_from_skills` | 重复或旧版本，移动到 archived |
| imagegen | 设计 | ⭐ 保留 (Keep) | 2026-06-21 10:54:19 | `C:\Users\win10\.codex\skills\.system\imagegen\SKILL.md` | `D:\AI-Skills\设计\imagegen` | 唯一有效技能，正常保留 |
| openai-docs | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-21 10:54:19 | `C:\Users\win10\.codex\skills\.system\openai-docs\SKILL.md` | `D:\AI-Skills\图片提示词\openai-docs` | 唯一有效技能，正常保留 |
| skill-creator | 工作流 | ⭐ 保留 (Keep) | 2026-06-21 10:54:19 | `C:\Users\win10\.codex\skills\.system\skill-creator\SKILL.md` | `D:\AI-Skills\工作流\skill-creator` | 唯一有效技能，正常保留 |
| skill-installer | 代码 | ⭐ 保留 (Keep) | 2026-06-21 10:54:19 | `C:\Users\win10\.codex\skills\.system\skill-installer\SKILL.md` | `D:\AI-Skills\代码\skill-installer` | 唯一有效技能，正常保留 |
| automate | 工作流 | ⭐ 保留 (Keep) | 2026-06-19 20:26:16 | `C:\Users\win10\.cursor\skills-cursor\automate\SKILL.md` | `D:\AI-Skills\工作流\automate` | 唯一有效技能，正常保留 |
| babysit | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\babysit\SKILL.md` | `D:\AI-Skills\其他\babysit` | 唯一有效技能，正常保留 |
| canvas | 设计 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\canvas\SKILL.md` | `D:\AI-Skills\设计\canvas` | 唯一有效技能，正常保留 |
| create-hook | 文案 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\create-hook\SKILL.md` | `D:\AI-Skills\文案\create-hook` | 唯一有效技能，正常保留 |
| create-rule | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\create-rule\SKILL.md` | `D:\AI-Skills\其他\create-rule` | 唯一有效技能，正常保留 |
| create-skill | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\create-skill\SKILL.md` | `D:\AI-Skills\其他\create-skill` | 唯一有效技能，正常保留 |
| create-subagent | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\create-subagent\SKILL.md` | `D:\AI-Skills\图片提示词\create-subagent` | 唯一有效技能，正常保留 |
| loop | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-19 20:26:16 | `C:\Users\win10\.cursor\skills-cursor\loop\SKILL.md` | `D:\AI-Skills\图片提示词\loop` | 唯一有效技能，正常保留 |
| migrate-to-skills | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\migrate-to-skills\SKILL.md` | `D:\AI-Skills\其他\migrate-to-skills` | 唯一有效技能，正常保留 |
| review | 代码 | ⭐ 保留 (Keep) | 2026-06-19 20:26:16 | `C:\Users\win10\.cursor\skills-cursor\review\SKILL.md` | `D:\AI-Skills\代码\review` | 唯一有效技能，正常保留 |
| review-bugbot | 代码 | ⭐ 保留 (Keep) | 2026-06-19 20:26:16 | `C:\Users\win10\.cursor\skills-cursor\review-bugbot\SKILL.md` | `D:\AI-Skills\代码\review-bugbot` | 唯一有效技能，正常保留 |
| review-security | 代码 | ⭐ 保留 (Keep) | 2026-06-19 20:26:16 | `C:\Users\win10\.cursor\skills-cursor\review-security\SKILL.md` | `D:\AI-Skills\代码\review-security` | 唯一有效技能，正常保留 |
| sdk | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\sdk\SKILL.md` | `D:\AI-Skills\图片提示词\sdk` | 唯一有效技能，正常保留 |
| shell | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\shell\SKILL.md` | `D:\AI-Skills\其他\shell` | 唯一有效技能，正常保留 |
| split-to-prs | 其他 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\split-to-prs\SKILL.md` | `D:\AI-Skills\其他\split-to-prs` | 唯一有效技能，正常保留 |
| statusline | 图片提示词 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\statusline\SKILL.md` | `D:\AI-Skills\图片提示词\statusline` | 唯一有效技能，正常保留 |
| update-cli-config | 代码 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\update-cli-config\SKILL.md` | `D:\AI-Skills\代码\update-cli-config` | 唯一有效技能，正常保留 |
| update-cursor-settings | 代码 | ⭐ 保留 (Keep) | 2026-06-19 20:20:20 | `C:\Users\win10\.cursor\skills-cursor\update-cursor-settings\SKILL.md` | `D:\AI-Skills\代码\update-cursor-settings` | 唯一有效技能，正常保留 |
| hello-ping | 其他 | ⭐ 保留 (Keep) | 2026-04-17 15:47:27 | `C:\Users\win10\Documents\Claude\Scheduled\hello-ping\SKILL.md` | `D:\AI-Skills\其他\hello-ping` | 唯一有效技能，正常保留 |
| bilibili-upload | 视频 | ⭐ 保留 (Keep) | 2026-04-02 16:37:29 | `D:\HeyGem\social-auto-upload\skills\bilibili-upload\SKILL.md` | `D:\AI-Skills\视频\bilibili-upload` | 唯一有效技能，正常保留 |
| douyin-upload | 视频 | ⭐ 保留 (Keep) | 2026-04-02 16:37:29 | `D:\HeyGem\social-auto-upload\skills\douyin-upload\SKILL.md` | `D:\AI-Skills\视频\douyin-upload` | 唯一有效技能，正常保留 |
| kuaishou-upload | 视频 | ⭐ 保留 (Keep) | 2026-04-02 16:37:29 | `D:\HeyGem\social-auto-upload\skills\kuaishou-upload\SKILL.md` | `D:\AI-Skills\视频\kuaishou-upload` | 唯一有效技能，正常保留 |
| xiaohongshu-upload | 视频 | ⭐ 保留 (Keep) | 2026-04-02 16:37:29 | `D:\HeyGem\social-auto-upload\skills\xiaohongshu-upload\SKILL.md` | `D:\AI-Skills\视频\xiaohongshu-upload` | 唯一有效技能，正常保留 |
