#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打字速度检测软件
主程序入口文件

作者: AI Assistant
版本: 1.0.0
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import json
import os
from datetime import datetime
import random
try:
    from zhipuai import ZhipuAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# 设置CustomTkinter主题
ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"


class TypingSpeedTest:
    def __init__(self):
        # 初始化主窗口
        self.root = ctk.CTk()
        self.root.title("打字速度检测器 v1.0")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 测试状态变量
        self.is_testing = False
        self.start_time = None
        self.current_text = ""
        self.user_input = ""
        self.current_position = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0
        self.accuracy = 100
        
        # 历史记录
        self.history_file = "typing_history.json"
        self.load_history()

        # AI配置
        self.config_file = "config.json"
        self.ai_client = None
        self.ai_style = "随机"  # 默认风格
        self.load_config()
        
        # 当前语言模式
        self.current_language = "english"  # "english" 或 "chinese"

        # 英文测试文本库
        self.english_texts = [
            "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet at least once.",
            "Python is a high-level programming language that emphasizes code readability and simplicity.",
            "Artificial intelligence is transforming the way we work, learn, and interact with technology.",
            "The future belongs to those who believe in the beauty of their dreams and work hard to achieve them.",
            "In the digital age, typing skills have become essential for effective communication and productivity.",
            "Practice makes perfect, and consistent effort leads to remarkable improvement in any skill.",
            "Technology has revolutionized our daily lives, making tasks easier and more efficient than ever before.",
            "Learning new skills requires patience, dedication, and the willingness to embrace challenges.",
            "The internet has connected people from all corners of the world, creating a global community.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts most."
        ]

        # 中文测试文本库
        self.chinese_texts = [
            "熟能生巧，勤能补拙。只有通过不断的练习，才能提高打字速度和准确率。",
            "科技改变生活，创新驱动发展。人工智能正在深刻地改变着我们的工作和生活方式。",
            "学而时习之，不亦说乎。学习是一个持续的过程，需要我们保持好奇心和求知欲。",
            "千里之行，始于足下。每一个伟大的成就都是从小小的步骤开始的。",
            "工欲善其事，必先利其器。掌握好的工具和技能是成功的重要基础。",
            "海纳百川，有容乃大。包容和理解是人际交往中最重要的品质之一。",
            "书山有路勤为径，学海无涯苦作舟。知识的获取需要我们付出努力和坚持。",
            "天行健，君子以自强不息。面对困难和挑战，我们要保持积极向上的态度。",
            "己所不欲，勿施于人。这是中华文化中关于道德修养的重要思想。",
            "路漫漫其修远兮，吾将上下而求索。追求真理和知识的道路虽然漫长，但值得我们坚持。"
        ]

        # 当前文本库
        self.text_samples = self.english_texts
        
        self.setup_ui()
        self.select_random_text()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_label = ctk.CTkLabel(
            self.root, 
            text="🚀 打字速度检测器", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 统计信息框架
        stats_frame = ctk.CTkFrame(self.root)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        # 统计标签
        self.wpm_label = ctk.CTkLabel(
            stats_frame, 
            text="WPM: 0", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.wpm_label.pack(side="left", padx=20, pady=10)
        
        self.accuracy_label = ctk.CTkLabel(
            stats_frame, 
            text="准确率: 100%", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.accuracy_label.pack(side="left", padx=20, pady=10)
        
        self.time_label = ctk.CTkLabel(
            stats_frame, 
            text="时间: 0s", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.time_label.pack(side="left", padx=20, pady=10)
        
        self.progress_label = ctk.CTkLabel(
            stats_frame, 
            text="进度: 0%", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.progress_label.pack(side="right", padx=20, pady=10)
        
        # 文本显示区域
        text_frame = ctk.CTkFrame(self.root)
        text_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        text_label = ctk.CTkLabel(text_frame, text="待打字文本:", font=ctk.CTkFont(size=16, weight="bold"))
        text_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 使用Text widget来支持文本高亮
        self.text_display = tk.Text(
            text_frame,
            height=8,
            font=("Consolas", 14),
            wrap=tk.WORD,
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#1f538d",
            relief="flat",
            padx=15,
            pady=15,
            state="disabled"
        )
        self.text_display.pack(padx=10, pady=5, fill="both", expand=True)
        
        # 用户输入区域
        input_label = ctk.CTkLabel(text_frame, text="请在此输入:", font=ctk.CTkFont(size=16, weight="bold"))
        input_label.pack(anchor="w", padx=10, pady=(15, 5))
        
        self.input_textbox = ctk.CTkTextbox(
            text_frame,
            height=100,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.input_textbox.pack(padx=10, pady=5, fill="x")
        self.input_textbox.bind("<KeyRelease>", self.on_text_change)
        self.input_textbox.bind("<Key>", self.on_key_press)
        
        # 控制按钮框架
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20, padx=20, fill="x")
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="开始测试",
            command=self.start_test,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120
        )
        self.start_button.pack(side="left", padx=10)
        
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="重置",
            command=self.reset_test,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120
        )
        self.reset_button.pack(side="left", padx=10)
        
        self.new_text_button = ctk.CTkButton(
            button_frame,
            text="新文本",
            command=self.select_random_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120
        )
        self.new_text_button.pack(side="left", padx=10)
        
        self.history_button = ctk.CTkButton(
            button_frame,
            text="历史记录",
            command=self.show_history,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120
        )
        self.history_button.pack(side="right", padx=10)

        self.language_button = ctk.CTkButton(
            button_frame,
            text="中文模式",
            command=self.toggle_language,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120
        )
        self.language_button.pack(side="right", padx=10)

        self.settings_button = ctk.CTkButton(
            button_frame,
            text="⚙️ 设置",
            command=self.show_settings,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=100
        )
        self.settings_button.pack(side="right", padx=10)

        # AI文本生成按钮
        self.ai_text_button = ctk.CTkButton(
            button_frame,
            text="🤖 AI文本",
            command=self.generate_ai_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120,
            state="disabled" if not AI_AVAILABLE else "normal"
        )
        self.ai_text_button.pack(side="left", padx=10)
        
        # 配置文本高亮标签
        self.text_display.tag_configure("correct", background="#2d5a2d", foreground="#90ee90")
        self.text_display.tag_configure("incorrect", background="#5a2d2d", foreground="#ff6b6b")
        self.text_display.tag_configure("current", background="#4a4a4a", foreground="#ffff00")
        self.text_display.tag_configure("remaining", background="#2b2b2b", foreground="#ffffff")
        
    def toggle_language(self):
        """切换语言模式"""
        if self.current_language == "english":
            self.current_language = "chinese"
            self.text_samples = self.chinese_texts
            self.language_button.configure(text="English")
        else:
            self.current_language = "english"
            self.text_samples = self.english_texts
            self.language_button.configure(text="中文模式")

        # 重置当前测试并选择新文本
        self.reset_test()
        self.select_random_text()

    def select_random_text(self):
        """选择随机文本"""
        self.current_text = random.choice(self.text_samples)
        self.update_text_display()
        
    def update_text_display(self):
        """更新文本显示"""
        self.text_display.config(state="normal")
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, self.current_text)
        self.text_display.tag_add("remaining", 1.0, tk.END)
        self.text_display.config(state="disabled")
        
    def start_test(self):
        """开始测试"""
        if not self.is_testing:
            self.is_testing = True
            self.start_time = time.time()
            self.start_button.configure(text="测试中...", state="disabled")
            self.input_textbox.delete("1.0", tk.END)
            self.input_textbox.focus()
            self.update_stats_timer()
            
    def reset_test(self):
        """重置测试"""
        self.is_testing = False
        self.start_time = None
        self.current_position = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0
        self.accuracy = 100
        
        self.start_button.configure(text="开始测试", state="normal")
        self.input_textbox.delete("1.0", tk.END)
        self.update_text_display()
        self.update_stats_display()
        
    def on_key_press(self, event):
        """处理按键事件"""
        # 只有在输入可见字符时才开始测试
        if not self.is_testing and event.char and event.char.isprintable():
            self.start_test()
            
    def on_text_change(self, event):
        """处理文本变化"""
        current_input = self.input_textbox.get("1.0", tk.END).rstrip('\n')

        # 如果还没开始测试，但用户已经输入了内容，则自动开始
        if not self.is_testing and current_input:
            self.start_test()

        if not self.is_testing:
            return

        self.user_input = current_input
        self.calculate_stats()
        self.highlight_text()

        # 检查是否完成
        if len(self.user_input) >= len(self.current_text):
            self.finish_test()
            
    def calculate_stats(self):
        """计算统计数据"""
        if not self.start_time:
            return
            
        # 计算时间
        elapsed_time = time.time() - self.start_time
        
        # 计算正确字符数和总字符数
        self.total_chars = len(self.user_input)
        self.correct_chars = 0
        
        for i in range(min(len(self.user_input), len(self.current_text))):
            if self.user_input[i] == self.current_text[i]:
                self.correct_chars += 1
                
        # 计算WPM (Words Per Minute)
        if elapsed_time > 0:
            if self.current_language == "chinese":
                # 中文按字符计算，每个汉字算作一个词
                self.wpm = int(self.correct_chars / (elapsed_time / 60))
            else:
                # 英文按标准计算，5个字符算作一个词
                self.wpm = int((self.correct_chars / 5) / (elapsed_time / 60))
            
        # 计算准确率
        if self.total_chars > 0:
            self.accuracy = int((self.correct_chars / self.total_chars) * 100)
        else:
            self.accuracy = 100
            
    def highlight_text(self):
        """高亮显示文本"""
        self.text_display.config(state="normal")
        
        # 清除所有标签
        for tag in ["correct", "incorrect", "current", "remaining"]:
            self.text_display.tag_remove(tag, 1.0, tk.END)
            
        user_len = len(self.user_input)
        text_len = len(self.current_text)
        
        # 标记已输入的字符
        for i in range(min(user_len, text_len)):
            start_pos = f"1.{i}"
            end_pos = f"1.{i+1}"
            
            if self.user_input[i] == self.current_text[i]:
                self.text_display.tag_add("correct", start_pos, end_pos)
            else:
                self.text_display.tag_add("incorrect", start_pos, end_pos)
                
        # 标记当前位置
        if user_len < text_len:
            current_pos = f"1.{user_len}"
            next_pos = f"1.{user_len + 1}"
            self.text_display.tag_add("current", current_pos, next_pos)
            
        # 标记剩余文本
        if user_len < text_len:
            remaining_start = f"1.{user_len + 1}"
            self.text_display.tag_add("remaining", remaining_start, tk.END)
            
        self.text_display.config(state="disabled")
        
    def update_stats_display(self):
        """更新统计显示"""
        self.wpm_label.configure(text=f"WPM: {self.wpm}")
        self.accuracy_label.configure(text=f"准确率: {self.accuracy}%")
        
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.time_label.configure(text=f"时间: {elapsed}s")
        else:
            self.time_label.configure(text="时间: 0s")
            
        # 计算进度
        if len(self.current_text) > 0:
            progress = int((len(self.user_input) / len(self.current_text)) * 100)
            progress = min(progress, 100)
            self.progress_label.configure(text=f"进度: {progress}%")
        else:
            self.progress_label.configure(text="进度: 0%")
            
    def update_stats_timer(self):
        """定时更新统计"""
        if self.is_testing:
            self.update_stats_display()
            self.root.after(1000, self.update_stats_timer)
            
    def finish_test(self):
        """完成测试"""
        if not self.is_testing:
            return

        self.is_testing = False
        if self.start_time is None:
            return
        elapsed_time = time.time() - self.start_time

        # 保存结果到历史记录
        result = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "wpm": self.wpm,
            "accuracy": self.accuracy,
            "time": int(elapsed_time),
            "text_length": len(self.current_text),
            "language": self.current_language,
            "correct_chars": self.correct_chars,
            "total_chars": self.total_chars
        }

        self.history.append(result)
        self.save_history()

        # 显示专业测试报告
        self.show_test_report(result, elapsed_time)

        self.start_button.configure(text="开始测试", state="normal")
        
    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except:
            self.history = []
            
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('zhipu_api_key', '')
                    self.ai_style = config.get('ai_style', '随机')
                    if api_key and AI_AVAILABLE:
                        try:
                            self.ai_client = ZhipuAI(api_key=api_key)
                        except NameError:
                            self.ai_client = None
        except:
            pass

    def save_config(self, api_key, ai_style=None):
        """保存配置"""
        try:
            if ai_style is not None:
                self.ai_style = ai_style

            config = {
                'zhipu_api_key': api_key,
                'ai_style': self.ai_style
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # 初始化AI客户端
            if api_key and AI_AVAILABLE:
                try:
                    self.ai_client = ZhipuAI(api_key=api_key)
                    self.ai_text_button.configure(state="normal")
                except NameError:
                    self.ai_client = None
                    self.ai_text_button.configure(state="disabled")
            else:
                self.ai_client = None
                self.ai_text_button.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            
    def show_history(self):
        """显示历史记录"""
        if not self.history:
            messagebox.showinfo("历史记录", "暂无历史记录")
            return
            
        # 创建历史记录窗口
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("历史记录")

        # 获取主窗口位置并计算历史窗口位置
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        history_width = 650
        history_height = 450

        # 设置窗口位置在主窗口中心偏上
        x = main_x + (main_width - history_width) // 2
        y = main_y + (main_height - history_height) // 2 - 50

        # 检查屏幕边界
        if x < 0: x = 20
        if y < 0: y = 20

        history_window.geometry(f"{history_width}x{history_height}+{x}+{y}")
        history_window.resizable(True, True)
        
        # 标题
        title_label = ctk.CTkLabel(
            history_window, 
            text="📊 历史记录", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 统计信息
        if self.history:
            best_wpm = max(record['wpm'] for record in self.history)
            avg_wpm = sum(record['wpm'] for record in self.history) / len(self.history)
            avg_accuracy = sum(record['accuracy'] for record in self.history) / len(self.history)
            
            stats_label = ctk.CTkLabel(
                history_window,
                text=f"测试次数: {len(self.history)} | 最佳WPM: {best_wpm} | 平均WPM: {avg_wpm:.1f} | 平均准确率: {avg_accuracy:.1f}%",
                font=ctk.CTkFont(size=14)
            )
            stats_label.pack(pady=5)
        
        # 历史记录列表
        history_frame = ctk.CTkScrollableFrame(history_window)
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 显示最近的20条记录
        recent_history = self.history[-20:]
        recent_history.reverse()
        
        for i, record in enumerate(recent_history):
            # 获取语言信息，兼容旧记录
            language = record.get('language', 'english')
            lang_text = "中文" if language == "chinese" else "英文"

            record_text = f"{record['date']} | {lang_text} | WPM: {record['wpm']} | 准确率: {record['accuracy']}% | 时间: {record['time']}s"
            record_label = ctk.CTkLabel(
                history_frame,
                text=record_text,
                font=ctk.CTkFont(size=12)
            )
            record_label.pack(pady=2, anchor="w")

    def show_settings(self):
        """显示设置窗口"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("设置")

        # 获取主窗口位置并计算设置窗口位置
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()

        settings_width = 520
        settings_height = 400

        # 设置窗口位置在主窗口右侧
        x = main_x + main_width + 20
        y = main_y + 50

        # 检查屏幕边界
        screen_width = settings_window.winfo_screenwidth()
        if x + settings_width > screen_width:
            x = main_x - settings_width - 20  # 如果右侧放不下，放到左侧
            if x < 0:
                x = 50  # 如果左侧也放不下，居中显示

        settings_window.geometry(f"{settings_width}x{settings_height}+{x}+{y}")
        settings_window.transient(self.root)
        settings_window.grab_set()
        settings_window.resizable(False, False)

        # 标题
        title_label = ctk.CTkLabel(
            settings_window,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)

        # AI配置框架
        ai_frame = ctk.CTkFrame(settings_window)
        ai_frame.pack(pady=10, padx=20, fill="x")

        ai_title = ctk.CTkLabel(
            ai_frame,
            text="🤖 AI配置 (智谱AI GLM-4-Flash)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ai_title.pack(pady=10)

        # API Key输入
        api_key_label = ctk.CTkLabel(ai_frame, text="API Key:")
        api_key_label.pack(pady=(10, 5))

        # 获取当前API Key
        current_key = ""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    current_key = config.get('zhipu_api_key', '')
        except:
            pass

        api_key_entry = ctk.CTkEntry(
            ai_frame,
            width=400,
            placeholder_text="请输入智谱AI的API Key",
            show="*"
        )
        api_key_entry.pack(pady=5)
        if current_key:
            api_key_entry.insert(0, current_key)

        # 说明文本
        info_label = ctk.CTkLabel(
            ai_frame,
            text="获取API Key: https://bigmodel.cn/dev/activities/free/glm-4-flash",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=5)

        # 风格选择
        style_label = ctk.CTkLabel(ai_frame, text="文本风格:")
        style_label.pack(pady=(15, 5))

        style_options = ["随机", "科技", "生活", "学习", "工作", "文学", "新闻", "故事", "哲理", "历史"]
        style_var = ctk.StringVar(value=self.ai_style)

        style_menu = ctk.CTkOptionMenu(
            ai_frame,
            values=style_options,
            variable=style_var,
            width=200
        )
        style_menu.pack(pady=5)

        # 按钮框架
        button_frame = ctk.CTkFrame(settings_window)
        button_frame.pack(pady=20, fill="x", padx=20)

        def save_settings():
            api_key = api_key_entry.get().strip()
            selected_style = style_var.get()
            self.save_config(api_key, selected_style)
            messagebox.showinfo("成功", "设置已保存！")
            settings_window.destroy()

        def test_api():
            api_key = api_key_entry.get().strip()
            if not api_key:
                messagebox.showerror("错误", "请输入API Key")
                return

            try:
                if not AI_AVAILABLE:
                    messagebox.showerror("错误", "AI功能不可用，请安装zhipuai库")
                    return
                test_client = ZhipuAI(api_key=api_key)
                response = test_client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": "你好"}],
                    max_tokens=10
                )
                messagebox.showinfo("成功", "API Key验证成功！")
            except Exception as e:
                messagebox.showerror("错误", f"API Key验证失败: {e}")

        save_button = ctk.CTkButton(
            button_frame,
            text="保存设置",
            command=save_settings,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_button.pack(side="left", padx=10, pady=10)

        test_button = ctk.CTkButton(
            button_frame,
            text="测试API",
            command=test_api,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        test_button.pack(side="left", padx=10, pady=10)

        close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            command=settings_window.destroy,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        close_button.pack(side="right", padx=10, pady=10)

    def generate_ai_text(self):
        """使用AI生成测试文本"""
        if not self.ai_client:
            messagebox.showerror("错误", "请先在设置中配置API Key")
            return

        try:
            # 根据当前语言和设置的风格生成文本
            language = self.current_language
            style = self.ai_style

            # 如果风格是随机，则随机选择一个
            if style == "随机":
                style_options = ["科技", "生活", "学习", "工作", "文学", "新闻", "故事", "哲理", "历史"]
                style = random.choice(style_options)

            # 构建提示词
            if language == "chinese":
                system_prompt = f"请生成一段关于'{style}'主题的中文文本，适合打字练习使用。要求：1.长度在50-100字之间 2.语言流畅自然 3.包含常用汉字 4.避免生僻字词 5.内容积极正面 6.符合{style}主题特色"
            else:
                system_prompt = f"Please generate an English text about '{style}' suitable for typing practice. Requirements: 1.Length between 50-150 characters 2.Natural and fluent language 3.Use common words 4.Avoid complex vocabulary 5.Positive content 6.Match the {style} theme"

            # 显示生成中的提示
            self.ai_text_button.configure(text="生成中...", state="disabled")
            self.root.update()

            response = self.ai_client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"生成{style}主题的打字练习文本"}
                ],
                max_tokens=200,
                temperature=0.7
            )

            generated_text = response.choices[0].message.content
            if generated_text is None:
                generated_text = "生成失败，请重试"
            else:
                generated_text = generated_text.strip()

            # 使用生成的文本
            self.current_text = generated_text
            self.reset_test()
            self.update_text_display()

            # 恢复按钮状态
            self.ai_text_button.configure(text="🤖 AI文本", state="normal")

        except Exception as e:
            # 恢复按钮状态
            self.ai_text_button.configure(text="🤖 AI文本", state="normal")
            messagebox.showerror("错误", f"生成文本失败: {e}")

    def show_test_report(self, result, elapsed_time):
        """显示专业测试报告"""
        report_window = ctk.CTkToplevel(self.root)
        report_window.title("📊 测试报告")

        # 获取主窗口位置和大小
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # 设置报告窗口大小
        report_width = 750
        report_height = 650

        # 计算居中位置，稍微偏右避免完全遮挡
        x = main_x + (main_width - report_width) // 2 + 50
        y = main_y + (main_height - report_height) // 2

        # 确保窗口不会超出屏幕边界
        screen_width = report_window.winfo_screenwidth()
        screen_height = report_window.winfo_screenheight()

        if x + report_width > screen_width:
            x = screen_width - report_width - 20
        if y + report_height > screen_height:
            y = screen_height - report_height - 20
        if x < 0:
            x = 20
        if y < 0:
            y = 20

        report_window.geometry(f"{report_width}x{report_height}+{x}+{y}")
        report_window.transient(self.root)
        report_window.grab_set()
        report_window.resizable(True, True)  # 允许用户调整大小

        # 标题
        title_label = ctk.CTkLabel(
            report_window,
            text="📊 打字测试完成报告",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 创建滚动框架
        scrollable_frame = ctk.CTkScrollableFrame(report_window, width=650, height=450)
        scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 基本信息区域
        basic_frame = ctk.CTkFrame(scrollable_frame)
        basic_frame.pack(pady=10, padx=10, fill="x")

        basic_title = ctk.CTkLabel(
            basic_frame,
            text="📈 基本测试数据",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        basic_title.pack(pady=10)

        # 基本数据
        language_text = "中文" if result["language"] == "chinese" else "英文"
        basic_info = [
            f"🌍 测试语言: {language_text}",
            f"⏱️  测试时间: {result['time']}秒 ({elapsed_time:.1f}秒)",
            f"📝 文本长度: {result['text_length']}字符",
            f"✅ 正确字符: {result['correct_chars']}个",
            f"❌ 错误字符: {result['total_chars'] - result['correct_chars']}个",
            f"📊 总输入字符: {result['total_chars']}个"
        ]

        for info in basic_info:
            info_label = ctk.CTkLabel(
                basic_frame,
                text=info,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            info_label.pack(pady=2, padx=20, fill="x")

        # 核心指标区域
        metrics_frame = ctk.CTkFrame(scrollable_frame)
        metrics_frame.pack(pady=10, padx=10, fill="x")

        metrics_title = ctk.CTkLabel(
            metrics_frame,
            text="🎯 核心性能指标",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        metrics_title.pack(pady=10)

        # 计算更多指标
        chars_per_second = result['correct_chars'] / elapsed_time if elapsed_time > 0 else 0
        error_rate = ((result['total_chars'] - result['correct_chars']) / result['total_chars'] * 100) if result['total_chars'] > 0 else 0

        # WPM等级评估
        wpm_level = self.get_wpm_level(result['wpm'], result['language'])
        accuracy_level = self.get_accuracy_level(result['accuracy'])

        metrics_info = [
            f"⚡ 打字速度: {result['wpm']} WPM ({wpm_level})",
            f"🎯 准确率: {result['accuracy']}% ({accuracy_level})",
            f"📊 字符/秒: {chars_per_second:.1f} CPS",
            f"❌ 错误率: {error_rate:.1f}%",
            f"⏱️  平均字符用时: {elapsed_time/result['text_length']:.2f}秒" if result['text_length'] > 0 else "⏱️  平均字符用时: 0秒"
        ]

        for info in metrics_info:
            info_label = ctk.CTkLabel(
                metrics_frame,
                text=info,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            info_label.pack(pady=2, padx=20, fill="x")

        # 按钮区域
        button_frame = ctk.CTkFrame(report_window)
        button_frame.pack(pady=10, fill="x", padx=20)

        def continue_practice():
            report_window.destroy()
            self.select_random_text()

        continue_button = ctk.CTkButton(
            button_frame,
            text="🔄 继续练习",
            command=continue_practice,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120
        )
        continue_button.pack(side="left", padx=10, pady=10)

        close_button = ctk.CTkButton(
            button_frame,
            text="✅ 关闭",
            command=report_window.destroy,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120
        )
        close_button.pack(side="right", padx=10, pady=10)

    def get_wpm_level(self, wpm, language):
        """获取WPM等级评价"""
        if language == "chinese":
            if wpm >= 120: return "专家级"
            elif wpm >= 80: return "优秀"
            elif wpm >= 50: return "良好"
            elif wpm >= 30: return "一般"
            else: return "初学者"
        else:
            if wpm >= 80: return "专家级"
            elif wpm >= 60: return "优秀"
            elif wpm >= 40: return "良好"
            elif wpm >= 20: return "一般"
            else: return "初学者"

    def get_accuracy_level(self, accuracy):
        """获取准确率等级评价"""
        if accuracy >= 98: return "完美"
        elif accuracy >= 95: return "优秀"
        elif accuracy >= 90: return "良好"
        elif accuracy >= 85: return "一般"
        else: return "需要改进"

    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    # 检查依赖
    try:
        import customtkinter
    except ImportError:
        print("请先安装依赖库:")
        print("pip install -r requirements.txt")
        print("或者:")
        print("pip install customtkinter zhipuai requests")
        exit(1)

    # 创建并运行应用
    app = TypingSpeedTest()
    app.run()
