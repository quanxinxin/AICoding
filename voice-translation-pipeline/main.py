import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import asyncio
import time
import os
import threading
from pydub import AudioSegment

class VoiceTranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("语音翻译流水线 - Voice Translation Pipeline")
        self.root.geometry("600x700")
        
        self.audio_path = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # 1. 导入音频文件
        frame_file = ttk.LabelFrame(self.root, text="1. 选择音频文件 (WAV/MP3)")
        frame_file.pack(fill="x", padx=10, pady=5)
        
        self.lbl_file = ttk.Label(frame_file, text="未选择文件")
        self.lbl_file.pack(side="left", padx=5, pady=5)
        
        btn_browse = ttk.Button(frame_file, text="浏览...", command=self.browse_file)
        btn_browse.pack(side="right", padx=5, pady=5)
        
        # 语言选择
        frame_lang = ttk.LabelFrame(self.root, text="语言设置 (加分项)")
        frame_lang.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_lang, text="源语言:").grid(row=0, column=0, padx=5, pady=5)
        self.src_lang = ttk.Combobox(frame_lang, values=["zh-CN", "en-US", "ja-JP", "ko-KR"])
        self.src_lang.set("zh-CN")
        self.src_lang.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_lang, text="目标语言:").grid(row=0, column=2, padx=5, pady=5)
        self.tgt_lang = ttk.Combobox(frame_lang, values=["en", "zh-CN", "ja", "ko"])
        self.tgt_lang.set("en")
        self.tgt_lang.grid(row=0, column=3, padx=5, pady=5)
        
        # 控制按钮
        self.btn_start = ttk.Button(self.root, text="开始翻译流水线", command=self.start_pipeline_thread)
        self.btn_start.pack(pady=10)
        
        # 日志和结果显示
        frame_log = ttk.LabelFrame(self.root, text="运行日志与结果")
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.text_log = tk.Text(frame_log, wrap="word", state="disabled")
        self.text_log.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.text_log.config(state="normal")
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)
        self.text_log.config(state="disabled")
        self.root.update_idletasks()
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3"), ("All Files", "*.*")]
        )
        if filename:
            self.audio_path = filename
            self.lbl_file.config(text=os.path.basename(filename))

    def start_pipeline_thread(self):
        if not self.audio_path:
            messagebox.showwarning("警告", "请先选择一个音频文件！")
            return
            
        self.btn_start.config(state="disabled")
        self.text_log.config(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.config(state="disabled")
        
        threading.Thread(target=self.run_pipeline, daemon=True).start()
        
    def run_pipeline(self):
        try:
            total_start_time = time.time()
            self.log("=== 开始语音翻译流水线 ===")
            
            # 预处理：如果是mp3转换为wav，因为SpeechRecognition原生只支持WAV/AIFF/FLAC
            process_path = self.audio_path
            if self.audio_path.lower().endswith('.mp3'):
                self.log("检测到MP3文件，正在转换为WAV格式...")
                t0 = time.time()
                audio = AudioSegment.from_mp3(self.audio_path)
                process_path = "temp_converted.wav"
                audio.export(process_path, format="wav")
                self.log(f"[耗时统计] 音频格式转换耗时: {time.time()-t0:.2f}秒")

            # 1. ASR 阶段
            self.log("\n[1/3] 正在进行 ASR (语音识别)...")
            t_asr_start = time.time()
            recognizer = sr.Recognizer()
            with sr.AudioFile(process_path) as source:
                audio_data = recognizer.record(source)
                
            # 将 zh-CN 转换为 zh-CN 等符合 recognizer 的格式
            asr_lang = self.src_lang.get()
            try:
                # 使用免费的 Google Web Speech API，无需秘钥
                recognized_text = recognizer.recognize_google(audio_data, language=asr_lang)
            except sr.UnknownValueError:
                raise Exception("无法识别音频中的文字 (未听到有效语音)")
            except sr.RequestError as e:
                raise Exception(f"ASR 服务请求失败: {e}")
                
            t_asr_end = time.time()
            self.log(f"ASR识别结果: {recognized_text}")
            self.log(f"[耗时统计] ASR 耗时: {t_asr_end - t_asr_start:.2f}秒")
            
            # 保存原文日志
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "original_text.txt"), "w", encoding="utf-8") as f:
                f.write(recognized_text)

            # 2. MT 阶段
            self.log("\n[2/3] 正在进行 MT (机器翻译)...")
            t_mt_start = time.time()
            tgt_lang_code = self.tgt_lang.get()
            # source language parameter for deep-translator uses 'auto' or 'zh-CN' etc. 'zh-CN' in google ASR -> 'zh-CN', deep translator uses 'zh-CN'
            translator = GoogleTranslator(source='auto', target=tgt_lang_code)
            translated_text = translator.translate(recognized_text)
            
            t_mt_end = time.time()
            self.log(f"MT翻译结果: {translated_text}")
            self.log(f"[耗时统计] MT 耗时: {t_mt_end - t_mt_start:.2f}秒")
            
            # 保存译文日志
            with open(os.path.join(output_dir, "translated_text.txt"), "w", encoding="utf-8") as f:
                f.write(translated_text)
                
            # 3. TTS 阶段
            self.log("\n[3/3] 正在进行 TTS (语音合成)...")
            t_tts_start = time.time()
            
            # 使用更稳定的 gTTS 来替代原本失败的 edge-tts
            output_audio_file = os.path.join(output_dir, "output_translated_audio.mp3")
            
            # 运行同步 gTTS
            tts = gTTS(text=translated_text, lang=tgt_lang_code)
            tts.save(output_audio_file)
            
            t_tts_end = time.time()
            self.log(f"合成音频已保存到: {output_audio_file}")
            self.log(f"[耗时统计] TTS 耗时: {t_tts_end - t_tts_start:.2f}秒")
            
            # 清理临时文件
            if process_path == "temp_converted.wav" and os.path.exists(process_path):
                os.remove(process_path)
                
            total_end_time = time.time()
            self.log(f"\n=== 流水线执行成功！总耗时: {total_end_time - total_start_time:.2f}秒 ===")
            
        except Exception as e:
            self.log(f"\n[错误] 流水线执行失败: {str(e)}")
            messagebox.showerror("运行失败", f"处理过程中发生错误:\n{str(e)}")
        finally:
            self.btn_start.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTranslationApp(root)
    root.mainloop()
