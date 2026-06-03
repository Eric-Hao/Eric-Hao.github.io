# Eric-Hao.github.io

> 基于 Jekyll 构建的个人学术主页，通过 GitHub Pages 部署。

<p align="center">
  <a href="https://eric-hao.github.io">
    <img src="https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF%E7%BD%91%E7%AB%99-🎯-blue?style=flat-square" alt="Live Site">
  </a>
  <a href="https://github.com/Eric-Hao/Eric-Hao.github.io/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Eric-Hao/Eric-Hao.github.io/pages/pages-build-deployment?style=flat-square&label=Deploy" alt="Deploy">
  </a>
  <a href="https://github.com/Eric-Hao/Eric-Hao.github.io/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF-MIT-green?style=flat-square" alt="License">
  </a>
  <img src="https://img.shields.io/github/last-commit/Eric-Hao/Eric-Hao.github.io?style=flat-square&label=%E6%9B%B4%E6%96%B0" alt="Last Updated">
</p>

---

## 📋 目录

- [关于](#-关于)
- [功能特性](#-功能特性)
- [项目结构](#-项目结构)
- [技术栈](#-技术栈)
- [本地开发](#-本地开发)
- [添加内容](#-添加内容)
- [部署](#-部署)
- [许可证](#-许可证)

---

## 🧑‍💻 关于

网站基于 [Jekyll](https://jekyllrb.com/) 构建，通过 **GitHub Pages** 部署。主题基于 [AcadHomepage](https://github.com/RayeRen/acad-homepage.github.io) 模板并进行了大量自定义改造。

**在线地址：** [https://Eric-Hao.github.io](https://Eric-Hao.github.io)

---

## ✨ 功能特性

- **响应式设计** — 移动友好的学术布局，配备侧边栏导航
- **多板块内容** — 个人简介、新闻动态、论文列表、竞赛荣誉、项目经历、所获奖项、教育背景
- **论文展示** — 带缩略图（PNG + WebP Retina 适配）的论文陈列，支持懒加载
- **Google Scholar 集成** — 通过 GitHub Actions 定时任务自动更新引用统计数据（每日同步）
- **SEO 优化** — 已配置 Google Analytics、Google Search Console、Bing Webmaster、百度站长验证
- **站点地图与 RSS** — 自动生成 `sitemap.xml` 和 RSS Feed
- **容器化开发** — 通过 Podman/Docker 构建，无需本地安装 Ruby 环境

---

## 📁 项目结构

```
.
├── _config.yml                  # 站点配置（作者信息、SEO、统计）
├── _data/
│   └── navigation.yml           # 导航栏链接和锚点
├── _includes/                   # 可复用的 HTML 组件（head、sidebar、SEO 等）
├── _layouts/                    # 页面布局模板
├── _pages/
│   ├── about.md                 # 主页面入口（包含所有板块）
│   └── includes/
│       ├── intro.md             # 个人简介
│       ├── news.md              # 新闻动态
│       ├── publications.md      # 论文列表（含缩略图）
│       ├── competitions.md      # 竞赛获奖
│       ├── projects.md          # 工业项目
│       ├── honors.md            # 荣誉奖项
│       └── educations.md        # 教育经历
├── _sass/                       # SCSS 样式表
├── assets/                      # 静态资源（CSS、JS、字体）
├── images/
│   ├── papers/                  # 论文缩略图（PNG + WebP）
│   ├── competitions/            # 竞赛缩略图
│   ├── projects/                # 项目截图
│   ├── eric-hao.jpg             # 头像（JPEG 格式）
│   └── eric-hao.webp            # 头像（WebP 格式）
├── google_scholar_crawler/      # Google Scholar 引用抓取脚本（Python）
├── github_myprofile_updater/    # GitHub 个人主页自动更新
├── .github/workflows/           # GitHub Actions 工作流
├── Gemfile                      # Ruby 依赖
├── run_server.sh                # 本地预览辅助脚本
└── README.md                    # 英文说明文档
```

---

## 🛠 技术栈

| 层级          | 技术                                                    |
|---------------|---------------------------------------------------------|
| **静态站点**  | [Jekyll](https://jekyllrb.com/) (Ruby)                 |
| **托管**      | [GitHub Pages](https://pages.github.com/)              |
| **模板引擎**  | Liquid + YAML 前置元数据                                 |
| **样式**      | SCSS → 压缩 CSS                                         |
| **标记语言**  | Markdown（GFM，kramdown 解析器）                         |
| **SEO**       | Google Analytics、Search Console、Bing、百度站长验证     |
| **自动化**    | GitHub Actions（部署 + Google Scholar 抓取）             |
| **本地开发**  | Podman / Docker + Python 3 HTTP 服务器                   |

---

## 🚀 本地开发

### 前置条件

- [**Podman**](https://podman.io/)（或 Docker）— 在容器中运行 Jekyll，无需本地安装 Ruby
- **Python 3** — 用于预览构建后的静态站点

```bash
podman --version   # 应显示 5.x 或更高版本
```

> **提示：** 如果使用 Docker，将以下命令中的 `podman` 替换为 `docker` 即可。

### 构建

```bash
# 确保 _site 目录存在且权限正确
mkdir -p _site && chmod 777 _site

# 启动 Podman 虚拟机（macOS 需要，Linux 可跳过）
podman machine start

# 构建站点
podman run --rm \
  --volume="$PWD:/srv/jekyll:Z" \
  jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build"
```

构建产物输出到 `_site/` 目录。

### 预览

```bash
cd _site
python3 -m http.server 4000
```

在浏览器中打开 **http://localhost:4000**。按 `Ctrl+C` 停止服务。

### 一行命令（构建 + 预览）

```bash
podman run --rm --volume="$PWD:/srv/jekyll:Z" jekyll/jekyll:4.2.2 \
  sh -c "bundle install 2>&1 | tail -1 && bundle exec jekyll build" \
  && cd _site && python3 -m http.server 4000
```

### 替代方案：原生 Ruby

项目提供了 `run_server.sh` 便捷脚本，支持原生 Ruby（rbenv）或 Docker 两种方式启动：

```bash
./run_server.sh
# 选择 1 使用原生 Ruby，选择 2 使用 Docker
```

### 平台说明

- **Apple Silicon（arm64）：** `jekyll/jekyll:4.2.2` 是 linux/amd64 镜像，Podman 通过 QEMU 模拟运行，`image platform does not match` 警告无害
- **不支持 `jekyll serve`：** 该容器中的 Ruby 3.x 已移除 `webrick`，需使用 `jekyll build` + Python 服务器替代
- **端口冲突：** 若 4000 端口被占用，可更换端口：`python3 -m http.server 4001`

### 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| `Permission denied @ dir_s_mkdir - _site` | `mkdir -p _site && chmod 777 _site` |
| `podman machine not running` | `podman machine start` |
| 端口 4000 被占用 | `python3 -m http.server 4001` |
| `no implicit conversion of Hash into Integer` | 使用 `jekyll build`，不要用 `jekyll serve` |
| Docker 卷挂载错误 | 移除 `:Z` 后缀（macOS），使用 `--volume="$PWD:/srv/jekyll"` |

---

## 📝 添加内容

### 新增论文

1. **缩略图** — 添加图片到 `images/papers/`（同时提供 PNG 和 WebP 格式）
2. **条目** — 按照现有的 `paper-box` 模板格式，在 `_pages/includes/publications.md` 中添加条目
3. **懒加载** — 确保 `<img>` 标签中包含 `loading="lazy"` 属性

### 图片优化

缩略图渲染最大宽度为 **400px**。源图片建议保持 **800px** 宽度（2× Retina 适配）：

```bash
# 单张图片缩放（macOS 内置工具，无需额外安装）
sips --resampleWidth 800 --setProperty formatOptions best images/papers/example.png

# 批量处理所有超过 500KB 的 PNG
for f in images/papers/*.png; do
  kb=$(wc -c < "$f" | awk '{printf "%d", $1/1024}')
  if [ $kb -gt 500 ]; then
    sips --resampleWidth 800 --setProperty formatOptions best "$f" --out "$f"
  fi
done
```

进一步压缩（需安装 Homebrew）：

```bash
brew install optipng pngquant

# 无损压缩
optipng -o7 images/papers/*.png

# 有损压缩（80-95% 质量）
pngquant --quality=80-95 --force --ext .png images/papers/*.png
```

### 更新头像

1. 将 JPEG 版本保存到 `images/eric-hao.jpg`
2. 转换为 WebP 格式以支持新一代图片格式：
   ```bash
   brew install webp
   cwebp images/eric-hao.jpg -o images/eric-hao.webp
   ```

---

## 🌐 部署

### 自动部署

推送到 `main` 分支后 — GitHub Pages 会自动通过 `pages/pages-build-deployment` 工作流完成构建和部署，无需手动操作。

### Google Scholar 自动更新

引用统计数据通过 `google_scholar_crawler` GitHub Action 在 **每天 UTC 08:00（北京时间 16:00）** 自动更新。需要：

1. 在仓库 Settings → Secrets and variables → Actions 中配置 **`GOOGLE_SCHOLAR_ID`** 密钥
2. Python 爬虫脚本位于 `google_scholar_crawler/` 目录下

### GitHub 个人主页自动更新

`github_myprofile_updater/` 工作流会自动同步个人资料元数据（如置顶仓库、个人简介等）到 GitHub 主页。

---

## 📄 许可证

本项目基于 MIT 许可证开源。详情请参阅 [LICENSE](./LICENSE) 文件。

---

<p align="center">
  <sub>用 ❤️ 构建，基于 Jekyll + GitHub Pages</sub>
</p>