# 语音翻译流水线 (Voice Translation Pipeline)

本项目是一个端到端的语音翻译桌面端应用程序，基于 Python 与 Tkinter 构建。能够实现以下功能：音频输入 -> ASR(语音识别) -> MT(机器翻译) -> TTS(语音合成) -> 输出目标语言音频文件及运行日志。

## 🎯 核心功能与特性
1. **纯桌面级图形用户界面 (GUI)**：使用 Tkinter 构建，提供可视化音频文件选择、语言配置以及实时运行日志追踪。
2. **多格式音频输入**：原生支持 `WAV` 格式。若本地环境安装了 `ffmpeg`，通过 `pydub` 加持亦完美接纳 `MP3` 等格式的多媒体文件，程序内部会自动进行解码及格式转换。
3. **免秘钥 (Zero-Config) 体验**：
    - **ASR (语音识别)**: 采用 `SpeechRecognition` 调用 Google Web Speech API，零配置开箱即用。
    - **MT (机器翻译)**: 采用 `deep-translator` 接入 Google Translate 服务，免费无额度限制。
    - **TTS (语音合成)**: 采用 `gTTS` (Google原生语音合成)，极端稳定可靠，能避免部分TTS框架经常遇到的网络及流控异常。
4. **加分项与体验优化**：
    - **多语言矩阵**：界面支持一键下拉选择 源语言 与 目标语言（涵盖中、英、日、韩等主流语种）。
    - **性能评估统计**：在控制面板可精准查阅每个处理核心阶段 (ASR, MT, TTS) 以及总体过程的时间开销，方便性能剖析。
    - **健壮的异常干预**：若发生无法识别无声片段或无可用网络连接的情况，程序不会直接崩溃退栈，而是会在日志大屏醒目提示并终止当次任务，状态机可自动平滑复原。

## 🛠️ 技术栈 (Tech Stack)
- **UI 框架**：Tkinter, ttk
- **音频处理**：Pydub, AudioSegment
- **异步与并发**：Python Threading (将任务脱离主线程以避免 GUI 假死)
- **核心管道组件**：
  - ASR: `SpeechRecognition`
  - MT: `deep-translator`
  - TTS: `gTTS`

## ⚙️ 环境依赖 (Dependencies)
- **Python环境**：Python 3.8 或更高版本。
- **系统包工具（可选但强烈推荐）**：如果您需要导入 MP3 等非WAV格式文件，请务必预先在系统安装 [FFmpeg](https://ffmpeg.org/download.html)，并确保可将其配置到系统的环境变量 `PATH` 中。

使用以下命令安装所有 Python 依赖：
```bash
pip install -r requirements.txt
```

## 🚀 如何运行 (How to Run)
1. **获取代码**：下载本仓库到本地，并在终端中进入项目根文件夹文件夹下。
2. **运行启动程序**：
```bash
python main.py
```
3. **界面操作向导**：
    - **第一步**：点击 **“浏览...”** 按钮，选取一段您的待识别本地音频文件 (`.wav` 或 `.mp3`)。
    - **第二步**：在 **“语言设置”** 分区选择 **源语言**（您音频的原始语言类型，如 `zh-CN` 或 `en-US`）及希望转换成的 **目标语言**（如 `en` 表示英语）。
    - **第三步**：点击 **“开始翻译流水线”**。
    - **第四步**：观察下方的结果和日志区域。等待控制台输出 “=== 流水线执行成功！ ===”。
    - **最终产物**：运行成功后，你可以在本目录自动生成的 `output/` 文件夹下随时回溯：
      - `original_text.txt` (识别出的原始文本记录)
      - `translated_text.txt` (翻译后的文本记录)
      - `output_translated_audio.mp3` (最终合成的目标语言语音文件)

## 📁 目录及代码结构 (Project Structure)
```text
voice-translation-pipeline/
├── main.py                  # 主应用文件：包含界面UI逻辑渲染、三步算法流水线的线程分配
├── requirements.txt         # 第三方 Python 库依赖声明文件
├── README.md                # 项目详细使用说明文档 (本文档)
└── output/                  # (运行时自动生成) 数据落地文件夹
    ├── original_text.txt    # 识别出的文字备份
    ├── translated_text.txt  # 翻译出的文字备份
    └── output_translated_audio.mp3 # TTS语音生成结果
```


