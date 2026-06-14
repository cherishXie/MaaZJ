# R4 Image Reference Audit

Date: 2026-06-09

Source of truth: `assets/interface.json`

Scope: read-only image/template/OCR/ROI reference audit for MaaZJ pipeline resources.

## 结论摘要

- 本报告只读审计 `assets/resource/pipeline/` 与 `assets/resource/image/`，未修改运行资源、图片或 pipeline。
- 当前扫描到 47 个 pipeline JSON 文件、389 个 pipeline 节点、121 个图片文件。
- 识别方式分布：`OCR` 252 个节点、`TemplateMatch` 91 个节点、`ColorMatch` 3 个节点、未声明 `recognition` 43 个节点。
- `template` 引用记录 116 条，去重后引用 74 个图片文件；当前未发现已引用但缺失的图片。
- 疑似未被当前 pipeline `template` 引用的图片有 47 个，只能作为 review 候选，不能作为删除依据。
- OCR/ROI 静态风险候选较多：OCR 节点中 137 个未声明 `roi`，12 个使用大范围 ROI，26 个 ROI 贴边，1 个小 ROI，1 个 regex expected。
- 高优先级截图/debug 候选集中在地图/野猪、登录/选服/账号切换、弹窗关闭、商城/宝库/奖励、活动入口与小推车/邮件收尾路径。

## 输入与边界

读取：

- `AGENTS.md`
- `assets/resource/pipeline/AGENTS.md`
- `.codex/skills/maazj-maafw-refactor/references/refactor-workflow.md`
- `.codex/skills/maazj-maafw-refactor/references/pipeline-rules.md`
- `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md`
- `docs/agent_context/pipeline_flow_map_initial_2026-06-09.md`
- `docs/agent_context/pipeline_graph_audit_2026-06-09.md`
- `assets/resource/pipeline/`
- `assets/resource/image/`

未修改：

- `assets/interface.json`
- `interface.json`
- `assets/resource/pipeline/`
- `assets/resource/image/`
- `agent/`
- `deps/`
- `install/`

V0 边界：

- 以 JSONC-aware 方式只读解析 pipeline。对尾逗号等 MaaFramework 兼容写法仅在内存中容错，不回写、不格式化。
- `template` 引用按字符串、数组和对象值递归提取。
- OCR/ROI 风险是静态候选，不证明真实识别失败。
- 未引用图片候选不等同于无用资源，不得直接用于删除、重命名或移动图片。

## 数据概览

| 项 | 数量 |
| --- | ---: |
| pipeline JSON 文件 | 47 |
| pipeline 节点 | 389 |
| 图片文件 | 121 |
| `template` 引用记录 | 116 |
| unique template 图片 | 74 |
| 已引用但缺失图片 | 0 |
| 疑似未引用图片 | 47 |
| OCR 节点 | 252 |
| TemplateMatch 节点 | 91 |
| ColorMatch 节点 | 3 |
| 未声明 recognition 节点 | 43 |

解析提示：

- `assets/resource/pipeline/小号/商城/巡礼之证.json` 与 `assets/resource/pipeline/小号/床/找回奖励.json` 存在尾逗号写法；本报告按 JSONC-like 边界容错读取。
- 不建议为了工具解析把上述文件 strict-format，因为 pipeline 注释和 JSONC-like 内容受仓库规则保护。

## Template 图片引用完整性

当前未发现 `template` 指向不存在图片文件。

| 分类 | 数量 | 说明 |
| --- | ---: | --- |
| 已引用且存在 | 74 | unique 图片均能在 `assets/resource/image/` 下找到。 |
| 已引用但缺失 | 0 | V0 未发现缺失图片。 |
| 疑似未引用 | 47 | 仅表示当前 pipeline `template` 静态扫描未引用。 |

代表性引用：

