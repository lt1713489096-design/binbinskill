# ToonFlow 本地使用手册

## 目录

- 定位与原则
- 数据层与项目状态
- 标准生产流程
- 提示词写入
- 素材与音色绑定
- 本地文件存储
- 生成前体检
- 生成与成片回收
- 常见故障
- 数据库写入安全规则
- 完成标准

## 定位与原则

把 ToonFlow 当作执行工作台，把 `project.json` 当作剧情、镜头、资产和生产状态的唯一事实源。先更新 `project.json`，再把目标 Clip 编译并同步到 ToonFlow；用户在 ToonFlow 中完成有效修改后，再把结果回写项目状态。

默认只处理用户指定的项目、剧本和节点。修复 `U07` 不得顺带重置 `U01-U13`。写入提示词不等于授权启动可能产生费用的视频生成；只有用户明确要求生成时才点击或调用生成。

本手册针对当前已验证的本地 ToonFlow SQLite 工作流。应用升级后先重新检查表结构和前端行为，不把旧版本细节当作永久 API。

## 数据层与项目状态

常用数据关系：

| 层级 | ToonFlow 表 | 关键字段 | 用途 |
|---|---|---|---|
| 项目 | `o_project` | `id`、`name`、`videoRatio`、`videoModel` | 锁定目标项目和生成配置 |
| 剧本 | `o_script` | `id`、`projectId`、`name`、`content` | 锁定当前集 |
| 分镜节点 | `o_storyboard` | `id`、`scriptId`、`index`、`trackId`、`prompt`、`videoDesc`、`duration` | 前端分镜层数据 |
| 视频轨道 | `o_videoTrack` | `id`、`prompt`、`duration`、`state`、`videoId`、`selectVideoId` | 实际视频生成区数据 |
| 资产 | `o_assets` | `id`、`name`、`type`、`imageId`、`projectId` | 角色、场景、道具、音频入口 |
| 图片/音频文件 | `o_image` | `id`、`filePath`、`type`、`state` | 资产对应的本地媒体文件 |
| 节点资产 | `o_assets2Storyboard` | `storyboardId`、`assetId` | 当前节点显示的参考素材 |
| 剧本资产 | `o_scriptAssets` | `scriptId`、`assetId` | 当前剧本可用素材池 |
| 角色音色 | `o_assetsRole2Audio` | `assetsRoleId`、`assetsAudioId` | 角色与音频资产绑定 |
| 视频结果 | `o_video` | `videoTrackId`、`filePath`、`state`、`errorReason` | 生成结果与失败信息 |
| 任务状态 | `o_tasks` | `relatedObjects`、`state`、`reason` | 后台任务诊断 |

`Uxx` 是用户可读节点号，通常对应 `o_storyboard.index`；不得据此猜测数据库 ID。每次先解析并记录 `projectId -> scriptId -> storyboardId -> trackId`，再执行任何操作。

## 标准生产流程

1. 读取 `project.json`、正式提示词文档和当前 ToonFlow 数据。
2. 用项目名、画幅、剧本名和节点数量共同确认目标，禁止只凭一个数字 ID 写入。
3. 查看目标节点当前提示词、时长、状态、成片 ID、素材绑定和文件可用性。
4. 若目标 Clip 已 `accepted` 或 ToonFlow 已有选中成片，先保留成片关联；除非用户明确要求重生成，不清空结果。
5. 先按 `prompt-bible.md` 编译并通过提示词圣经质检，再核对对白、参考调度、内部 Shot 时长、必须发生、不得发生和末帧锚点。
6. 同步目标节点的双层提示词、时长、素材和音色。
7. 关闭或离开正在编辑该节点的旧 ToonFlow 页面，再执行数据库写入；写入后重新打开或强制刷新，防止旧页面内存把旧提示词覆盖回来。
8. 使用只读体检脚本并再次直接回读数据库。不要把“脚本运行成功”当作写入成功。
9. 在前端逐项确认缩略图、提示词、时长、模型和画幅，再生成目标节点。
10. 实际查看成片首帧、过程、末帧和声音；接受后把实际终点写回 `project.json`。

## 提示词写入

任何提示词写入前必须通过 `prompt-bible.md`；ToonFlow 只负责存储与执行，不得把未通过圣经质检的旧提示词直接同步到生成轨道。

ToonFlow 的一个视频节点至少有两类提示词：

- `o_storyboard.prompt`：分镜图/首帧提示词；跳过分镜图直接生成视频时，也可保存最终视频提示词。
- `o_storyboard.videoDesc`：分镜节点记录的视频描述。
- `o_videoTrack.prompt`：实际视频生成轨道提示词。

