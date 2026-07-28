---
name: binbinskill
description: >
  通用 AI 漫剧导演、分镜与生产控制 Skill。把故事、剧本、对白稿、已有分镜、参考资产或生成成片转换为可追踪的 Beat/Shot/Clip/Asset 项目状态，并按“提示词圣经”编译和质检所有 Asset、关键图、视频、续拍、局部编辑与平台提示词，同时支持连续性、Markdown/HTML 生产文档、本地 ToonFlow 同步和失败诊断。用于漫剧分镜、镜头语言、AI提示词输入输出、关键图、图生视频、ToonFlow、素材绑定、连续生成、成片复盘、提示词版本管理或知识吸收；当用户明确要求“生成日系照片”“生成日系图片”或“日系写真”时，启用内部日系图片生成分支。
---

# binbinskill

## 核心目标

把故事变成观众看得懂、AI 生成得出、剪辑接得上、Codex 能持续维护的生产项目。先决定剧情与导演设计，再编译平台提示词；所有输出都回到唯一项目状态，不用“电影感”、复杂运镜或画质词掩盖不清楚的戏。

## 工作原则

- 没有实质歧义时直接执行；只有会明显改变剧情、资产身份、空间轴线、平台成本或主要交付的高风险选择才询问。
- 默认画幅 `9:16`，默认中文平台中立；用户指定画幅或平台时覆盖。
- 不擅自改写核心冲突、人物动机、结局和主题。
- 未指定爽文、隐藏身份或公开兑现时，不增加羞辱、围观、身份揭示和打脸。
- 完整人物、世界观、故事结构或整部剧本交给 `screenwriting-master`；本 Skill 只为镜头成立轻度修补节拍。
- 用户提供图片、视频或成片时必须实际查看，不凭文件名、旧稿或计划判断。
- 任何任务只要读取、诊断、改写、生成、同步或质检提示词，必须首先读取 `references/prompt-bible.md`；它是提示词层最高编译优先级。

## 任务路由

- 任何提示词输入或输出：首先读取 `references/prompt-bible.md`，再按任务读取专项参考；未通过圣经质检不得交付或同步。
- 用户明确要求生成日系照片、日系图片或日系写真：在提示词圣经之后读取 `references/japanese-photo-generation.md`；只有提及日系、分析日系作品或普通分镜任务时不自动套用该分支。
- 新项目、旧 `Uxx` 迁移、编号或状态管理：读取 `references/project-state-and-identifiers.md`。
- 已有剧本进入分镜，或需要检查场景因果与对白保留范围：读取 `references/screenplay-handoff.md`。
- 输入不完整、资产/位置/时间可能需要确认：读取 `references/preflight-and-risk-gates.md`。
- 剧本转分镜、对话戏、动作戏或场景调度：读取 `references/dramatic-beats.md`、`references/scene-strategy-and-power-blocking.md`、`references/visual-language.md`。
- 需要第一人称、物品POV、半主观、关系、全知、媒介视角、直视镜头或第四面墙：读取 `references/viewpoint-and-gaze-design.md`。
- 需要遮挡、甩镜、动作匹配、构图匹配或跨 Shot/Clip 转场：读取 `references/transition-design-and-cut-bridges.md`，并与 `references/generation-clip-compiler.md` 联用。
- 普通剧情需要能力、关系、欲望或基调铺垫：读取 `references/setup-and-causality.md`。
- 明确存在知情差、误会、回溯、揭示或公开地位兑现：读取 `references/insight-payoff.md`。
- 需要角色、场景、道具参考图或资产库：读取 `references/asset-preparation.md` 与 `references/asset-reference-system.md`。
- 需要编写、生成、检查或修复关键图，尤其是画面杂乱、主体不清、光色虚假、人物僵硬、AI海报感或CG感：读取 `references/key-image-restraint-and-repair.md`。
- 需要把 Shot 编译为一次或多次视频生成：读取 `references/generation-clip-compiler.md`。
- 需要导入、更新、审核或排查本地 ToonFlow 项目、提示词、素材、音色和生成节点：读取 `references/toonflow-local-workflow.md`；任何写入前先按其中的身份确认、备份和双层回读规则执行。
- 连续生成、续拍、重试或接受成片：读取 `references/production-state-and-retakes.md`。
- Markdown/HTML 交付或视频复盘：读取 `references/delivery-and-media-review.md`。
- 所有正式输出使用 `references/templates.md`。
- 把视频、文章、课程或案例加入本 Skill：读取 `references/knowledge-ingestion.md`。

## 四级生产模型

新项目统一使用：

- `Bxx`：Beat，剧情变化。
- `Sxx`：Shot，一个画面任务、主体动作和主运镜。
- `Cxx`：Clip，一次 AI 视频生成，可包含一个或多个连续 Shot。
- `A-TYPE-xx`：Asset，角色、场景、道具、服装、风格或参考。

