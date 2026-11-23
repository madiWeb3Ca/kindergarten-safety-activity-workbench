# 园所三防安全活动工作台（kindergarten-safety-activity-workbench）

带园所后勤 / 安全岗分步填空，产出**防火、防震、防拐**三类安全活动的方案稿，以及活动后的总结报告；默认交付单文件 HTML（总结稿现场照片内嵌）。

- **方案生成（活动前）**：定背景 → 盘条件 → 选组合 → 搭方案 → 出稿留痕；含宣教认知、疏散 / 避险演练、成人专项（仅防火）、外联体验、家园宣传板块与留痕清单。
- **活动总结（活动后）**：接收口述陈述与现场照片，归纳定量与定性信息，出独立成页、可打印留档的单页总结。

> 边界：只出活动组织初稿与总结初稿；不搭隐患台账体系、不编应急预案、不承接设施改造与值班排班，不下"达标 / 零隐患"结论；幼儿只认知、观摩、参与教师带领的演练，不碰明火与器材。

## 目录结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能定义、双模式三分支流程、质量规则、边界与资源索引 |
| `agents/doubao.yaml` / `openai.yaml` | 平台接口配置（显示名、默认提示词） |
| `references/policy-basis.md` | 三分支年度节点、法定 / 指南动作口径、排查重点（以官方最新为准） |
| `references/coaching-scripts.md` | 方案五步 / 总结五步引导话术、追问链、答不全兜底 |
| `references/data-checklist.md` | 采集清单：方案字段＋总结字段；A 对话必问 / B 现场待核实 / C 政策待核 |
| `references/activity-seeds.md` | 三分支板块原型种子、对象边界、前提与留痕 |
| `references/plan-framework.md` | 方案要素、流程示例、量力校验、降级预案；总结报告基线格式 |
| `references/drill-sop.md` | 三分支活动分步 SOP：通用阶段对照、防火触发响应链、防震避险疏散链、防拐情景活动链、岗位动作清单、动作要领、异常分支引用位 |
| `references/yearly-schedule.md` | 年度／学期三防轮换排期参考表、场间衔接规则与台账边界 |
| `references/red-lines.md` | 通用红线＋三分支专项红线、事实检索、能力与隐私边界、占位写法 |
| `references/faq.md` | 高频问答与反模式 |
| `references/publish-checklist.md` | 对外发布前 TRACE 五维过表、专有名词剥离表与上架待办 |
| `examples/fire-plan-sample.md` / `.html` | 防火综合场示例 |
| `examples/fire-drill-sample.md` / `.html` | 防火疏散演练专场示例 |
| `examples/fire-education-sample.md` / `.html` | 防火宣教认知专场示例 |
| `examples/earthquake-sample.md` / `.html` | 防震避险疏散演练示例 |
| `examples/abduction-sample.md` / `.html` | 防拐情景教育示例 |
| `examples/summary-sample.md` / `.html` | 活动总结报告示例（照片内嵌） |
| `examples/yearly-schedule-sample.md` / `.html` | 年度三防活动排期参考表示例 |
| `scripts/scaffold_plan.py` | 按背景参数生成方案 / 总结骨架（`--branch` 选分支，`--mode summary` 出总结） |
| `scripts/render_html.py` | Markdown 渲染为单文件 HTML，本地照片 base64 内嵌；大图超 700KB 告警，压缩钩子预留 |
| `scripts/check_plan.py` | 结构与红线校验（方案稿 / 总结稿 / 年度排期表三套规则，.md / .html 均可） |
| `scripts/selftest.py` | 冒烟测试用例 |
| `CHANGELOG.md` / `LICENSE.txt` | 版本记录；CC-BY-NC-SA-4.0 |

## 环境依赖

- Python 3（仅标准库：argparse / os / sys / re / html / base64 / mimetypes），无第三方包、无网络依赖。
- 产出 HTML 内联 CSS 与照片 data URI，断网可双击打开、可打印存 PDF。

