# 规则来源索引

只记录来源和提炼结果，不保存视频字幕、文章全文或课程逐字稿。

| 日期 | 来源 | 类型/位置 | 提炼内容 | 写入位置 |
|---|---|---|---|---|
| 2026-07-16 | 想用 AI 做短剧得先学习“视听语言” | 视频；`<local-source>/9378f1075a2492a31b7ec8ba2517dcd6.mp4` | 先做导演决策再写提示词；景别、轴线、视线、运镜与剪辑必须服务叙事；增加静音观看质检 | `SKILL.md` 强制工作流；`visual-language.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-16 | 山音超级编剧大师 | 本地 Skill；`<codex-skills>/screenwriting-master` | 增加目标-障碍-结果微型戏剧动作、预期/实际鸿沟、价值转变、动作潜台词、双轨节奏、时长预算、长内容状态检查点与开场钩子 | `dramatic-beats.md`；`visual-language.md` 段落策略；`templates.md`；`regression-scenarios.md` |
| 2026-07-16 | 爽文 Insight 编剧 | 本地 Skill；`<codex-skills>/shuangwen-insight-screenwriter` | 增加观众/角色知情差、伏笔-回溯点-兑现闭环、兑现时机、误会递进与视觉揭示 | `insight-payoff.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-16 | 竹林问心真人漫剧提示词 | 本地 Skill；`<codex-skills>/zhulin-wenxin-cinematic-image-prompts` | 增加资产冲突优先级、参考用途分类、六维风格共性、场景/道具资产与定向故障修复 | `asset-reference-system.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-16 | Baoyu Comic | 本地 Skill；`<codex-skills>/baoyu-comic` | 增加角色资产表、参考用途映射、生成前固定提示词、版本留存和最小单元重生成 | `asset-reference-system.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-16 | Baoyu Short Video Workflow | 本地 Skill；`<codex-skills>/baoyu-short-video-workflow` | 增加默认竖屏前 3 秒可读性、移动端字幕安全和视觉必须承担任务；不吸收固定 2–6 秒镜头限制 | `templates.md` 移动端质检 |
| 2026-07-18 | Seedance 2.0 Skill OS（Iamemily2050） | GitHub；`https://github.com/Emily2040/seedance-2.0`；用户提供转存链接 | 增加单一导演意图、全局规划局部生成、接受成片覆盖计划终点、片段合同、五级结果处置与单变量重试；不吸收 Seedance 专属参数 | `SKILL.md`；`visual-language.md`；`production-state-and-retakes.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-18 | 激励事件前的剧情铺垫课程 | 视频；`<local-source>/0f818a4448e7771e07c4a8b5ece01533.mp4` | 增加普通剧情的能力证据阶梯、铺垫与行动验证、权力变化和行为惯性分离、欲望路径连续、开场体验承诺；明确与爽文/Insight分流 | `SKILL.md`；`setup-and-causality.md`；`insight-payoff.md`；`knowledge-ingestion.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-18 | DeepWhite Cinematic Shot Designer ZH v3 | 本地Skill包；`<local-downloads>/deepwhite-cinematic-shot-designer-zh-v3.skill` | 增加场景四维诊断、权力空间、普通拍法损失测试、行为触发运镜和功能型视觉策略；不吸收导演姓名过滤与固定视觉装置配额 | `scene-strategy-and-power-blocking.md`；`SKILL.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-18 | DeepWhite Shotlist Builder ZH v2.7 | 本地Skill包；`<local-downloads>/deepwhite-shotlist-builder-zh-user-v2.7-portable-20260604-205059.skill` | 增加资产/空间/时间预检、Shot与Clip分离、生成分组和HTML交付；将六个强制确认改为风险分级，不吸收Seedance固定时长与提示词硬编码 | `preflight-and-risk-gates.md`；`project-state-and-identifiers.md`；`generation-clip-compiler.md`；`delivery-and-media-review.md`；脚本与模板 |
| 2026-07-18 | DeepWhite Image Prompt Builder | 本地Skill包；`<local-downloads>/deepwhite-image-prompt-builder-complete-20260604-203446.skill` | 增加静态资产提示词和剧本资产准备流程；默认中文平台中立，不强制双语 | `asset-preparation.md`；`templates.md` |
| 2026-07-18 | DeepWhite 中文影视编剧 v1 | 本地Skill包；`<local-downloads>/deepwhite-screenwriting-v1-complete-20260604-203446.skill` | 增加场景价值、前后因果和对白保留范围的剧本到分镜交接；完整编剧与量化评分仍交给编剧Skill | `screenplay-handoff.md`；`SKILL.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-18 | Cinematic Style Repair | Markdown Skill；`<local-source>/cinematic-style-repair.md` | 增加画面主核、关键图复杂度预算、可信单主光、受控色彩、先删后加和静态失败定向修复；不吸收16:9默认、拒绝参考资产、固定单人物和固定相机质感 | `key-image-restraint-and-repair.md`；`SKILL.md`；`asset-preparation.md`；`visual-language.md`；`production-state-and-retakes.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-23 | AI 电影转场四种方法 | 视频；`<local-source>/4c5125576929014f31f8c91ba00b7486.mp4` | 增加遮挡、甩镜、动作匹配、构图匹配的转场合同、隐藏剪切窗口、保持变量与逐帧质检；不吸收具体软件步骤和平台承诺 | `transition-design-and-cut-bridges.md`；`SKILL.md`；`generation-clip-compiler.md`；`visual-language.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-23 | POV、直视镜头与第四面墙 | 视频；`<local-source>/a07f92ed030055f520786282054ce333.mp4` | 区分视角所有权、凝视对象与第四面墙；角色看镜头不自动等于面对现实观众 | `viewpoint-and-gaze-design.md`；`SKILL.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-23 | 物品 POV 提示方法 | 视频；`<local-source>/ff3d3e4f1230a315e87c8ad6c396205c.mp4` | 增加拟人POV所有者、空间原点、前景结构证据、主体互动和空间故障检查；不强制GoPro或鱼眼 | `viewpoint-and-gaze-design.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-23 | AI 视频镜头运动语言 | 视频；`<local-source>/cd9fd93421d033b26a4e95b40c3d9f8b.mp4` | 强化运镜触发、终点新增信息、人物调度和固定镜头；区分运动路径、跟随关系与稳定方式 | `viewpoint-and-gaze-design.md`；`visual-language.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-24 | Seedance 2.0 核心使用方法 | 视频；`<local-source>/6d2a5b8b36559231feb7746f574c4b3f.mp4` | 提炼时间脚本、动作准备/执行/落定、参考调度、延展拼接重叠检查、局部编辑合同与定向稳定约束；不吸收固定时长、固定参考数量和平台按钮 | `prompt-bible.md`；`SKILL.md`；`generation-clip-compiler.md`；`production-state-and-retakes.md`；`toonflow-local-workflow.md`；`templates.md`；`regression-scenarios.md` |
| 2026-07-27 | 日系记忆感图片的三种视觉逻辑 | 视频；`<local-source>/13429596509001316.mp4` | 建立按明确生图意图触发的日系图片分支；提炼叙事性留白、有物理来源的受控过曝逆光、心理性色调分离及专项质检；不吸收导演姓名、宣传话术和全局固定滤镜 | `SKILL.md`；`japanese-photo-generation.md`；`regression-scenarios.md` |