| 路径类型 | 代表图片 | 代表节点/文件 | 风险提示 |
| --- | --- | --- | --- |
| 启动/家园入口 | `家园图标.png` | `小号/farm.json`、`小号/商城/商城.json`、`小号/床/床.json`、`小号/杂货店/杂货店.json` | 跨多个模块复用，是主界面稳定点，不应局部替换。 |
| 地图/野猪 | `地图图标.png`、`地图图标2.png`、`地图宝箱.png`、`森之国一.png`、`森之国二.png`、`怪物-野猪*.png` | `小号/地图/打野猪.json` | R2 S6 已标记为真实流程验证候选，图片和 ROI 应绑定截图证据。 |
| 小推车/收尾 | `领取小推车.png`、`绯乐找回.png`、`樱花树.png`、`绯乐*.png`、`苹果树*.png` | `小号/床/小推车.json` | 关联特殊账号收尾 override，不能只按默认 FARM 路径判断。 |
| 活动/奖励 | `红点.png`、`小黑的冒险.png`、`continue.png`、`next.png`、`获得奖励.png` | `小号/联动活动/罗小黑.json`、`小号/精彩活动/`、`小号/笔记/` | 活动开放状态易变，缺截图时不建议重构识别。 |
| 商城/宝库/公会 | `红点.png`、`商店宠物抽.png`、`打折羊*.png`、`打折鸡*.png`、`远征之门*.png` | `小号/商城/`、`小号/公会/` | 多为商店、奖励、活动入口状态，需结合 OCR 与库存/货币状态。 |
| 笔记/副本 | `笔记.png`、`每日活动.png`、`匹配按钮.png`、`挑战对手.png`、`素材秘境-铁石.png`、`auto_add.png` | `小号/笔记/` | 与特殊账号 `FARM_点击笔记.next` 覆盖相关，R8 选试点时需避开高变识别点。 |

## 多处复用图片

| 图片 | 引用次数 | 初判 |
| --- | ---: | --- |
| `红点.png` | 11 | 活动、商城、邮件、笔记、公会等多模块共享状态标记；属于高误伤复用资源。 |
| `家园图标.png` | 8 | 主界面/家园稳定点；影响启动、FARM、商城、床、小推车和杂货店入口。 |
| `auto_add.png` | 5 | 打野猪托管与素材秘境购买数量复用；涉及数值/次数操作。 |
| `笔记.png` | 5 | 多个笔记子 flow 返回笔记入口复用。 |
| `任务菜单.png` | 3 | 任务与用户菜单相关复用。 |
| `next.png` | 3 | 起号与联动活动对话推进复用。 |
| `怪物-野猪.png` 至 `怪物-野猪5.png` | 各 2 | `FARM_打野猪` 与 `FARM_打野猪2` 复用。 |

建议：

- `红点.png`、`家园图标.png`、`auto_add.png`、`笔记.png` 进入 R7 module boundary 的共享资源清单。
- C 类任务若要调整这些图片相关节点，必须先确认影响范围并补截图/debug 证据。

## 疑似未引用图片候选

以下 47 个图片文件未在当前 pipeline `template` 字段中被静态引用：

| 候选图片 |
| --- |
| `active.png` |
| `active_locate.png` |
| `auto_times.png` |
| `back.png` |
| `demo.png` |
| `empty.png` |
| `focus.png` |
| `gift.png` |
| `locate.png` |
| `locate_upper.png` |
| `menu.png` |
| `not_active_locate.png` |
| `任务.png` |
| `前往.png` |
| `启动画面.png` |
| `地图.png` |
| `外观1.png` |
| `外观2.png` |
| `失落女神.png` |
| `失落女神像.png` |
| `妖灵手札.png` |
| `小推车3.png` |
| `小推车晚上.png` |
| `小推车白天.png` |
| `小推车资源.png` |
| `小推车资源领取.png` |
| `怪物-野猪6.png` |
| `怪物-野猪7.png` |
| `怪物.png` |
| `换装备.png` |
| `探索.png` |
| `更换.png` |
| `森林神像.png` |
| `激活.png` |
| `确定.png` |
| `神像.png` |
| `继续挑战.png` |
| `自动打怪标记.png` |
| `苹果树.png` |
| `解锁.png` |
| `购买素材.png` |
| `赛季礼扎.png` |
| `邮件1.png` |
| `邮件2.png` |
| `野怪图标.png` |
| `领取小推车2.png` |
| `领取小推车3.png` |

解释边界：

- 这些候选可能来自历史调试、未来分支、注释分支、非 template 引用、截图证据或尚未挂到 `assets/interface.json` 的 flow。
- 删除或移动前必须重新执行全仓引用搜索，并结合 V1/V2/V3/V4 证据。
- `怪物-野猪6.png`、`怪物-野猪7.png` 与当前已引用的 `怪物-野猪1-5` 同属野猪模板族，优先作为“候选补充模板”而不是删除候选。
- `邮件1.png`、`邮件2.png`、`小推车*.png`、`苹果树.png` 与特殊账号收尾相关，后续 C 类任务不应提前清理。

