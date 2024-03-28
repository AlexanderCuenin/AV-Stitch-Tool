import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import subprocess
import re
import os

CONFIG_FILE = "config.txt"

def select_video():
    file_path = filedialog.askopenfilename(filetypes=(("Video files", "*.mp4;*.mkv;*.avi"), ("All files", "*.*")))
    video_entry.delete(0, tk.END)
    video_entry.insert(0, file_path)

def select_audio():
    file_path = filedialog.askopenfilename(filetypes=(("Audio files", "*.mp3;*.wav;*.aac"), ("All files", "*.*")))
    audio_entry.delete(0, tk.END)
    audio_entry.insert(0, file_path)

def select_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=(("MP4 Video", "*.mp4"),))
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)

def select_ffmpeg_location():
    global ffmpeg_executable
    file_path = filedialog.askopenfilename(filetypes=(("Executable files", "*.exe"), ("All files", "*.*")))
    ffmpeg_executable = file_path
    save_config()

def save_config():
    global ffmpeg_executable
    with open(CONFIG_FILE, "w") as f:
        f.write(ffmpeg_executable)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    return ""

def stitch_audio_video():
    video_path = video_entry.get()
    audio_path = audio_entry.get()
    output_path = output_entry.get()

    if not video_path or not audio_path or not output_path:
        messagebox.showerror("Error", "Please select video, audio, and specify an output file.")
        return

    if not ffmpeg_executable:
        messagebox.showerror("Error", "Please select the location of ffmpeg executable.")
        return

    cmd = [
        ffmpeg_executable, '-i', video_path, '-i', audio_path,
        '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', output_path
    ]

    progress_window = tk.Toplevel(root)
    progress_window.title("Progress")
    
    # Calculate DPI scale factor
    dpi = 163.18
    scale_factor = dpi / 72
    progress_window.tk.call('tk', 'scaling', scale_factor)

    progress_label = tk.Label(progress_window, text="Stitching in progress...")
    progress_label.pack(padx=10, pady=5)

    progress_bar = Progressbar(progress_window, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(padx=10, pady=5)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        duration = None

        for line in process.stdout:
            if "Duration:" in line:
                # Extract duration from ffmpeg output
                match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", line)
                if match:
                    hours, minutes, seconds = map(float, match.groups())
                    duration = hours * 3600 + minutes * 60 + seconds

            if "time=" in line:
                # Extract time from ffmpeg output
                match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                if match and duration:
                    hours, minutes, seconds = map(float, match.groups())
                    current_time = hours * 3600 + minutes * 60 + seconds

                    # Update progress bar
                    progress_percent = (current_time / duration) * 100
                    progress_bar["value"] = progress_percent
                    progress_window.update_idletasks()

        process.communicate()  # Wait for the process to finish

        messagebox.showinfo("Success", "Audio and video have been stitched successfully!")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "An error occurred during the stitching process.")
    finally:
        progress_window.destroy()

# GUI Setup
root = tk.Tk()
root.title("Audio-Video Stitcher")

# Load FFmpeg location
ffmpeg_executable = load_config()

# FFmpeg location selection
ffmpeg_button = tk.Button(root, text="Set FFmpeg Destination", command=select_ffmpeg_location)
ffmpeg_button.grid(row=0, column=0, columnspan=3, pady=10)

# Video selection
video_label = tk.Label(root, text="Video Source:")
video_label.grid(row=1, column=0, padx=5, pady=5)
video_entry = tk.Entry(root, width=40)
video_entry.grid(row=1, column=1, padx=5, pady=5)
video_button = tk.Button(root, text="Browse", command=select_video)
video_button.grid(row=1, column=2, padx=5, pady=5)

# Audio selection
audio_label = tk.Label(root, text="Audio Source:")
audio_label.grid(row=2, column=0, padx=5, pady=5)
audio_entry = tk.Entry(root, width=40)
audio_entry.grid(row=2, column=1, padx=5, pady=5)
audio_button = tk.Button(root, text="Browse", command=select_audio)
audio_button.grid(row=2, column=2, padx=5, pady=5)

# Output selection
output_label = tk.Label(root, text="Output File:")
output_label.grid(row=3, column=0, padx=5, pady=5)
output_entry = tk.Entry(root, width=40)
output_entry.grid(row=3, column=1, padx=5, pady=5)
output_button = tk.Button(root, text="Browse", command=select_output)
output_button.grid(row=3, column=2, padx=5, pady=5)

# Stitch button
stitch_button = tk.Button(root, text="Stitch", command=stitch_audio_video, font=("Arial", 14, "bold"))
stitch_button.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
