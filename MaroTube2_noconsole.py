import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import threading
import os
import re
import json

class YouTubeDLPAudioExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 برنامج تنزيل فيديوهات اليوتيوب المتطور")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.minsize(800, 650)
        
        # تدرج لوني للخلفية
        self.root.configure(bg="#1a1a2e")

        # إعداد الأنماط المحدثة
        self.setup_styles()
        
        # إنشاء الواجهة الرئيسية
        self.create_main_interface()
        
        # تخزين معلومات الفيديو مؤقتاً
        self.current_video_info = None
        self.format_map = {} 

        # التحقق من وجود ffmpeg عند بدء التطبيق
        self.root.after(100, self.check_ffmpeg_exists)

    def setup_styles(self):
        """إعداد الأنماط المحسنة للواجهة"""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # الألوان الأساسية
        self.colors = {
            'bg_primary': '#1a1a2e',
            'bg_secondary': '#16213e',
            'bg_tertiary': '#0f3460',
            'accent': '#e94560',
            'accent_hover': '#c73650',
            'text_primary': '#ffffff',
            'text_secondary': '#b8c5d6',
            'success': '#4ecdc4',
            'warning': '#ffe66d',
            'error': '#ff6b6b'
        }
        
        # إعداد أنماط الإطارات
        self.style.configure("Main.TFrame", 
                           background=self.colors['bg_primary'])
        
        self.style.configure("Card.TFrame", 
                           background=self.colors['bg_secondary'],
                           relief="flat",
                           borderwidth=1)
        
        # إعداد أنماط التسميات
        self.style.configure("Title.TLabel", 
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 20, "bold"))
        
        self.style.configure("Heading.TLabel", 
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 12, "bold"))
        
        self.style.configure("Info.TLabel", 
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_secondary'],
                           font=("Segoe UI", 10))
        
        self.style.configure("Status.TLabel", 
                           background=self.colors['bg_primary'],
                           foreground=self.colors['success'],
                           font=("Segoe UI", 10, "bold"))
        
        # إعداد أنماط الأزرار
        self.style.configure("Primary.TButton",
                           background=self.colors['accent'],
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 11, "bold"),
                           borderwidth=0,
                           focuscolor="none",
                           relief="flat")
        
        self.style.map("Primary.TButton",
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent_hover'])])
        
        self.style.configure("Secondary.TButton",
                           background=self.colors['bg_tertiary'],
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 10),
                           borderwidth=0,
                           focuscolor="none",
                           relief="flat")
        
        self.style.map("Secondary.TButton",
                      background=[('active', self.colors['bg_secondary'])])
        
        # إعداد أنماط حقول الإدخال
        self.style.configure("Modern.TEntry",
                           fieldbackground=self.colors['bg_tertiary'],
                           foreground=self.colors['text_primary'],
                           insertcolor=self.colors['text_primary'],
                           borderwidth=1,
                           relief="flat",
                           font=("Segoe UI", 11))
        
        self.style.configure("Modern.TCombobox",
                           fieldbackground=self.colors['bg_tertiary'],
                           foreground=self.colors['text_primary'],
                           selectbackground=self.colors['accent'],
                           selectforeground=self.colors['text_primary'],
                           borderwidth=1,
                           relief="flat",
                           font=("Segoe UI", 10))
        
        # إعداد شريط التقدم
        self.style.configure("Modern.Horizontal.TProgressbar",
                           troughcolor=self.colors['bg_tertiary'],
                           background=self.colors['success'],
                           borderwidth=0,
                           relief="flat")
        
        # إعداد خانات الاختيار
        self.style.configure("Modern.TCheckbutton",
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           font=("Segoe UI", 10),
                           focuscolor="none")
        
        # إعداد إطارات التسميات
        self.style.configure("Modern.TLabelframe",
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief="flat")
        
        self.style.configure("Modern.TLabelframe.Label",
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['accent'],
                           font=("Segoe UI", 11, "bold"))    
    def create_main_interface(self):
        """إنشاء الواجهة الرئيسية المحسنة"""
        # إطار خارجي للـ canvas
        outer_frame = ttk.Frame(self.root, style="Main.TFrame")
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # إنشاء Canvas وشريط التمرير
        self.canvas = tk.Canvas(outer_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=self.canvas.yview)
        
        # إطار رئيسي داخل الـ Canvas
        main_frame = ttk.Frame(self.canvas, padding="25 25 25 25", style="Main.TFrame")
        
        # تكوين الـ Canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # ترتيب العناصر
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # إضافة الإطار الرئيسي إلى الـ Canvas
        canvas_frame = self.canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # تكوين التمرير
        self.configure_scrolling(main_frame, canvas_frame)

        # العنوان الرئيسي مع أيقونة
        title_frame = ttk.Frame(main_frame, style="Main.TFrame")
        title_frame.pack(pady=(0, 25), fill=tk.X)
        
        title_label = ttk.Label(title_frame, 
                               text="🎬 برنامج تنزيل الفيديوهات المتطور", 
                               style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="قم بتنزيل فيديوهاتك المفضلة بأعلى جودة",
                                 font=("Segoe UI", 12),
                                 foreground=self.colors['text_secondary'],
                                 background=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))

        # قسم إدخال الرابط
        self.create_link_section(main_frame)
        
        # قسم معلومات الفيديو
        self.create_info_section(main_frame)
        
        # قسم خيارات التنزيل
        self.create_options_section(main_frame)
        
        # قسم مسار الحفظ
        self.create_path_section(main_frame)
        
        # زر التنزيل الرئيسي
        self.create_download_section(main_frame)
        
        # قسم التقدم والحالة
        self.create_progress_section(main_frame)
        
        # قسم المخرجات
        self.create_output_section(main_frame)

    def create_link_section(self, parent):
        """إنشاء قسم إدخال الرابط"""
        link_card = ttk.Frame(parent, style="Card.TFrame", padding="20 15 20 15")
        link_card.pack(pady=(0, 15), fill=tk.X)

        ttk.Label(link_card, text="🔗 رابط الفيديو أو قائمة التشغيل", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        link_input_frame = ttk.Frame(link_card, style="Card.TFrame")
        link_input_frame.pack(fill=tk.X)
        
        self.link_entry = ttk.Entry(link_input_frame, 
                                   font=("Segoe UI", 11),
                                   style="Modern.TEntry")
        self.link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # قائمة السياق للرابط
        self.setup_context_menu()

        self.fetch_button = ttk.Button(link_input_frame, 
                                     text="📥 جلب المعلومات", 
                                     command=self.fetch_info_thread,
                                     style="Secondary.TButton")
        self.fetch_button.pack(side=tk.LEFT)

    def create_info_section(self, parent):
        """إنشاء قسم معلومات الفيديو"""
        self.info_card = ttk.LabelFrame(parent, 
                                       text="📋 معلومات الفيديو", 
                                       style="Modern.TLabelframe", 
                                       padding="15 10 15 15")
        self.info_card.pack(pady=(0, 15), fill=tk.X)

        self.title_label = ttk.Label(self.info_card, 
                                   text="العنوان: في انتظار الرابط...", 
                                   style="Info.TLabel")
        self.title_label.pack(anchor=tk.W, pady=2)

        self.author_label = ttk.Label(self.info_card, 
                                    text="الناشر: --", 
                                    style="Info.TLabel")
        self.author_label.pack(anchor=tk.W, pady=2)

        self.duration_label = ttk.Label(self.info_card, 
                                      text="المدة: --", 
                                      style="Info.TLabel")
        self.duration_label.pack(anchor=tk.W, pady=2)

    def create_options_section(self, parent):
        """إنشاء قسم خيارات التنزيل"""
        options_card = ttk.LabelFrame(parent, 
                                    text="⚙️ خيارات التنزيل", 
                                    style="Modern.TLabelframe", 
                                    padding="15 10 15 15")
        options_card.pack(pady=(0, 15), fill=tk.X)

        # اختيار الجودة
        quality_frame = ttk.Frame(options_card, style="Card.TFrame")
        quality_frame.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(quality_frame, text="🎥 اختر الجودة:", 
                 style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.quality_combobox = ttk.Combobox(quality_frame, 
                                           state="readonly", 
                                           width=40,
                                           style="Modern.TCombobox",
                                           font=("Segoe UI", 10))
        self.quality_combobox.pack(anchor=tk.W)
        self.quality_combobox['values'] = ["جلب المعلومات أولاً..."]
        self.quality_combobox.set("جلب المعلومات أولاً...")
        self.quality_combobox.bind("<<ComboboxSelected>>", self.update_quality_selection)

        # الخيارات
        options_frame = ttk.Frame(options_card, style="Card.TFrame")
        options_frame.pack(fill=tk.X)

        self.extract_audio_var = tk.BooleanVar(value=False)
        self.extract_audio_checkbox = ttk.Checkbutton(options_frame, 
                                                    text="🎵 استخراج الصوت فقط (MP3)", 
                                                    variable=self.extract_audio_var, 
                                                    command=self.toggle_audio_extraction,
                                                    style="Modern.TCheckbutton")
        self.extract_audio_checkbox.pack(anchor=tk.W, pady=5)

        self.download_playlist_var = tk.BooleanVar(value=False)
        self.download_playlist_checkbox = ttk.Checkbutton(options_frame, 
                                                        text="📋 تنزيل قائمة التشغيل كاملة", 
                                                        variable=self.download_playlist_var,
                                                        style="Modern.TCheckbutton")
        self.download_playlist_checkbox.pack(anchor=tk.W, pady=5)

    def create_path_section(self, parent):
        """إنشاء قسم مسار الحفظ"""
        path_card = ttk.Frame(parent, style="Card.TFrame", padding="20 15 20 15")
        path_card.pack(pady=(0, 15), fill=tk.X)

        ttk.Label(path_card, text="📁 مسار الحفظ", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))

        path_input_frame = ttk.Frame(path_card, style="Card.TFrame")
        path_input_frame.pack(fill=tk.X)

        self.path_entry = ttk.Entry(path_input_frame, 
                                   font=("Segoe UI", 11),
                                   style="Modern.TEntry")
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # تعيين مجلد التنزيلات الافتراضي
        self.default_download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.default_download_path):
            self.default_download_path = os.path.expanduser("~")
        self.path_entry.insert(0, self.default_download_path)

        self.browse_button = ttk.Button(path_input_frame, 
                                      text="📂 تصفح", 
                                      command=self.browse_path,
                                      style="Secondary.TButton")
        self.browse_button.pack(side=tk.LEFT)

    def create_download_section(self, parent):
        """إنشاء قسم زر التنزيل"""
        download_frame = ttk.Frame(parent, style="Main.TFrame")
        download_frame.pack(pady=20)

        self.download_button = ttk.Button(download_frame, 
                                        text="⬇️ بدء التنزيل", 
                                        command=self.start_download_thread, 
                                        state=tk.DISABLED,
                                        style="Primary.TButton")
        self.download_button.pack()

    def create_progress_section(self, parent):
        """إنشاء قسم التقدم والحالة"""
        progress_card = ttk.Frame(parent, style="Card.TFrame", padding="20 15 20 15")
        progress_card.pack(pady=(0, 15), fill=tk.X)

        self.progress_bar = ttk.Progressbar(progress_card, 
                                          orient="horizontal", 
                                          length=400, 
                                          mode="determinate", 
                                          style="Modern.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=(0, 10), fill=tk.X)

        self.status_label = ttk.Label(progress_card, 
                                    text="📊 الحالة: في انتظار الرابط...", 
                                    style="Status.TLabel")
        self.status_label.pack()

    def create_output_section(self, parent):
        """إنشاء قسم المخرجات"""
        output_card = ttk.Frame(parent, style="Card.TFrame", padding="15 10 15 15")
        output_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(output_card, text="📝 مخرجات التطبيق", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))

        # إطار النص مع شريط التمرير
        text_frame = ttk.Frame(output_card, style="Card.TFrame")
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(text_frame, 
                                 height=8, 
                                 wrap="word", 
                                 bg=self.colors['bg_tertiary'], 
                                 fg=self.colors['text_primary'], 
                                 font=("Consolas", 9), 
                                 relief="flat",
                                 borderwidth=0,
                                 insertbackground=self.colors['text_primary'])
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_text.insert(tk.END, "مرحباً! ابدأ بإدخال رابط الفيديو وجلب المعلومات.\n")
        self.output_text.config(state=tk.DISABLED)

    def setup_context_menu(self):
        """إعداد قائمة السياق لحقل الرابط"""
        self.context_menu = tk.Menu(self.root, tearoff=0, 
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_primary'],
                                  activebackground=self.colors['accent'],
                                  activeforeground=self.colors['text_primary'])
        self.context_menu.add_command(label="قص", command=lambda: self.link_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="نسخ", command=lambda: self.link_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="لصق", command=lambda: self.link_entry.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="مسح الكل", command=lambda: self.link_entry.delete(0, tk.END))
        self.link_entry.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def browse_path(self):
        download_path = filedialog.askdirectory(initialdir=self.default_download_path)
        if download_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, download_path)

    def toggle_audio_extraction(self):
        """تبديل حالة قائمة الجودة حسب خيار استخراج الصوت"""
        if self.extract_audio_var.get():
            self.quality_combobox.config(state=tk.DISABLED)
            self.quality_combobox.set("🎵 استخراج الصوت فقط (MP3)")
        else:
            self.quality_combobox.config(state="readonly")
            if self.quality_combobox.get() == "🎵 استخراج الصوت فقط (MP3)":
                if "bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)" in self.quality_combobox['values']:
                    self.quality_combobox.set("bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)")
                elif self.quality_combobox['values']:
                    self.quality_combobox.set(self.quality_combobox['values'][0])
                else:
                    self.quality_combobox.set("")

    def update_quality_selection(self, event=None):
        """تحديث خيار استخراج الصوت حسب اختيار الجودة"""
        selected_display_format = self.quality_combobox.get()
        if selected_display_format == "🎵 استخراج الصوت فقط (MP3)":
            self.extract_audio_var.set(True)
        else:
            self.extract_audio_var.set(False)
        self.toggle_audio_extraction()
        
    def check_ffmpeg_exists(self):
        """التحقق من وجود ffmpeg"""
        try:
            ffmpeg_path = r"C:\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
            
            if os.path.exists(ffmpeg_path):
                process = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, encoding='latin-1', errors='replace', timeout=5)
            else:
                process = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, encoding='latin-1', errors='replace', timeout=5)
            
            if process.returncode == 0:
                self.log_output("✅ ffmpeg موجود ومتاح للاستخدام.")
                return True
            else:
                self.log_output("❌ خطأ: ffmpeg غير موجود أو غير قابل للتشغيل.")
                messagebox.showwarning("تحذير", "ffmpeg غير موجود أو غير قابل للتشغيل.\nقم بتنزيله من https://ffmpeg.org/download.html")
                return False
        except FileNotFoundError:
            self.log_output("❌ خطأ: ffmpeg غير موجود في المسار.")
            messagebox.showwarning("تحذير", "ffmpeg غير موجود.\nقم بتنزيله من https://ffmpeg.org/download.html")
            return False
        except subprocess.TimeoutExpired:
            self.log_output("⏰ خطأ: استغرق التحقق من ffmpeg وقتاً طويلاً.")
            return False
        except Exception as e:
            self.log_output(f"❌ خطأ غير متوقع أثناء التحقق من ffmpeg: {e}")
            return False

    def fetch_info_thread(self):
        threading.Thread(target=self._fetch_video_info, daemon=True).start()

    def _fetch_video_info(self):
        url = self.link_entry.get().strip()
        if not url:
            messagebox.showwarning("تنبيه", "الرجاء إدخال رابط الفيديو أو قائمة التشغيل.")
            return

        self.root.after(0, lambda: self.status_label.config(text="📡 جاري جلب المعلومات..."))
        self.root.after(0, lambda: self.set_ui_state(False))
        self.root.after(0, lambda: self.quality_combobox.set("⏳ جلب المعلومات..."))

        try:
            command = ["yt-dlp", "--dump-json", url]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin-1', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.log_output(f"❌ خطأ في جلب المعلومات:\n{stderr}")
                messagebox.showerror("خطأ", f"حدث خطأ أثناء جلب المعلومات: {stderr}")
                self.root.after(0, self.reset_ui_after_fetch)
                return

            info = json.loads(stdout)
            self.current_video_info = info
            self.format_map = {}

            # تحديث معلومات الفيديو
            if 'entries' in info and len(info['entries']) > 0:
                self.root.after(0, lambda: self.title_label.config(text=f"📋 العنوان: {info.get('title', 'غير متاح')} (قائمة تشغيل)"))
                self.root.after(0, lambda: self.author_label.config(text=f"👤 الناشر: {info.get('uploader', 'غير متاح')}"))
                self.root.after(0, lambda: self.duration_label.config(text=f"📊 عدد الفيديوهات: {len(info['entries'])}"))
                self.root.after(0, lambda: self.download_playlist_var.set(True))
            else:
                self.root.after(0, lambda: self.title_label.config(text=f"🎬 العنوان: {info.get('title', 'غير متاح')}"))
                self.root.after(0, lambda: self.author_label.config(text=f"👤 الناشر: {info.get('uploader', 'غير متاح')}"))
                self.root.after(0, lambda: self.duration_label.config(text=f"⏱️ المدة: {self.format_duration(info.get('duration'))}"))
                self.root.after(0, lambda: self.download_playlist_var.set(False))

            # تحديث قائمة الجودة
            available_formats_for_display = []
            
            available_formats_for_display.append("🎥 bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)")
            self.format_map["🎥 bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)"] = "bestvideo+bestaudio/best"
            
            available_formats_for_display.append("🎵 استخراج الصوت فقط (MP3)")
            self.format_map["🎵 استخراج الصوت فقط (MP3)"] = "bestaudio"

            # إضافة الجودات المتاحة
            combined_formats = []
            for fmt in info.get('formats', []):
                if fmt.get('height') and 144 <= fmt['height'] <= 1080 and \
                   fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    
                    display_string = f"🎥 {fmt['height']}p {fmt.get('ext', 'N/A')} ({self.format_size(fmt.get('filesize') or fmt.get('filesize_approx'))})"
                    yt_dlp_format_string = fmt.get('format_id')
                    combined_formats.append((fmt['height'], display_string, yt_dlp_format_string))

            combined_formats.sort(key=lambda x: x[0], reverse=True)

            for height, display_str, yt_dlp_fmt_str in combined_formats:
                if display_str not in available_formats_for_display:
                    available_formats_for_display.append(display_str)
                    self.format_map[display_str] = yt_dlp_fmt_str

            def update_ui():
                self.quality_combobox['values'] = available_formats_for_display
                if available_formats_for_display:
                    if "🎥 bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)" in available_formats_for_display:
                        self.quality_combobox.set("🎥 bestvideo+bestaudio/best (أفضل جودة فيديو وصوت)")
                    else:
                        self.quality_combobox.set(available_formats_for_display[0])
                else:
                    self.quality_combobox.set("❌ لا توجد جودات متاحة")
                    self.download_button.config(state=tk.DISABLED)

                self.status_label.config(text="✅ جاهز للتنزيل!")
                self.download_button.config(state=tk.NORMAL)
                self.set_ui_state(True)

            self.root.after(0, update_ui)            
            self.log_output("✅ تم جلب المعلومات بنجاح!")

        except json.JSONDecodeError as e:
            self.log_output(f"❌ خطأ في تحليل JSON: {e}")
            messagebox.showerror("خطأ", f"حدث خطأ في تحليل بيانات yt-dlp: {e}")
            self.root.after(0, self.reset_ui_after_fetch)
        except FileNotFoundError:
            messagebox.showerror("خطأ", "لم يتم العثور على برنامج 'yt-dlp'. يرجى تثبيته أولاً.")
            self.root.after(0, self.reset_ui_after_fetch)
        except Exception as e:
            self.log_output(f"❌ خطأ غير متوقع: {e}")
            messagebox.showerror("خطأ", f"حدث خطأ غير متوقع: {e}")
            self.root.after(0, self.reset_ui_after_fetch)

    def format_size(self, size):
        """تنسيق حجم الملف"""
        if not size:
            return "غير معروف"
        for unit in ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} تيرابايت"

    def reset_ui_after_fetch(self):
        """إعادة تعيين واجهة المستخدم بعد جلب المعلومات"""
        self.set_ui_state(True)
        self.status_label.config(text="❌ حدث خطأ في جلب المعلومات.")
        self.download_button.config(state=tk.DISABLED)
        self.quality_combobox.set("جلب المعلومات أولاً...")

    def set_ui_state(self, enabled):
        """تحديث حالة عناصر الواجهة"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.link_entry.config(state=state)
        self.fetch_button.config(state=state)
        if enabled and not self.extract_audio_var.get():
            self.quality_combobox.config(state="readonly")
        else:
            self.quality_combobox.config(state=tk.DISABLED)
        self.extract_audio_checkbox.config(state=state)
        self.download_playlist_checkbox.config(state=state)
        self.path_entry.config(state=state)
        self.browse_button.config(state=state)

    def start_download_thread(self):
        """بدء عملية التنزيل في خيط منفصل"""
        download_path = self.path_entry.get().strip()
        if not download_path:
            messagebox.showwarning("تنبيه", "الرجاء تحديد مسار الحفظ.")
            return

        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except OSError as e:
                messagebox.showerror("خطأ", f"تعذر إنشاء مجلد الحفظ: {e}")
                return

        if not self.check_ffmpeg_exists():
            messagebox.showwarning("تحذير", "لا يمكن بدء التنزيل. ffmpeg غير موجود. يرجى تثبيته أولاً.")
            return

        self.set_ui_state(False)
        self.download_button.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.status_label.config(text="🚀 جاري بدء التنزيل...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "🔰 بدء عملية التنزيل...\n")
        self.output_text.config(state=tk.DISABLED)

        threading.Thread(target=self._download_video, daemon=True).start()

    def _download_video(self):
        """تنفيذ عملية التنزيل"""
        url = self.link_entry.get().strip()
        download_path = self.path_entry.get().strip()
        selected_quality = self.quality_combobox.get()
        format_code = self.format_map.get(selected_quality, "bestvideo+bestaudio/best")
        extract_audio = self.extract_audio_var.get()
        download_playlist = self.download_playlist_var.get()

        ffmpeg_path = r"C:\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
        command = ["yt-dlp", url, "-P", download_path, "--ffmpeg-location", ffmpeg_path]

        if extract_audio:
            command.extend(["-x", "--audio-format", "mp3"])
        else:
            command.extend(["-f", format_code])

        if 'playlist' in url.lower() and not download_playlist:
            command.append("--no-playlist")

        command.extend([
            "--progress",
            "--newline",
            "--no-warnings",
            "--no-simulate",
            "--no-check-certificates"
        ])

        self.log_output(f"⚙️ جاري التنفيذ: {' '.join(command)}\n")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='latin-1',
                errors='replace'
            , creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            for line in process.stdout:
                self.log_output(line.strip())
                
                # تحديث شريط التقدم
                progress_match = re.search(r'\[download\]\s+(\d+\.\d+)%\s+of\s+.*', line)
                if progress_match:
                    percentage = float(progress_match.group(1))
                    self.root.after(0, lambda p=percentage: self.update_progress(p))
                elif "[ExtractAudio]" in line:
                    self.root.after(0, lambda: self.status_label.config(text="🎵 جاري استخراج الصوت..."))
                elif "[Merger]" in line:
                    self.root.after(0, lambda: self.status_label.config(text="🔄 جاري دمج الصوت والفيديو..."))

            process.wait()

            if process.returncode == 0:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"✅ تم التنزيل بنجاح! المسار: {download_path}"
                ))
                messagebox.showinfo("نجاح", "✅ تم التنزيل بنجاح!")
            else:
                error_message = "❌ فشل التنزيل. يرجى التحقق من الرابط ومراجعة السجل."
                self.root.after(0, lambda: self.status_label.config(text=error_message))
                messagebox.showerror("خطأ", error_message)

        except FileNotFoundError:
            self.root.after(0, lambda: messagebox.showerror(
                "خطأ",
                "❌ لم يتم العثور على برنامج 'yt-dlp'. يرجى تثبيته أولاً."
            ))
            self.root.after(0, lambda: self.status_label.config(text="❌ خطأ في برنامج التنزيل."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("خطأ", f"❌ حدث خطأ غير متوقع: {e}"))
            self.root.after(0, lambda: self.status_label.config(text=f"❌ خطأ: {e}"))
        finally:
            self.root.after(0, self.reset_ui_after_download)

    def update_progress(self, percentage):
        """تحديث شريط التقدم والحالة"""
        self.progress_bar["value"] = percentage
        self.status_label.config(text=f"⏳ جاري التنزيل... {percentage:.1f}%")

    def reset_ui_after_download(self):
        """إعادة تعيين واجهة المستخدم بعد التنزيل"""
        self.set_ui_state(True)
        self.download_button.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0

    def format_duration(self, seconds):
        """تنسيق مدة الفيديو"""
        if seconds is None:
            return "غير متاح"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"

    def log_output(self, text):
        """تسجيل المخرجات في مربع النص"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def configure_scrolling(self, main_frame, canvas_frame):
        """تكوين سلوك التمرير للواجهة"""
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def configure_canvas_frame(event):
            self.canvas.itemconfig(canvas_frame, width=event.width)
        
        main_frame.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", configure_canvas_frame)
        
        # تمكين التمرير بعجلة الماوس
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDLPAudioExtractor(root)
    root.mainloop()