把 `project.json` 作为唯一事实源。使用 `assets/project-state-template.json` 创建；更新后运行 `scripts/validate_project.py`。旧 `Uxx` 项目先映射为 B/S/C/A，保留迁移记录，不直接作废。

## 强制生产流程

1. **预检**：确定范围、不可改变事实、画幅、平台、资产和风险；低/中风险直接推进。
2. **项目状态**：建立或更新 Project、Asset、Beat、Shot、Clip 和对白 ID。
3. **场景诊断**：判断戏剧发动机、信息关系、权力流向和空间问题，选择一个主视觉策略。
4. **Beat**：写目标 -> 障碍 -> 尝试 -> 预期/实际结果 -> 价值/信息/关系变化。
5. **Shot**：完成画面任务与导演意图，再确定景别机位、权力空间、视线轴线、主体动作、主运镜和剪辑锚点。
6. **资产与关键图**：按提示词圣经映射硬资产并编译静态起点；缺少时先建立最小资产提示词。
7. **Clip 编译**：按提示词圣经完成参考调度、完成边界、时间脚本、动作节奏、连续性、末帧和定向约束，再进行平台适配。
8. **验证与交付**：验证项目状态，默认交付 Markdown；用户需要生产看板时再生成并检查 HTML。
9. **成片复盘**：查看画面与声音，记录实际终点，执行五级处置和单变量重试。

## Shot 硬性要求

- 只完成一个画面任务和一个可验证的导演意图。
- 只包含一个主体动作和一种主运镜；复杂动作配简单镜头，复杂运镜配简单动作。
- 景别、机位、权力空间、光线、表演、运镜和声音共同服务同一意图。
- 每个 Shot 选择一个主视角；非客观视角写清所有者、镜头身份、凝视目标、成立证据和进入/退出方式。
- 写清动作与运镜的起点、路径、时长或速度、终点和触发原因。
- 保持人物屏幕侧、视线、轴线、方向、道具地理和光源连续。
- 入口/出口锚点必须能被下一 Shot 使用；末帧不得提前执行后续 Beat。
- 使用特殊转场时建立转场合同，写清意图、类型、隐藏剪切窗口、前后状态、保持变量、允许变化和失败条件。
- 若普通中景正反打不会损失任何信息或关系，优先使用更简单方案；不得为特殊而特殊。

## Clip 硬性要求

- 列出内部 Shot ID 和顺序；Shot 身份不得在合并后消失。
- 明确必须发生、不得发生、预计时长、内部时长、资产映射、提示词版本和末帧交接。
- 平台未指定时不写专属参数、模型名或固定时长；指定后只按已核实的平台档案适配。
- 多段生成采用“全局规划、局部生成”，不重演完成节拍，不提前泄露未来节拍。
- 接受成片的实际终点覆盖计划终点；拒绝片段不得进入正式连续性。

## 诊断与重做

按剧情可读性 -> 场景策略 -> 空间 -> 动作 -> Clip 可执行性 -> 生成稳定性 -> 剪辑顺序定位问题。

- 区分剧本、导演设计、资产、提示词、平台随机性和后期问题。
- 先判为保留/后期修复/局部编辑/同提示词重抽/重写提示词。
- 一次只改变一个变量，先更新项目状态和版本，再只重做受影响的 Shot/Clip。
- 不用位图覆盖修补错误身份、主体构图或不可读文字；需要时更新提示词并重生成。
- 关键图失败时先删减干扰，再补必要信息；一次只修改主体分离、人物状态、光线、色彩、构图或成像响应中的一项。

## Codex 工具化执行

- 项目校验：`python scripts/validate_project.py <project.json>`。
- HTML 报告：`python scripts/build_production_report.py <project.json> --output <report.html>`，随后实际检查页面。
- 视频预检：`python scripts/review_video.py <video> --output-dir <dir>`；需要且环境支持时增加 `--transcribe`。
- ToonFlow 只读体检：`python scripts/audit_toonflow_project.py --db <db2.sqlite> --project-id <id> --script-id <id> --direct-video`；修单个节点时增加 `--unit <序号>` 和 `--contains <关键句>`。
- Skill 更新后运行 `quick_validate.py`，并复查 `references/regression-scenarios.md`。

## 输出原则

- 先给可直接生产的结果，再补充必要说明。
- 平台中立的导演合同与平台提示词分层保存。
- 所有提示词必须通过 `prompt-bible.md` 的强制输出质检；不得直接交付未经编译的散文式描述或通用稳定咒语。
- 参考资产已提供的信息不要反复重写；每份参考标明主要用途和禁止迁移项。
- 对白需要完整保留时分配对白 ID 并验证覆盖；允许改编时记录删改授权范围。
- 输出前修复已知错误，不把明知不成立的分镜、状态或提示词交给用户。
