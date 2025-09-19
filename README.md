# Longbo Cloud Autobot

一键运行的长步云（longbo.cloud）航旅积分自动写作与发布工具。项目遵循“发现 → 研究 → 写作 → 配图 → SEO → 发布”全流程自动化，默认每天 08:00 与 16:00 启动批处理。

## 快速开始

```bash
poetry install
cp .env.example .env  # 填入 WordPress 凭据与可选的 API Key
poetry run longbo sync-taxonomy
poetry run longbo start --now
```

- 若 `.env` 中提供 `WP_USER` 与 `WP_APP_PASS`，程序会通过 WordPress REST API 直接发布并设置特色图。
- 未提供凭据时，会在 `./output/` 目录生成完整草稿（HTML + JSON + WebP），终端提示草稿路径。

## 调度运行

- `poetry run longbo start`：启动调度器，按照 `config/schedule.yml` 的时间窗口循环运行。
- `poetry run longbo schedule`：直接进入每日 08:00 / 16:00 阻塞调度。

### Windows 任务计划程序示例

1. 创建基本任务，触发器设置为每天 08:00 和 16:00。
2. 操作填写：
   ```
   Program/script: C:\\Users\\<YOU>\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\longbo-cloud-autobot-<hash>\\Scripts\\poetry.exe
   Add arguments: run longbo start --now
   Start in: C:\\path\\to\\repo
   ```

### macOS launchd 示例

创建 `~/Library/LaunchAgents/cloud.longbo.autobot.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>cloud.longbo.autobot</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/bin/poetry</string>
      <string>run</string>
      <string>longbo</string>
      <string>start</string>
      <string>--now</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/repo</string>
    <key>StartCalendarInterval</key>
    <array>
      <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
      </dict>
      <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>0</integer>
      </dict>
    </array>
    <key>StandardOutPath</key>
    <string>/tmp/longbo-autobot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/longbo-autobot.err</string>
  </dict>
</plist>
```

加载命令：`launchctl load ~/Library/LaunchAgents/cloud.longbo.autobot.plist`

## 数据与配置

- `config/sources.yml`：航司/酒店/银行/积分源 RSS 列表，程序会在首次运行时循环抓取。
- `config/schedule.yml`：调度时间窗口与批次限制。
- `config/thresholds.yml`：去重、评分等阈值。
- `autobot/templates` 与 `autobot/prompts`：写作、FAQ、封面图风格模板。

## 本地草稿结构

当未配置 WordPress 时，`longbo start --now` 会生成：

- `output/<slug>.html`：带 JSON-LD 的完整正文。
- `output/<slug>.json`：标题、摘要、分类、标签、引用来源等元数据。
- `output/cover-*.webp`：OG 封面图，含 ALT 文本。

## 开发脚本

- `make install`：安装依赖。
- `make run`：运行一次完整流程。
- `make lint`：快速语法检查。
- `make fmt`：使用 Black 格式化（可选安装）。

## 许可证

MIT License
