import tkinter as tk
from tkinter import messagebox
import time
from plyer import notification
import pygame
import sys
import os

def resource_path(relative_path):
    return os.path.join(os.path.dirname(sys.executable), relative_path)

def notify(title, message, sound_file=None):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        print("通知エラー:", e)

    if sound_file:
        try:
            pygame.mixer.music.load(resource_path(sound_file))
            pygame.mixer.music.play()
        except Exception as e:
            print("音再生エラー:", e)

pygame.init()
pygame.mixer.quit()
pygame.mixer.init()

class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("ポモドーロタイマー")

        tk.Label(master, text="作業時間（分）:").pack()
        self.work_entry = tk.Entry(master)
        self.work_entry.insert(0, "25")
        self.work_entry.pack()

        tk.Label(master, text="休憩時間（分）:").pack()
        self.break_entry = tk.Entry(master)
        self.break_entry.insert(0, "5")
        self.break_entry.pack()

        self.start_button = tk.Button(master, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.pause_button = tk.Button(master, text="一時停止 / 再開", command=self.toggle_pause)
        self.pause_button.pack(pady=5)

        self.reset_button = tk.Button(master, text="リセット", command=self.reset_timer)
        self.reset_button.pack(pady=5)

        self.status_label = tk.Label(master, text="待機中")
        self.status_label.pack()

        self.timer_label = tk.Label(master, text="00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=10)

        self.running = False
        self.paused = False
        self.current_cycle = 0
        self.start_time = None
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.phase = "work"  # "work" or "break"

    def start_timer(self):
        if self.running:
            return
        try:
            self.work_min = int(self.work_entry.get())
            self.break_min = int(self.break_entry.get())
        except ValueError:
            messagebox.showerror("入力エラー", "数字を入力してください")
            return

        self.current_cycle = 1
        self.running = True
        self.paused = False
        self.phase = "work"
        self.start_phase()

    def start_phase(self):
        if self.current_cycle > 4:
            self.status_label.config(text="すべて完了！")
            notify("ポモドーロ完了", "お疲れさまでした！", "finish.wav")
            self.running = False
            return

        if self.phase == "work":
            self.status_label.config(text=f"{self.current_cycle}セット目：作業中")
            self.total_seconds = self.work_min * 60
            notify("作業スタート！", f"{self.work_min}分集中しよう！", "start.wav")
        else:
            self.status_label.config(text=f"{self.current_cycle}セット目：休憩中")
            self.total_seconds = self.break_min * 60
            notify("休憩タイム", f"{self.break_min}分休もう！", "break.wav")

        self.start_time = time.time()
        self.remaining_seconds = self.total_seconds
        self.update_timer()

    def update_timer(self):
        if not self.running:
            return

        if self.paused:
            self.start_time += 1
            self.master.after(1000, self.update_timer)
            return

        elapsed = int(time.time() - self.start_time)
        self.remaining_seconds = self.total_seconds - elapsed

        if self.remaining_seconds <= 0:
            self.timer_label.config(text="00:00")
            if self.phase == "work":
                self.phase = "break"
            else:
                self.phase = "work"
                self.current_cycle += 1
            self.start_phase()
            return

        mins, secs = divmod(self.remaining_seconds, 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")
        self.master.after(1000, self.update_timer)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.status_label.config(text=f"{self.current_cycle}セット目：一時停止中")
            notify("一時停止", "作業が一時停止されました", "stop.wav")
        else:
            self.status_label.config(text=f"{self.current_cycle}セット目：再開中")
            notify("再開", "作業を再開します", "start.wav")

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.timer_label.config(text="00:00")
        self.status_label.config(text="リセット済み")
        notify("リセット", "タイマーをリセットしました", "stop.wav")

root = tk.Tk()
app = PomodoroTimer(root)
root.mainloop()
