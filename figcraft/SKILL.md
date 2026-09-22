---
name: figcraft
description: 为中文文章/公众号推文绘制清晰的结构图、流程图、时间线、链路图。用 Python 手写 SVG（figstyle.py 公共库）再经 rsvg-convert 输出 1200px 白底高清 PNG。当用户要求"画结构图/配图/流程图/时间线/链路图/架构示意图"、"给文章出图"、"gen_figs"等时使用。输出 PNG 直接可入 assets/，视觉风格与工作区已发表文章一致。
---

# FigCraft — 文章结构图出图

为文章画一张"比文字更清楚"的结构图：卡片 + 箭头 + 分区 + 时间线，统一视觉语言，输出高清 PNG。

## 何时用

- 文章需要结构图 / 流程图 / 链路图 / 时间线 / 对比图 / 分层架构图
- 目标是公众号正文配图（白底、1200px 宽、中文清晰）
- 不适用：数据统计图表（折线/柱状，请用 matplotlib 脚本）、交互式 HTML 图（用 html-diagram）

## 工作流

1. **读脚本** `scripts/figstyle.py`（`Canvas` + 配色常量），理解可用元素。
2. **规划布局**：先在草稿上定画布尺寸（宽固定 1200，高按内容 500–900）。每张图一个 `Canvas`，一个文件可出多张。先列元素清单：几个卡片、几条箭头、几个分区，再算坐标——**对齐是清晰度的第一要素**：
   - 同层卡片同一 y、等宽或按内容分档；
   - 卡片间距 ≥ 40px，箭头不穿卡片；
   - 箭头 label 放中点上方 8px，避免压线。
3. **写脚本**：在目标目录建 `gen_figs.py`（参考 `scripts/example_gen_figs.py`）：

   ```python
   import sys, os
   sys.path.insert(0, "/opt/pro/vanskill/figcraft/scripts")
   from figstyle import Canvas, BLUE, INK, SUB, BLUE_L, BLUE_B, RED, RED_L, GREEN, GREEN_L, AMBER, AMBER_L, GRAY_L, GRAY_B

   c = Canvas(1200, 560, title="上传链路")
   c.card(60, 160, 220, 80, "本地 Markdown", sub="master.md")
   c.arrow(280, 200, 360, 200, label="渲染")
   c.card(360, 160, 220, 80, "微信 HTML")
   c.save("assets/fig1-pipeline.png")
   ```

4. **出图**：`python3 gen_figs.py`（工作目录 = 选题目录，输出进本目录 `assets/`）。
5. **验收（必做）**：
   - 用读图工具查看每张 PNG，检查：文字无截断/溢出卡片、箭头指向正确、无元素重叠、中文无乱码（应为方块或豆腐字时立即检查字体）；
   - 检查 `assets/*.png` 宽度是否 1200（`python3 -c "from PIL import Image;print(Image.open('assets/fig1.png').size)"` 或 `file assets/*.png`）；
   - 正文引用路径 `assets/xxx.png` 与实际文件名逐一核对（可用工作区 `tools/verify_draft.cjs`）。

## 视觉规范（与已发表文章一致）

- 白底 `#FFFFFF`；标题 26px 加粗 + 底部灰色分隔线；正文 13–16px；副标题比主文字小 4px 用 SUB 灰。
- 语义配色：正常/主流程 = BLUE 系；风险/失败 = RED 系；成功/修复 = GREEN 系；注意/延迟 = AMBER 系；背景分组 = GRAY 虚线 panel。
- 颜色是编码不是装饰：一张图主色只一种（蓝），红绿琥珀只用于需要读者注意的少数元素。
- 时间线：横向节点 + dot + 连线，节点下方两行文字（日期 + 事件）。
- 图底可加一行 `caption` 说明口径/来源。

## 依赖

- `rsvg-convert`（首选）或 `cairosvg`（回退）；中文字体 WenQuanYi Micro Hei（工作区 `.xdg/fonts/`，勿删）。
- 无其他第三方依赖。

## 提示

- 改图只改 `gen_figs.py` 重跑，PNG 永远是产物不是源头。
- 高清大图需要 2x 时：`c.save(path, width=2400)`。
- 不要在图里堆太多字——一屏 ≤ 6 张卡片时最清晰，多了就拆成两张图。
