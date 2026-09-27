# TXT → MD（LocalSend 风格便携版）

把你随手写的 `.txt` 笔记用 AI 重排成排版美观的 `.md`，支持后台自动更新和托盘手动转换。

## 功能
- **监视清单**：可添加单个 txt 文件，也可添加文件夹（含子目录，自动跟随其中所有 txt）。
- **自动更新**：清单内文件保存后，延迟约 2 秒自动转换（可在设置里改）。
- **手动转换**：托盘左键单击 = 立即转换清单内全部文件；双击 = 打开最近文件夹。
- **单向生成**：`x.txt` → 同目录 `x.md`；覆盖前会备份为 `x.md.bak`。
- **删除同步**：清单里的 txt 被删除时，对应 md 一并删除，并把文件条目移出清单。
- **明暗主题**：默认跟随系统，可手动切换。

## 使用（打包后的 exe）
1. 双击 `txt2md.exe`。
2. 点「⚙ 设置」，填入你自己的 DeepSeek API Key（`api_base` 默认 `https://api.deepseek.com`，模型 `deepseek-chat`），点「测试连接」确认可用，再「保存设置」。
3. 回主界面点「＋ 文件」或「＋ 文件夹」把要监视的 txt 加进来。
4. 之后正常编辑这些 txt 并保存即可；md 会自动更新。
5. 关闭窗口不会退出，程序缩到右下角托盘。

## 源码运行
```
py -3 -m pip install customtkinter pystray watchdog pillow pyinstaller
py -3 app.py
```

## 打包
双击 `build.bat`，产物在 `dist\txt2md.exe`（记得把同目录的 `prompt.md` 一起带走分发）。

## 文件说明
| 文件 | 说明 |
|---|---|
| `app.py` | 入口：UI 装配、托盘、监听、转换调度 |
| `ui_home.py` / `ui_settings.py` | 主界面 / 设置页 |
| `theme.py` | 配色与圆角令牌 |
| `icons.py` | 运行时绘制的图标 |
| `converter.py` | 调用 AI 并写 md |
| `watcher.py` | 文件夹/文件监听 |
| `tray.py` | 系统托盘 |
| `config.py` | 便携配置读写 |
| `prompt.md` | 给 AI 的排版规则 |
| `config.example.json` | 配置示例 |

## 注意
- 配置保存在程序（或 exe）同目录 `config.json`；目录不可写时回退到 `%APPDATA%\txt2md\`。
- 日志写在同目录 `sync.log`。
- 单个 txt 超过 1MB 会跳过。
- 未签名的 exe 可能被 SmartScreen / 智能应用控制(SAC)拦截，见下方"代码签名"。
- 仅支持 Windows。API 费用由使用者自己的 Key 承担。

## 从源码构建
```
pip install -r requirements.txt pyinstaller
python make_icon.py
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name txt2md --icon icon.ico ^
  --collect-all customtkinter --hidden-import pystray._win32 app.py
```
或直接双击 `build.bat`。CI 构建见 `.github/workflows/build.yml`。

## 代码签名（开源免费）
本项目使用开源许可证（MIT）。未签名的 exe 会被 Windows 智能应用控制(SAC)拦截。
免费签名渠道：

1. **SignPath Foundation**（推荐）：为开源项目免费提供证书，私钥存于 HSM，
   在 CI 中自动签名（信誉由基金会背书）。申请 <https://signpath.org/>，
   通过后在仓库 Secrets 配置 `SIGNPATH_API_TOKEN`、`SIGNPATH_ORGANIZATION_ID`，
   并设置仓库变量 `SIGNPATH_ENABLED=true`，工作流即会自动签名。
2. **Certum - Open Source Code Signing**：面向开源开发者的免费 1 年期证书。

## 许可证
MIT，见 `LICENSE`。
