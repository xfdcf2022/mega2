# MEGA2 · 静态章节阅读站

把 MEGA 语料 PDF 整理成离线可双击打开、且可部署到 GitHub Pages 的静态章节阅读网站。

在线地址：<https://xfdcf2022.github.io/mega2/>

## 已收录

| 卷 | 说明 |
|---|---|
| MEGA² II/3 第 3 卷 | Marx, Zur Kritik der politischen Ökonomie (Manuskript 1861–1863) |
| MEGA² II/1.1 第 1 卷 Apparat | Ökonomische Manuskripte 1857–1858 Apparat |
| MEGA² II/1.2 第 2 卷 | Ökonomische Manuskripte und Schriften 1858–1861 |

## 站点功能

- 三个查看面板：**文本 / 原稿 / 对照**（文本来自 PDF 文字层，原稿为页图）
- 右侧滑出章节目录、底栏上一章/下一章，状态（面板、侧栏）跨章节记忆（localStorage）
- 页标页码映射：印刷页号 `[S. …]` 自动恢复，未命中回退 `[PDF页 N]`
- 每页页眉（跑题）独立以 aside 展示，页脚数字进入脚注栏
- 内置章节检索（search-data.js）

## 目录结构

```
books/           网站内容（书籍章节 HTML + 页图 WebP）—— 仓库根即 Pages 根
assets/          站点静态资源（css / js）
grp/             分组页
pdfbook/         构建工具（Python，pymupdf）
config/          catalog.json 卷分组/元数据
docs/            技术文档
```

## 原稿页图压缩方案

- **印刷页 → 1-bit 无损 WebP（1500px）**：黑白二值化，笔画锐利，~49KB/页
- **灰调页 → 灰度 WebP q75（1500px）**：保留灰墨层次，避免二值化失真
- 判定依据：页图像素亮度直方图（白占比 >0.60 且中间调 <0.30 视为印刷页）

## 本地构建

```bash
pip install pymupdf pillow
python3 -m pdfbook.cli \
  --src "2/3.Gesamtausgabe*" "2/1.Okonomische*" "2/2.Larissa*" \
  --out . --toc-max-level 2 --render-images by-mode --img-width 1500 --resume
```

关键参数：

| 参数 | 说明 |
|---|---|
| `--out` | 输出目录；站点在仓库根时用 `.` |
| `--toc-max-level` | 目录深度（默认 2） |
| `--render-images` | `by-mode` / `none` / `all` 页图烘焙策略 |
| `--img-width` | 页图渲染宽度像素 |
| `--footnote-band` | 页脚判定带比例（默认 0.90） |
| `--resume` | 复用 work/ 缓存增量构建 |

## 部署

- 仓库名：`mega2`；Pages 源路径 `/`（仓库根即网站），分支 `main`
- 文件全部为相对路径，本地 `file://` 打开同样可用

## 维护提示

- GitHub Pages 发布上限 1 GB；当前站点约 486 MB，余量约 500 MB
- 重建后旧对象会留在 git 历史中，若体积回落不明显可执行：

```bash
git fetch --prune
git reflog expire --all --expire=now
git gc --prune=now
```