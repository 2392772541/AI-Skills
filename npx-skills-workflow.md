# ⚙️ npx skills 安全工作流与新技能引入规范

本文档定义了如何在保留当前目录联接（Junction）唯一事实源方案的基础上，将开源工具 `npx skills` 作为一个安全的“查找、下载、评估”辅助工具的使用规范。

---

## 一、 为什么不完全切换到 `npx skills`
1. **本地调试实时性**：当前方案中，修改 `D:\AI-Skills\skills` 下的技能代码（例如微调 `00-skill-router` 规则），AI 客户端立即实时生效。若切换到 `npx skills` 完全接管，每次微调必须通过 git 提交和更新，效率极其低下。
2. **唯一事实源绝对受控**：`npx skills` 无法直接管理本地非 Git 分发源。如果交由其接管，其内置的软链接重构机制极易破坏我们精心整理的 80 个本地特化技能，导致 `00-skill-router` 决策中枢被强行抹除。
3. **隔离防污染**：网络拉取的开源技能可能带有未知的冲突规则或冗余文件，需要经过安全审计和去重分析后才可进入正式库。

---

## 二、 统一技能库当前物理结构
- 📂 **唯一事实正式库**：`D:\AI-Skills\skills` (当前共 80 个技能，不可直接污染)
- 🔗 **Codex/agents 挂载点**：`C:\Users\win10\.agents\skills` (指向总库)
- 🔗 **Claude Code 挂载点**：`C:\Users\win10\.claude\skills` (指向总库)
- 📥 **新增技能隔离区**：`D:\AI-Skills\incoming` (放新下载、待审核和已驳回的技能)

---

## 三、 `npx skills` 在本系统中的定位
* 🔍 **只用于查找**：在网络上检索可能存在的高质量开源技能。
* 📥 **只用于下载**：通过命令拉取技能包，但**仅限下载到隔离区**。
* 🧪 **只用于评估**：在隔离区内进行代码审计和场景适配性评估。
* ⚠️ **不直接接管**：坚决禁止 `npx skills` 自动对 `C:\Users\win10\.agents` 或 `C:\Users\win10\.claude` 下的正式技能目录进行任何写入或软链接管理。

---

## 四、 新技能安全引入流程
所有新增的开源/第三方技能必须严格履行以下九步流程：

1. **下载到 incoming**：运行指令将目标技能克隆至隔离区的临时缓存目录中。
2. **检查 SKILL.md**：核对 YAML frontmatter 是否完整，`name` 与 `description` 是否规范。
3. **检查属性与依赖**：检查其是否包含本地 shell 执行或第三方 node 模块依赖。
4. **去重核对**：检查技能名称是否与现有的 80 个技能冲突，是否需进行版本合入或重命名。
5. **模板化记录**：套用 `incoming\NEW_SKILL_REVIEW_TEMPLATE.md` 模板填写评估记录。
6. **测试与效果校验**：在隔离区中由 Agent 进行局部的只读模拟路由或规则跑通测试。
7. **审核合入**：用户批准后，手动将该技能子文件夹复制到 `D:\AI-Skills\skills` 中。
8. **更新索引表**：更新 [skill-index.md](file:///D:/AI-Skills/skill-index.md) 中的技能总数与描述。
9. **微调路由规则**：在 `00-skill-router` 的 `SKILL.md` 和 `skill-map.md` 中添加对应的匹配规则、场景及触发词。

---

## 五、 危险操作清单 (严禁执行 ❌)
* **严禁直接覆盖 `D:\AI-Skills\skills`**：禁止将未经审查的第三方技能文件直接解压或写入正式库。
* **严禁让 `npx skills` 全局接管**：禁止运行 `npx skills add -g` 破坏现有的 Junction 指针。
* **严禁删除 Junction**：任何时候均不得擅自删除 `~/.agents/skills` 或 `~/.claude/skills` 下的目录联接。
* **严禁把缓存目录当正式库**：禁止在 AI 客户端中将 `.skills` 缓存区作为活动工作区，以防调试错乱。

---

## 六、 应急回滚方式
若不慎执行了危险操作导致 Junction 脱链或损坏：
1. 清空 `C:\Users\win10\.agents\skills` 和 `C:\Users\win10\.claude\skills` 冲突路径。
2. 以管理员权限运行以下命令，重新创建目录联接即可一键无损修复：
   ```powershell
   cmd /c mklink /J "C:\Users\win10\.agents\skills" "D:\AI-Skills\skills"
   cmd /c mklink /J "C:\Users\win10\.claude\skills" "D:\AI-Skills\skills"
   ```

---

## 七、 以后新增开源 Skill 时使用的提示词

### 📢 【以后新增开源 Skill 时使用的提示词】

> 我想用 `npx skills` 引入一个新的开源技能。请按照 [npx-skills-workflow.md](file:///D:/AI-Skills/npx-skills-workflow.md) 规范执行以下操作：
> 1. 请使用 `npx skills` 工具的 `use` 或 `download` 逻辑，将其安全下载到 `D:\AI-Skills\incoming\npx-downloads` 隔离目录中，**绝对不要**直接写入正式技能库或运行全局 `skills add -g`。
> 2. 对下载的技能进行审计：检查 `SKILL.md`、提取其名称和描述、评估是否与现有的 80 个技能重名或功能相似。
> 3. 套用 `D:\AI-Skills\incoming\NEW_SKILL_REVIEW_TEMPLATE.md` 模板生成评审记录。
> 4. 完成后向我报告，等待我确认后再决定是否手动合入 `D:\AI-Skills\skills`。