## OCR/ROI 风险表

静态规则：

- `no_roi`：OCR 节点未声明 `roi`，可能受全屏文本干扰。
- `large_roi`：ROI 面积较大，可能匹配到非目标文字。
- `edge_roi`：ROI 靠近屏幕边界，可能受设备比例、状态栏、底部按钮或缩放影响。
- `small_roi`：ROI 很小，可能对分辨率和字体抗锯齿敏感。
- `multi_expected`：expected 候选较多，可能混合多个状态。
- `regex_expected`：正则 expected，需要确认 MaaFramework 当前版本兼容和真实 OCR 输出。

| 风险 | 数量 | 代表节点 |
| --- | ---: | --- |
| `no_roi` | 137 | `sub_启动杖剑传说官_选择服务器`、`FARM_宝库购买体力`、`FARM_体力不足`、`FARM_点击商城`、`FARM_空白处关闭` |
| `large_roi` | 12 | `FARM_日常任务`、`FARM_周任务领取`、`FARM_混沌点击绯乐`、`FARM_宝库购买限购`、`探索_中间按钮` |
| `edge_roi` | 26 | `FARM_点击委托`、`FARM_委托页面`、`FARM_小地图页面`、`幻兽界面`、`挑战赛界面` |
| `multi_expected` | 7 | `FARM_空白处关闭`、`升级礼包弹窗`、`FARM_委托好感度关闭`、`FARM_达到指定托管次数`、`探索_中间按钮` |
| `small_roi` | 1 | `FARM_托管体力不足` |
| `regex_expected` | 1 | `FARM_托管体力不足` expected `^[0-4]$` |

高优先级 OCR/ROI 候选：

| 节点 | 文件 | 风险 | 原因 |
| --- | --- | --- | --- |
| `sub_启动杖剑传说官_选择服务器` | `assets/resource/pipeline/start_up.json` | no_roi + override | 30 个账号/服务器 task 覆盖 `expected`，真实路径依赖选服 OCR。 |
| `用户切换_选择账号` | `assets/resource/pipeline/小号/用户.json` | override + 列表定位 | 30 个账号 task 覆盖手机号，账号列表滚动稳定性需要 V3/V4。 |
| `FARM_混沌点击绯乐` | `assets/resource/pipeline/小号/地图/打野猪.json` | large_roi | ROI `[22,446,651,616]` 较大，且影响地图/混沌路径。 |
| `FARM_小地图页面` | `assets/resource/pipeline/小号/地图/打野猪.json` | edge_roi | ROI `[7,1106,693,173]` 贴近底部，设备比例风险较高。 |
| `FARM_托管体力不足` | `assets/resource/pipeline/小号/地图/打野猪.json` | small_roi + regex_expected | ROI `[619,35,26,33]` 很小且 expected 为正则。 |
| `FARM_宝库购买限购` | `assets/resource/pipeline/小号/杂货店/杂货店.json` | large_roi | 特殊账号 override 会接入该节点，需单独验证。 |
| `FARM_空白处关闭` | `assets/resource/pipeline/小号/公会/公会.json` | no_roi + multi_expected | 共享弹窗/奖励关闭节点，C5 前需确认复用语义。 |
| `升级礼包弹窗` | `assets/resource/pipeline/小号/床/床.json` | no_roi + multi_expected | 通用遮挡恢复节点，影响多条 FARM 路径。 |
| `探索_中间按钮` | `assets/resource/pipeline/小号/探索/开图.json` | large_roi + edge_roi + multi_expected | 当前 task entry 未触达，若后续启用探索需先补截图。 |

## 截图/debug 证据候选

| 优先级 | 候选 | 证据需求 | 下游消费 |
| --- | --- | --- | --- |
| 高 | S1/S2 启动、公告、选服 | 公告页、服务器列表、目标服务器 OCR 截图 | T6、登录/选服 smoke |
| 高 | S3 账号切换 | 账号列表、目标手机号定位、滑动前后截图 | T6、账号切换 smoke |
| 高 | S6 打野猪 | 地图入口、小地图、森之国定位、野猪模板、托管次数 OCR | R8/C4 或地图专项 |
| 高 | `FARM_世界返回家园` StopTask override | 到达返回节点后的 task 停止日志 | T6、C 类前置验证 |
| 中 | 商城/宝库 | `FARM_宝库购买体力`、`FARM_宝库购买限购`、活动列表状态截图 | C1/C2/R8 |
| 中 | 弹窗关闭 | 升级礼包、礼包、空白处关闭、委托好感度关闭截图 | C5 recovery normalization |
| 中 | 小推车/邮件收尾 | 小推车领取、邮件红点、苹果树/绯乐找回状态截图 | 特殊账号收尾验证 |
| 中 | 活动入口 | 罗小黑联动、刷友情币、精彩活动红点/奖励截图 | C3 活动单 flow |
| 低 | 疑似未引用图片族 | 文件来源、历史用途、是否应保留为候选模板 | T4 脚本或资源治理 review |