只更新 `o_storyboard.prompt` 会出现“文档和分镜看似正确，生成区仍显示旧提示词”的问题。视频提示词至少要同步到 `o_storyboard.videoDesc` 和 `o_videoTrack.prompt`。

每次写入后必须验证：

- 常规“分镜图 -> 图生视频”模式：`o_storyboard.videoDesc = o_videoTrack.prompt`；`o_storyboard.prompt` 可以保留独立的关键图提示词。
- 跳过分镜图、直接多参考视频模式：`o_storyboard.prompt = o_storyboard.videoDesc = o_videoTrack.prompt`。
- 所有正文比较都做全文精确比较，不能只比较长度。
- 两层 `duration` 数值一致，并等于 Clip 计划时长。
- 至少检查一个新版独有关键句同时存在于 `videoDesc` 和视频轨道；直接视频模式还要存在于 `storyboard.prompt`。
- 提示词中的 `@图片N`、`@音频N` 与前端实际展示顺序一致。

不要假定资产插入顺序就是前端显示顺序。绑定后打开节点确认缩略图顺序，再编译 `@图片N` 映射；顺序变化时只修映射，不改剧情和镜头合同。

默认保留 `state`、`videoId`、`selectVideoId`、分镜 `filePath` 和已有视频记录。只有用户明确要求重生成该节点时，才重置该节点的生成状态；不得批量清空其他节点。

`shouldGenerateImage=0` 只用于已经确认跳过分镜图、直接多参考生成视频的节点。需要首帧图或分镜图时保留原工作流，不要全项目统一改为 `0`。

## 素材与音色绑定

绑定视觉资产时同时检查三层：

1. `o_assets` 中资产属于正确 `projectId`，名称和身份唯一，`imageId` 非空。
2. `o_scriptAssets` 中资产属于当前 `scriptId`，确保剧本素材池可见。
3. `o_assets2Storyboard` 中资产只绑定到需要它的目标节点。

更新节点资产集合时，可在同一事务内删除该 `storyboardId` 的旧映射后写入精确集合；禁止删除整个剧本或项目的映射。绑定完成后按资产名称回读，不只检查数量。

每张参考图都要在提示词里声明主要用途：角色身份、场景结构、道具造型、风格、动作或首帧。不得把场景图里偶然出现的人物迁移为新角色，也不得让风格图覆盖角色三视图。

音色绑定需要同时满足：

- 角色资产与音频资产都存在于当前项目。
- 音频资产有有效媒体记录和本地文件。
- `o_assetsRole2Audio` 正确映射角色资产 ID 到音频资产 ID。
- 音频资产进入当前 `o_scriptAssets`，并在需要的节点提示词中按前端实际顺序声明 `@音频N`。

音色参考只锁定音色、语气、语速和情绪，不把参考音频原文误当成当前台词。无对白节点可保留身份音色参考，但必须在映射中注明“本镜不说话”。

## 本地文件存储

默认数据库位置通常为 `%APPDATA%\toonflow\data\db2.sqlite`，媒体文件通常位于数据库同级的 `oss` 目录。以实际环境为准，不在脚本中假定用户名。

`o_image.filePath` 和 `o_video.filePath` 常保存 URL 相对路径，例如 `/项目ID/role/文件.png`。验证时将开头斜杠去掉后拼到 `data/oss`，并检查：

- 文件真实存在且大小大于零。
- 扩展名和媒体类型相符。
- 图片能实际打开，音频/视频能实际播放。
- 数据库里的 `state` 和 `errorReason` 没有未处理错误。

“资产卡片存在”不代表素材有效。`imageId` 为空、媒体行缺失、路径错误或文件未复制到 `oss`，都会导致前端显示空白或“图片无法显示”。

## 生成前体检

优先运行：

```powershell
python scripts/audit_toonflow_project.py --db "$env:APPDATA\toonflow\data\db2.sqlite" --project-id <项目ID> --script-id <剧本ID> --direct-video
```

只检查一个节点并确认新版关键句：

```powershell
python scripts/audit_toonflow_project.py --db "$env:APPDATA\toonflow\data\db2.sqlite" --project-id <项目ID> --script-id <剧本ID> --unit 7 --contains "新版独有关键句" --direct-video
```

体检通过后仍要在 ToonFlow 前端确认：

