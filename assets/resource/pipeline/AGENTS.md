# Pipeline Agent 指南

本文件专门指导 `assets/resource/pipeline/` 下的 pipeline 编辑。这里的文件是 MaaFramework 资源逻辑，不是普通严格 JSON 配置。

## 模块边界

当前 pipeline 大致按入口与业务模块分布：

- `start_up.json`：启动与 app launch，包括官服启动、服务器选择、登录进入主界面等。
- `activity/`：独立活动 flow，例如友情币、联动活动、魔物讨伐。
- `小号/farm.json`：日常流水线入口与早期串联节点。
- `小号/用户.json`：用户、账号切换相关节点。
- `小号/任务/`：日常任务、周任务、委托等。
- `小号/公会/`：公会、商店、讨伐等。
- `小号/商城/`、`小号/杂货店/`：商店、礼包、月卡、宝库等。
- `小号/笔记/`：笔记及各类副本、活动页签。
- `小号/探索/`、`小号/地图/`：探索、开图、打野猪等世界地图 flow。
- `起号/`：起号 / early-game setup。

新增或移动节点时，尽量放入对应业务模块，避免把跨模块跳转集中塞进单个文件。

## 节点命名

尽量保留已有节点名，因为 `assets/interface.json` 的 `task.entry` 与 `pipeline_override` 可能引用它们。

`FARM_` 是当前日常流水线的主要命名空间。日常 flow 新节点若属于同一流水线，优先沿用 `FARM_` 前缀。

`sub_` 常用于子流程或启动相关节点。修改这类节点时，额外检查是否被 task 或 override 直接引用。

重命名或删除节点前，必须搜索：

以下命令默认在仓库根目录执行：

```powershell
rg -n "节点名" assets\interface.json assets\resource\pipeline
```

如果节点名出现在 `pipeline_override` 中，不要仅修改 pipeline 文件；必须同步评估该 override 的运行意图。

## 常见字段

常见 MaaFramework 字段包括 `recognition`、`action`、`expected`、`template`、`roi`、`target`、`next`、`interrupt`、`on_error`、`post_delay`、`post_wait_freezes`、`focus`、`package`、`begin`、`duration`。

`recognition` 决定识别方式，例如 `OCR`、`TemplateMatch`。修改时确认 `expected`、`template`、`roi` 是否仍与识别方式匹配。

`action` 决定动作，例如 `Click`、`DoNothing`、`StartApp`、`StopApp`、`Swipe`、`StopTask`。不要为了“看起来更简单”改动动作类型。

`next` 决定后续节点，顺序会影响优先匹配与跨模块流转。增删 `next` 前先确认 fallback、循环和退出路径。

`interrupt` 会改变等待与打断行为。重复引用自身的 interrupt 可能是为了重试或等待界面稳定，不要轻易删除。

`on_error` 是异常路径，通常承担兜底返回或停止逻辑。修改前确认失败场景。

对齐新版 MaaFramework 前，先查最新版 pipeline 协议、recognition/action 字段、custom action/custom recognition 接入说明和资源加载规则，再决定是否迁移旧写法。

不要仅凭旧项目经验改字段名或节点结构。字段兼容性以当前目标 MaaFramework 文档、资源检查结果和实际运行行为为准。

## `pipeline_override`

`pipeline_override` 主要写在 `assets/interface.json` 的 task 中，用来按账号、服务器或任务入口覆盖 pipeline 节点行为。

当前存在大量账号/服务器相关 override。它们是已知重构目标，但不是可随意删除的重复内容。

在生成器或受支持配置机制替代前，保留 `pipeline_override` 的行为。修改被 override 的节点时，必须同时检查 override 是否仍然有效。

尤其注意覆盖 `expected`、`next`、`action` 的 override，这些会直接改变登录、选服、账号切换或日常流水线的执行路径。

## JSONC 处理

pipeline 文件可保留 MaaFramework 兼容的 JSONC-like 写法，例如 `//` 注释。

不要剥离注释，不要用严格 JSON 工具批量格式化 pipeline，也不要为了统一缩进而重写整份文件。

若需要工具解析 pipeline，应使用 JSONC-capable parser，或以 MaaFramework 资源检查结果作为准绳。

`assets/interface.json` 与 pipeline 不同：它必须是严格 JSON。不要把 pipeline 的 JSONC 习惯带到 `assets/interface.json`。

## 上游参考

MaaHub 可作为 pipeline、custom、skill 和 experience 组织方式的参考来源，但不能直接替代 MaaZJ 的业务判断。

参考 MaaHub 或其他 MaaFramework 项目时，先确认三件事：目标样例使用的 MaaFramework 版本、样例 pipeline 与 MaaZJ 游戏流程是否同类、样例资源命名和识别方式是否能被当前资源包支持。

可以吸收更清晰的模块拆分、节点命名、debug 记录和 custom 接入方式；不要机械复制社区样例中的节点、图片名、坐标、ROI 或业务流程。

若升级目标涉及 MaaPracticeBoilerplate，只参考其资源组织、脚本和 CI 模式，不用模板覆盖当前 pipeline 业务资源。

## Debug 与验证

修改 pipeline 后，先用搜索确认入口与引用关系：

以下命令默认在仓库根目录执行：

```powershell
rg -n "节点名|图片名|expected文本" assets\interface.json assets\resource\pipeline
```

资源改动完成前运行：

```powershell
python .\check_resource.py .\assets\resource\
```

若涉及图片识别，确认 `template` 指向的图片仍存在于资源图片目录，且文件名未被误改。

若涉及登录、选服、账号切换或跨模块 `next`，优先做手动 debug 或保留更小改动范围，因为这些路径失败后通常会影响多个 task。

## 修改建议

优先做局部、可验证的节点修正。跨模块重排前，先画出入口、主路径、fallback 和停止路径。

新增节点时，给它一个能表达业务位置的名称，并让 `next` 明确回到当前模块出口或下一个模块入口。

删除节点时，不只看当前文件；必须检查全 pipeline、`assets/interface.json`、`pipeline_override` 和相关图片引用。

当发现历史注释或暂时跳过的 `next` 分支时，先保留上下文。注释可能记录了当前自动化不稳定或等待恢复的路径。
