"""
Focus Tracker - Odaklanma Asistanı
Webcam üzerinden bakış yönü tespiti yapan masaüstü uygulaması.
Cross-platform destek: Windows, macOS, Linux
"""

import tkinter as tk
from tkinter import ttk, font
import cv2
from PIL import Image, ImageTk
import threading
import time
from datetime import timedelta

from gaze_detector import GazeDetector
from alert_manager import AlertManager
from config import (
    TIME_OPTIONS, 
    DISTRACTION_THRESHOLD, 
    FRAME_SKIP, 
    TARGET_FPS,
    WEBCAM_WIDTH,
    WEBCAM_HEIGHT,
    WINDOW_SIZE,
    MIN_WINDOW_SIZE,
    WINDOW_TITLE,
    ALERT_COOLDOWN,
    GAZE_SENSITIVITY
)


class FocusTrackerApp:
    """
    Odaklanma Asistanı ana uygulama sınıfı.
    Thread-safe ve cross-platform.
    """
    
    def __init__(self):
        """Uygulamayı başlat."""
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.root.resizable(True, True)
        self.root.configure(bg="#1a1a2e")
        
        self.root.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        self.gaze_detector = None
        self.alert_manager = AlertManager(cooldown_seconds=ALERT_COOLDOWN)
        self.cap = None
        
        self.is_running = False
        self.remaining_seconds = 0
        self.selected_duration = tk.StringVar(value="10 Dakika")
        
        self.video_thread = None
        self.timer_thread = None
        self.stop_event = threading.Event()
        self._state_lock = threading.Lock()
        
        self.warning_visible = False
        self.consecutive_distraction_frames = 0
        self.distraction_threshold = DISTRACTION_THRESHOLD
        
        self.frame_counter = 0
        self.frame_skip = FRAME_SKIP
        
        self.title_font = font.Font(family="Segoe UI", size=28, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=14)
        self.warning_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.timer_font = font.Font(family="Consolas", size=20, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=12, weight="bold")
        
        self.create_start_screen()
        
    def create_start_screen(self):
        """Başlangıç ekranını oluştur."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg="#F5CDB5")
        main_frame.pack(expand=True, fill="both")
        
        content_frame = tk.Frame(main_frame, bg="#F5CDB5")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = tk.Label(
            content_frame,
            text="ODAK YARDIMCISI",
            font=("Segoe UI", 42, "bold"),
            fg="#4A4A68",
            bg="#F5CDB5"
        )
        title_label.pack(pady=(0, 60))
        
        time_label = tk.Label(
            content_frame,
            text="Süre Seçiniz:",
            font=("Segoe UI", 16),
            fg="#8B8B9E",
            bg="#F5CDB5"
        )
        time_label.pack(pady=(0, 15))
        
        dropdown_canvas = tk.Canvas(
            content_frame,
            width=450,
            height=60,
            bg="#F5CDB5",
            highlightthickness=0
        )
        dropdown_canvas.pack(pady=(0, 40))
        
        dropdown_canvas.create_oval(0, 0, 60, 60, fill="#FFFFFF", outline="")
        dropdown_canvas.create_oval(390, 0, 450, 60, fill="#FFFFFF", outline="")
        dropdown_canvas.create_rectangle(30, 0, 420, 60, fill="#FFFFFF", outline="")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.TCombobox",
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground="#4A4A68",
            borderwidth=0,
            relief="flat",
            arrowcolor="#9C8AA5",
            padding=10
        )
        style.map('Custom.TCombobox',
                  fieldbackground=[('readonly', '#FFFFFF')],
                  selectbackground=[('readonly', '#FFFFFF')],
                  selectforeground=[('readonly', '#4A4A68')])
        
        time_dropdown = ttk.Combobox(
            dropdown_canvas,
            textvariable=self.selected_duration,
            values=list(TIME_OPTIONS.keys()),
            state="readonly",
            font=("Segoe UI", 14),
            width=28,
            style="Custom.TCombobox"
        )
        dropdown_canvas.create_window(225, 30, window=time_dropdown)
        
        button_canvas = tk.Canvas(
            content_frame,
            width=350,
            height=70,
            bg="#F5CDB5",
            highlightthickness=0
        )
        button_canvas.pack(pady=(0, 50))
        
        button_oval = button_canvas.create_oval(
            0, 0, 350, 70,
            fill="#9C8AA5",
            outline=""
        )
        
        button_text = button_canvas.create_text(
            175, 35,
            text="Başlat",
            font=("Segoe UI", 18),
            fill="#FFFFFF"
        )
        
        def on_enter(e):
            button_canvas.itemconfig(button_oval, fill="#8A7893")
        
        def on_leave(e):
            button_canvas.itemconfig(button_oval, fill="#9C8AA5")
        
        def on_click(e):
            self.start_focus_session()
        
        button_canvas.bind("<Enter>", on_enter)
        button_canvas.bind("<Leave>", on_leave)
        button_canvas.bind("<Button-1>", on_click)
        button_canvas.config(cursor="hand2")
        
        info_label = tk.Label(
            content_frame,
            text="Bu uygulama, webcam aracılığı ile seçtiğiniz süre boyunca odağınızı ekranda tutmaya yardımcı olur.",
            font=("Segoe UI", 10),
            fg="#8B8B9E",
            bg="#F5CDB5",
            wraplength=600,
            justify="center"
        )
        info_label.pack(pady=10)
    
    
    def create_focus_screen(self):
        """Odaklanma ekranını oluştur."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg="#FAE5D8")
        main_frame.pack(expand=True, fill="both")
        
        top_bar = tk.Frame(main_frame, bg="#B8A7BE", height=60)
        top_bar.pack(fill="x", pady=(0, 10))
        top_bar.pack_propagate(False)
        
        self.timer_label = tk.Label(
            top_bar,
            text="00:00:00",
            font=("Consolas", 20, "bold"),
            fg="#FFFFFF",
            bg="#B8A7BE"
        )
        self.timer_label.pack(expand=True)
        
        bottom_bar = tk.Frame(main_frame, bg="#FAE5D8", height=70)
        bottom_bar.pack(fill="x", side="bottom", pady=10)
        bottom_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            bottom_bar,
            text="Odaklanıyorsunuz...",
            font=("Segoe UI", 14),
            fg="#5A8F5A",
            bg="#FAE5D8"
        )
        self.status_label.pack(side="left", padx=20)
        
        stop_canvas = tk.Canvas(
            bottom_bar,
            width=160,
            height=50,
            bg="#FAE5D8",
            highlightthickness=0
        )
        stop_canvas.pack(side="right", padx=20)
        
        stop_oval = stop_canvas.create_oval(
            0, 0, 160, 50,
            fill="#9C8AA5",
            outline=""
        )
        
        stop_text = stop_canvas.create_text(
            80, 25,
            text="BİTİR",
            font=("Segoe UI", 14, "bold"),
            fill="#FFFFFF"
        )
        
        def on_enter(e):
            stop_canvas.itemconfig(stop_oval, fill="#8A7893")
        
        def on_leave(e):
            stop_canvas.itemconfig(stop_oval, fill="#9C8AA5")
        
        def on_click(e):
            self.stop_focus_session()
        
        stop_canvas.bind("<Enter>", on_enter)
        stop_canvas.bind("<Leave>", on_leave)
        stop_canvas.bind("<Button-1>", on_click)
        stop_canvas.config(cursor="hand2")
        
        video_container = tk.Frame(main_frame, bg="#E8D5C8", padx=3, pady=3)
        video_container.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.video_label = tk.Label(video_container, bg="#000000")
        self.video_label.pack(expand=True, fill="both")
        
        self.warning_frame = tk.Frame(main_frame, bg="#E57373")
        
        self.warning_label = tk.Label(
            self.warning_frame,
            text="! EKRANA ODAKLANINIZ !",
            font=("Segoe UI", 24, "bold"),
            fg="#FFFFFF",
            bg="#E57373",
            padx=30,
            pady=15
        )
        self.warning_label.pack()
    
    def start_focus_session(self):
        """Odaklanma oturumunu başlat."""
        duration_label = self.selected_duration.get()
        duration_minutes = TIME_OPTIONS[duration_label]
        self.remaining_seconds = duration_minutes * 60
        
        self.gaze_detector = GazeDetector(sensitivity=GAZE_SENSITIVITY)
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("Webcam açılamadı! Lütfen webcam bağlantınızı kontrol edin.")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)
        
        with self._state_lock:
            self.is_running = True
            self.stop_event.clear()
            self.consecutive_distraction_frames = 0
            self.warning_visible = False
            self.frame_counter = 0
        
        self.create_focus_screen()
        
        threading.Thread(target=self.alert_manager.play_start_sound, daemon=True).start()
        
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
    
    def video_loop(self):
        """Video işleme döngüsü (ayrı thread'de çalışır)."""
        last_processed_frame = None
        last_is_looking = True
        last_direction = "merkez"
        
        while self.is_running and not self.stop_event.is_set():
            if self.cap is None or not self.cap.isOpened():
                break
            
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            with self._state_lock:
                self.frame_counter += 1
                should_process = (self.frame_counter % self.frame_skip == 0)
            
            if should_process:
                processed_frame, is_looking, direction = self.gaze_detector.process_frame(frame)
                last_processed_frame = processed_frame
                last_is_looking = is_looking
                last_direction = direction
                
                with self._state_lock:
                    if not is_looking:
                        self.consecutive_distraction_frames += 1
                        
                        if self.consecutive_distraction_frames >= self.distraction_threshold:
                            if not self.warning_visible:
                                    print(f"[UYARI] Eşik aşıldı! Uyarı tetikleniyor...")
                                    self.root.after(0, self.show_warning)
                                    threading.Thread(target=self.alert_manager.trigger_alert, daemon=True).start()
                    else:
                        if self.consecutive_distraction_frames > 0:
                            print(f"[DEBUG] Odaklanma geri döndü.")
                        self.consecutive_distraction_frames = 0
                        if self.warning_visible:
                            self.root.after(0, self.hide_warning)
            else:
                if last_processed_frame is not None:
                    processed_frame = last_processed_frame
                else:
                    processed_frame = frame
            
            try:
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                if hasattr(self, 'video_label') and self.video_label.winfo_exists():
                    label_width = self.video_label.winfo_width()
                    label_height = self.video_label.winfo_height()
                    
                    if label_width > 1 and label_height > 1:
                        img_ratio = img.width / img.height
                        label_ratio = label_width / label_height
                        
                        if img_ratio > label_ratio:
                            new_width = label_width
                            new_height = int(label_width / img_ratio)
                        else:
                            new_height = label_height
                            new_width = int(label_height * img_ratio)
                        
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    self.root.after(0, lambda: self.update_video_label(imgtk))
            except Exception as e:
                pass
            
            time.sleep(1.0 / TARGET_FPS)
    
    def update_video_label(self, imgtk):
        """Video label'ı güncelle (ana thread'de)."""
        try:
            if hasattr(self, 'video_label') and self.video_label.winfo_exists():
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        except tk.TclError:
            pass
    
    def timer_loop(self):
        """Zamanlayıcı döngüsü (ayrı thread'de çalışır)."""
        while self.is_running and self.remaining_seconds > 0 and not self.stop_event.is_set():
            time_str = str(timedelta(seconds=self.remaining_seconds))
            
            if len(time_str.split(':')) == 2:
                time_str = "0:" + time_str
            
            self.root.after(0, lambda t=time_str: self.update_timer_label(t))
            
            time.sleep(1)
            with self._state_lock:
                self.remaining_seconds -= 1
        
        with self._state_lock:
            if self.remaining_seconds <= 0 and self.is_running:
                self.root.after(0, self.session_complete)
    
    def update_timer_label(self, time_str):
        """Timer label'ı güncelle (ana thread'de)."""
        try:
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.configure(text=time_str)
        except tk.TclError:
            pass
    
    def show_warning(self):
    """Uyarı mesajını göster (ana thread'de çağrılmalı)."""
    self.warning_visible = True
        try:
            if hasattr(self, 'warning_frame') and self.warning_frame.winfo_exists():
                self.warning_frame.place(relx=0.5, rely=0.5, anchor="center")
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.configure(text="Dikkat dağıldı!", fg="#D84545")
        except tk.TclError:
            pass

    def hide_warning(self):
    """Uyarı mesajını gizle (ana thread'de çağrılmalı)."""
        self.warning_visible = False
        threading.Thread(target=self.alert_manager.stop_alert, daemon=True).start()
        try:
            if hasattr(self, 'warning_frame') and self.warning_frame.winfo_exists():
                self.warning_frame.place_forget()
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.configure(text="Odaklanıyorsunuz...", fg="#5A8F5A")
        except tk.TclError:
            pass
        
    def stop_focus_session(self):
        """Odaklanma oturumunu durdur."""
        with self._state_lock:
            self.is_running = False
            self.stop_event.set()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        if self.gaze_detector is not None:
            self.gaze_detector.release()
            self.gaze_detector = None
        
        threading.Thread(target=self.alert_manager.play_end_sound, daemon=True).start()
        
        self.root.after(500, self.create_start_screen)
    
    def session_complete(self):
        """Oturum tamamlandığında çalışır."""
        with self._state_lock:
            self.is_running = False
            self.stop_event.set()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        if self.gaze_detector is not None:
            self.gaze_detector.release()
            self.gaze_detector = None
        
        threading.Thread(
            target=self.alert_manager.play_complete_sound, 
            daemon=True
        ).start()
        
        self.show_completion_screen()
    
    def show_completion_screen(self):
        """Tamamlanma ekranını göster."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg="#F5CDB5")
        main_frame.pack(expand=True, fill="both")
        
        content_frame = tk.Frame(main_frame, bg="#F5CDB5")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        congrats_label = tk.Label(
            content_frame,
            text="TEBRİKLER!",
            font=("Segoe UI", 36, "bold"),
            fg="#5A8F5A",
            bg="#F5CDB5"
        )
        congrats_label.pack(pady=(0, 20))
        
        message_label = tk.Label(
            content_frame,
            text="Odaklanma oturumunu başarıyla tamamladınız!",
            font=("Segoe UI", 16),
            fg="#4A4A68",
            bg="#F5CDB5"
        )
        message_label.pack(pady=(0, 40))
        
        button_canvas = tk.Canvas(
            content_frame,
            width=350,
            height=70,
            bg="#F5CDB5",
            highlightthickness=0
        )
        button_canvas.pack()
        
        button_oval = button_canvas.create_oval(
            0, 0, 350, 70,
            fill="#9C8AA5",
            outline=""
        )
        
        button_text = button_canvas.create_text(
            175, 35,
            text="YENİDEN BAŞLA",
            font=("Segoe UI", 18),
            fill="#FFFFFF"
        )
        
        def on_enter(e):
            button_canvas.itemconfig(button_oval, fill="#8A7893")
        
        def on_leave(e):
            button_canvas.itemconfig(button_oval, fill="#9C8AA5")
        
        def on_click(e):
            self.create_start_screen()
        
        button_canvas.bind("<Enter>", on_enter)
        button_canvas.bind("<Leave>", on_leave)
        button_canvas.bind("<Button-1>", on_click)
        button_canvas.config(cursor="hand2")
    
    
    def show_error(self, message: str):
        """Hata mesajı göster."""
        from tkinter import messagebox
        messagebox.showerror("Hata", message)
    
    def on_closing(self):
        """Pencere kapatılırken çalışır."""
        with self._state_lock:
            self.is_running = False
            self.stop_event.set()
        
        if self.cap is not None:
            self.cap.release()
        
        if self.gaze_detector is not None:
            self.gaze_detector.release()
        
        self.root.destroy()
    
    def run(self):
        """Uygulamayı çalıştır."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    app = FocusTrackerApp()
    app.run()