- 打开的是正确项目和正确集。
- 节点号、时长和模型正确。
- 所有参考缩略图可见，没有空白卡片。
- 提示词完整显示，开头不是旧版本。
- `@图片N` 和 `@音频N` 与卡片顺序一致。
- 目标节点没有误带其他角色、场景、道具或成片参考。

## 生成与成片回收

一次只生成当前待验收 Clip。上一 Clip 未接受时，下一 Clip 只保持 `prompt_ready`，不要把计划末帧当成真实连续性。

生成完成后实际查看媒体，不凭历史缩略图判断。记录：

- 首帧是否符合计划起点。
- 必须动作是否发生，不得动作是否被提前生成。
- 人物位置、屏幕侧、道具归属和场景地理是否连续。
- 对白说话人、口型、音色、语速和专业词读音是否正确。
- 实际末帧是否能直接承接下一 Clip。

按保留、后期修复、局部编辑、同提示词重抽、重写提示词五级处置。接受成片后，保留 ToonFlow 的 `selectVideoId` 和视频文件，更新 Clip 为 `accepted` 并写入 `actual_end_state`；拒绝片段不得进入后续连续性。

## 常见故障

### 前端仍显示旧提示词

依次检查 `o_storyboard.prompt`、`o_storyboard.videoDesc`、`o_videoTrack.prompt`。直接视频模式要求三处一致；常规图生视频模式要求后两处一致。若数据库已一致但页面仍旧，关闭旧编辑页并重新打开；旧页面可能把内存中的轨道提示词再次保存回数据库。刷新后再回读数据库确认没有反向覆盖。

### 素材卡片空白

检查 `o_assets.imageId -> o_image.id -> o_image.filePath -> data/oss/实际文件`，再检查资产是否同时进入 `o_scriptAssets` 和目标节点的 `o_assets2Storyboard`。不要只重绑卡片而忽略缺失文件。

### 素材已绑定但生成身份错误

检查 `@图片N` 是否和前端顺序一致、参考用途是否写清、是否存在互相冲突的角色图或场景图。先修映射和用途，不用更多形容词掩盖错误参考。

### 音色没有生效

检查音频文件、音频资产、`o_assetsRole2Audio`、`o_scriptAssets` 和提示词 `@音频N` 五处。确认当前说话角色确实有对白，且没有把另一角色的音频卡排在同一编号。

### 视频发起失败

先读取 `o_videoTrack.state/reason`、`o_video.state/errorReason` 和 `o_tasks.state/reason`，再检查模型、时长、参考数量和媒体格式。区分“提示词问题、素材读取问题、模型限制、网络/服务问题”，不要一律重写提示词。

### 修一个节点却影响整集

检查同步脚本是否遍历并重置整集。改为显式接收 `projectId`、`scriptId`、目标 `unit/index`，只更新目标 `storyboardId/trackId`。修改前后比较其他节点的 `state`、`videoId` 和 `selectVideoId`，必须保持不变。

## 数据库写入安全规则

直接写数据库属于低自由度操作，必须满足：

1. 先关闭或离开正在编辑的 ToonFlow 节点，避免缓存回写。
2. 使用 SQLite backup API 生成带时间戳的完整备份，不用文件复制替代正在使用中的数据库备份。
3. 以项目名、画幅、剧本名、节点号和现有轨道关系验证目标。
4. 设置 `busy_timeout`，使用单个事务；失败则完整回滚。
5. 更新语句必须带 `projectId/scriptId/storyboardId/trackId` 等窄条件，检查受影响行数。
6. 默认不删除资产、剧本、分镜、视频和已接受结果。
7. 写入后关闭写连接，再用只读新连接全文回读。
8. 验证不能只看字符长度、数量或脚本退出码，必须核对正文、名称、路径和状态。
9. 重新打开前端后再次回读，确认没有被旧页面覆盖。
10. 保留备份路径和本次唯一修改项，便于最小回滚。

优先为重复操作编写项目无关、参数化、可验证的脚本。禁止把某一集的固定 ID、用户名和资产名称写入彬彬 skill 的通用脚本。

## 完成标准

一次 ToonFlow 节点维护只有同时满足以下条件才算完成：

- `project.json` 与正式提示词文档一致。
- 常规图生视频模式的 `videoDesc` 与视频轨道正文一致；直接视频模式三处正文一致。
- 时长一致，节点状态没有误伤。
- 素材与音色绑定名称正确，媒体文件真实可读。
- 前端刷新后显示正确，且数据库没有被缓存覆盖。
- 生成结果经过实际观看，接受结果的实际末帧已回写项目状态。
- 其他已通过节点、成片和绑定保持不变。