## 安装与加载

1. 把整个目录放入技能目录（本地用户技能目录或平台技能目录），保持 `SKILL.md` 在根目录。
2. 重开一次会话，由平台按 `name` / `displayName` 识别；也可在对话中用默认提示词触发：
   > 使用 $kindergarten-safety-activity-workbench 帮我出一份幼儿园安全活动方案
3. 对话按引导填空；A 类必问项填完后出稿，B / C 类待核实项归集到文末清单。

## 命令行快速验证

```bash
# 生成方案骨架（默认 HTML，--format md 出底稿；--branch 选 防火/防震/防拐）
python scripts/scaffold_plan.py --title "防震避险疏散演练方案" --branch 防震

# 生成总结骨架
python scripts/scaffold_plan.py --mode summary --title "防火疏散演练活动总结"

# 校验稿子（方案稿 / 总结稿自动识别，md / html 均可）
python scripts/check_plan.py 稿子.md

# 渲染单文件 HTML（本地照片自动 base64 内嵌）
python scripts/render_html.py 稿子.md
```

## 自测

```bash
python scripts/selftest.py
```

退出码：`0` 全部通过；`1` 有错误（缺段 / 红线硬伤 / 未处理警告）；`2` 文件读取失败（不存在、目录、空文件、编码异常等中文提示）。

常见校验提示与处置：

| 提示 | 含义 | 处置 |
|---|---|---|
| 缺必备章节 | 骨架未含对应模式的背景、板块 / 基本信息、流程 / 过程、分工、校验 / 定量、红线 / 问题改进、留痕、待核定等段落 | 对照 `plan-framework.md` 补齐 |
| 红线词拦截 | 出现承诺性表述（零隐患 / 全部达标 / 保证不出事）或幼儿明火、器材实操 | 删除改写；实操对象仅限成人在岗人员 |
| 【待填】残留 | A 类对话必问项未采集完 | 回到引导问题补问，出稿前清零 |
| 【待核实】未归集 | 现场盘点 / 政策核对项散落在正文 | 收进文末待核定 / 待核实清单 |
| 外联写成既定事实 | 未接洽却写"已邀请消防站 / 民警 / 家长" | 改为"尚未接洽、列为备选"，联系不上走降级 |
| 过程标记残留 | 正文出现"口述 / 录音 / 语音转写"等来源标注 | 移到文末待核实清单或过程草稿，正文按成稿口吻 |
| 时段标签混用 | 同一篇既有钟点又有"到点后 / 另列时段"等相对时点 | 相对时点写明对应钟点，或统一为钟点表述 |
| 防火触发链缺失 | 方案未见火情发现 → 上报 → 启动通报环节，从警报直接跳到撤离 | 对照 `drill-sop.md` 第三节补齐，或注明本场为信号直启演练 |
| 防震避险链缺失 | 方案未见就近避险、伏地遮挡手抓牢、停止口令后疏散等避险环节 | 对照 `drill-sop.md` 第四节补齐 |
| 防拐写成撤离 / 强行带走模拟 | 防拐稿出现撤离疏散安排，或抱走、拖拽、强行带走类情景 | 改为班级情景认知与角色扮演；对照 `drill-sop.md` 第五节 |
| 总结定量为空 | 定量章节未出现人数 / 班级 / 用时数字 | 以名册记录补齐；取不到记【待核实】，不靠照片估算 |

## 发布口径

- 包内不固化园所名称、人数、器材、场地、联系人与当年主题；运行时从对话 / 项目空间检索，找不到留占位。
- 公共发布版须再次复检：无校名、地名、人名、企业名、坐标等专有事实；示例为模拟演示口径。发布前按 `references/publish-checklist.md` 过表。
- 旧版单类消防包 `fire-safety-activity-workbench` 保留留档，作为防火分支迁移源，不在本包内改动。