## 对下游任务的建议

### R7-module-boundary-doc

- 单列共享图片资源：`家园图标.png`、`红点.png`、`auto_add.png`、`笔记.png`。
- 把共享图片复用与业务跨模块边分开建模，避免把资源复用误判为模块耦合错误。
- 将 `FARM_世界返回家园`、账号/选服 OCR、特殊账号笔记/收尾 override 放入风险登记。

### R8-low-risk-flow-selection

- 首个低风险试点应避开登录、选服、账号切换、地图定位、野猪模板与大范围 OCR。
- 商城/奖励类试点可以考虑，但若涉及 `红点.png`、`家园图标.png`、通用弹窗关闭，需要先收窄识别影响。
- `FARM_宝库购买限购` 因特殊账号 override 接入，应在候选评审中单独标注。

### T4-image-usage-check-script

建议脚本输出字段：

- 图片：`image_name`、`exists`、`referenced_by_count`、`referenced_nodes`、`referenced_files`、`suspected_unused`。
- 节点：`node`、`file`、`recognition`、`template`、`expected`、`roi`、`target`、`next`、`interrupt`。
- 风险：`missing_template`、`multi_reuse`、`cross_module_reuse`、`no_roi`、`large_roi`、`edge_roi`、`small_roi`、`regex_expected`、`multi_expected`。

处理规则：

- 必须 JSONC-aware，支持注释和尾逗号；不得改写 pipeline。
- `template` 需支持字符串、数组和对象形式。
- `suspected_unused` 只能输出候选，不自动生成删除建议。
- 需要保留截图/debug 证据字段，例如 `evidence_required`、`evidence_status`。

### C1-C5

- 涉及 TemplateMatch/OCR/ROI 的 C 类任务，至少应在实现说明中引用本报告中的候选风险，并说明是否需要截图或 debug 证据。
- C5 recovery normalization 不应优先合并弹窗/OCR 关闭节点，除非已有截图证明不同模块语义一致。
- 地图、野猪、托管次数、账号/选服相关识别改动应要求 V3/V4 或明确降级原因。

## V0 验证记录

已完成：

- 47 个 pipeline JSON 文件以 JSONC-aware 方式只读解析；尾逗号仅内存容错。
- 389 个 pipeline 节点识别字段扫描完成。
- 121 个图片文件枚举完成。
- 116 条 template 引用记录提取完成。
- 74 个 unique template 图片全部能在 `assets/resource/image/` 中找到。
- 抽查关键图片文件存在：
  - `家园图标.png`
  - `红点.png`
  - `地图图标.png`
  - `地图宝箱.png`
  - `怪物-野猪.png`
  - `auto_add.png`
  - `笔记.png`
- 抽查关键节点存在：
  - `sub_启动杖剑传说官_选择服务器`
  - `用户切换_选择账号`
  - `FARM_点击世界`
  - `FARM_打野猪`
  - `FARM_托管体力不足`
  - `FARM_宝库购买限购`
  - `FARM_空白处关闭`
  - `升级礼包弹窗`

未执行：

- V1 MaaFramework resource load。本任务只读新增报告，不修改资源。
- V2 task entry 启动验证。
- V3 真实控制器流程验证。
- V4 日志、截图或 debug 证据。
- V5 回归矩阵。

## D4/D5/N1 判断

- D4：暂不需要。R4 的任务矩阵、产物格式和 V0 边界可以承载本次 image usage report 与 OCR/ROI risk table。
- D5：建议后续 T4 或 C 类任务前再检查。本次观察到“疑似未引用图片不得作为删除依据”“共享图片需要单列风险”与现有 AGENTS/skill 规则一致，暂不需要同步新稳定规则。
- N1：暂不需要。本任务只产生 T4 脚本字段建议和 C 类证据要求，没有新增立即实现需求。
