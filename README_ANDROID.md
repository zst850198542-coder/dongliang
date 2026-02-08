# Android 版构建说明

本项目已经配置为可以通过 GitHub Actions 自动构建 Android APK 安装包。

## 如何获取 APK

1. **上传代码到 GitHub**:
   将此文件夹中的所有文件上传到您的 GitHub 仓库。

2. **触发构建**:
   - 如果您刚刚推送了代码，构建可能已经自动开始（参考 `.github/workflows/build_apk.yml` 中的配置）。
   - 或者，在 GitHub 仓库页面，点击 "Actions" 标签页。
   - 选择 "Build Android APK" 工作流。
   - 点击 "Run workflow" 按钮。

3. **下载 APK**:
   - 等待构建完成（通常需要 10-15 分钟）。
   - 点击构建成功的运行记录。
   - 在页面底部的 "Artifacts" 区域，您会看到一个名为 `app-debug` 的文件。
   - 点击下载，解压后即可获得 `.apk` 文件。

4. **安装**:
   - 将 APK 发送到您的 Android 手机。
   - 安装并运行。

## 本地运行（Windows）

您仍然可以在 Windows 上运行此程序进行测试：

```bash
pip install -r requirements.txt
python main.py
```

这将启动一个窗口并打开浏览器访问应用。

## 注意事项

- **首次启动**: 应用首次在手机上启动时可能需要几秒钟来加载 Python 环境，请耐心等待。
- **权限**: 应用需要网络权限来获取 ETF 数据。
