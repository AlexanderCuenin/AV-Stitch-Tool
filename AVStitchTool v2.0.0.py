import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
import threading

class AudioVideoStitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("AVStitchTool") # Renamed the title here
        self.root.geometry("600x870")
        self.root.resizable(True, True)
        
        # Configuration file path
        self.config_file = "stitcher_config.json"
        self.config = self.load_config()
        
        # Current mode: 'stitch' or 'strip'
        self.current_mode = tk.StringVar(value=self.config.get('last_mode', 'stitch')) # Load last mode
        
        # File paths
        self.ffmpeg_path = tk.StringVar(value=self.config.get('ffmpeg_path', ''))
        self.video_source = tk.StringVar()
        self.audio_source = tk.StringVar()
        self.video_to_strip = tk.StringVar()
        self.output_file = tk.StringVar()

        self.setup_ui()
        self.update_ffmpeg_status()
        self.update_command_preview()
        
        # Bind variable changes to update command preview
        self.ffmpeg_path.trace('w', lambda *args: self.update_command_preview())
        self.video_source.trace('w', lambda *args: self.update_command_preview())
        self.audio_source.trace('w', lambda *args: self.update_command_preview())
        self.video_to_strip.trace('w', lambda *args: self.update_command_preview())
        self.output_file.trace('w', lambda *args: self.update_command_preview())
        self.current_mode.trace('w', lambda *args: self.on_mode_change()) # Call on_mode_change (mostly for saving mode)

    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        row = 0
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="🎬 AVStitchTool", 
                                 font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, text="FFmpeg-powered media processing tool by Alexander Cuenin", 
                                     font=('Arial', 10))
        subtitle_label.grid(row=1, column=0)
        
        row += 1
        
        # FFmpeg Configuration Section
        ffmpeg_frame = ttk.LabelFrame(main_frame, text="⚙️ FFmpeg Configuration", padding="15")
        ffmpeg_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        ffmpeg_frame.columnconfigure(0, weight=1)
        
        # FFmpeg path input
        ffmpeg_input_frame = ttk.Frame(ffmpeg_frame)
        ffmpeg_input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ffmpeg_input_frame.columnconfigure(0, weight=1)
        
        self.ffmpeg_entry = ttk.Entry(ffmpeg_input_frame, textvariable=self.ffmpeg_path, 
                                        font=('Arial', 9))
        self.ffmpeg_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(ffmpeg_input_frame, text="Browse", 
                   command=self.browse_ffmpeg).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(ffmpeg_input_frame, text="Save", 
                   command=self.save_ffmpeg_path).grid(row=0, column=2)
        
        # FFmpeg status
        self.status_frame = ttk.Frame(ffmpeg_frame)
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.status_indicator = tk.Label(self.status_frame, text="●", font=('Arial', 12), 
                                         fg="red")
        self.status_indicator.grid(row=0, column=0, padx=(0, 5))
        
        self.status_label = ttk.Label(self.status_frame, text="FFmpeg path not set")
        self.status_label.grid(row=0, column=1)
        
        row += 1
        
        # Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="🔧 Operation Mode", padding="15")
        mode_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        mode_buttons_frame = ttk.Frame(mode_frame)
        mode_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        mode_buttons_frame.columnconfigure(0, weight=1)
        mode_buttons_frame.columnconfigure(1, weight=1)
        
        ttk.Radiobutton(mode_buttons_frame, text="🔗 Stitch Audio + Video", 
                        variable=self.current_mode, value="stitch",
                        command=self.on_mode_change).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Radiobutton(mode_buttons_frame, text="🔇 Strip Audio", 
                        variable=self.current_mode, value="strip",
                        command=self.on_mode_change).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        row += 1
        
        # Operations Section
        self.operations_frame = ttk.LabelFrame(main_frame, text="Operations", padding="15")
        self.operations_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.operations_frame.columnconfigure(0, weight=1)
        
        # Stitch Mode Frame
        self.stitch_frame = ttk.Frame(self.operations_frame)
        self.stitch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.stitch_frame.columnconfigure(0, weight=1)
        
        ttk.Label(self.stitch_frame, text="🎥 Video Source:", 
                  font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        video_frame = ttk.Frame(self.stitch_frame)
        video_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(video_frame, textvariable=self.video_source, 
                  font=('Arial', 9)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(video_frame, text="Browse", 
                   command=lambda: self.browse_file(self.video_source, "video_input_for_output_suggestion")).grid(row=0, column=1)
        
        ttk.Label(self.stitch_frame, text="🎵 Audio Source:", 
                  font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        audio_frame = ttk.Frame(self.stitch_frame)
        audio_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        audio_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(audio_frame, textvariable=self.audio_source, 
                  font=('Arial', 9)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(audio_frame, text="Browse", 
                   command=lambda: self.browse_file(self.audio_source, "audio")).grid(row=0, column=1)
        
        # Strip Mode Frame
        self.strip_frame = ttk.Frame(self.operations_frame)
        self.strip_frame.columnconfigure(0, weight=1)
        
        ttk.Label(self.strip_frame, text="🎬 Video File:", 
                  font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        strip_video_frame = ttk.Frame(self.strip_frame)
        strip_video_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        strip_video_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(strip_video_frame, textvariable=self.video_to_strip, 
                  font=('Arial', 9)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(strip_video_frame, text="Browse", 
                   command=lambda: self.browse_file(self.video_to_strip, "video_input_for_output_suggestion")).grid(row=0, column=1)
        
        row += 1
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="💾 Output File", padding="15")
        output_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(0, weight=1)
        
        output_input_frame = ttk.Frame(output_frame)
        output_input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        output_input_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_input_frame, textvariable=self.output_file, 
                  font=('Arial', 9)).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_input_frame, text="Browse", 
                   command=self.browse_output_file).grid(row=0, column=1)
        
        row += 1
        
        # Command Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Command Preview", padding="15")
        preview_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.command_text = tk.Text(preview_frame, height=4, wrap=tk.WORD, 
                                     font=('Courier New', 9), bg='#2d3748', fg='#e2e8f0')
        self.command_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for command preview
        command_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.command_text.yview)
        command_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.command_text.configure(yscrollcommand=command_scrollbar.set)
        
        row += 1
        
        # Execute Button
        self.execute_btn = ttk.Button(main_frame, text="Execute FFmpeg Command", 
                                        command=self.execute_command, state="disabled")
        self.execute_btn.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        row += 1
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        row += 1
        
        # Status label
        self.status_text = ttk.Label(main_frame, text="Ready", font=('Arial', 10))
        self.status_text.grid(row=row, column=0, sticky=tk.W)
        
        # Initialize mode display
        self.on_mode_change()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config['ffmpeg_path'] = self.ffmpeg_path.get()
            self.config['last_mode'] = self.current_mode.get()
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def browse_ffmpeg(self):
        """Browse for FFmpeg executable"""
        filename = filedialog.askopenfilename(
            title="Select FFmpeg executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.ffmpeg_path.set(filename)

    def save_ffmpeg_path(self):
        """Save FFmpeg path to configuration"""
        path = self.ffmpeg_path.get().strip()
        if path:
            self.save_config()
            self.update_ffmpeg_status()
        else:
            messagebox.showerror("Error", "Please enter a valid FFmpeg path")

    def update_ffmpeg_status(self):
        """Update FFmpeg status indicator"""
        if self.ffmpeg_path.get().strip():
            self.status_indicator.config(fg="green")
            self.status_label.config(text="FFmpeg path configured ✓")
        else:
            self.status_indicator.config(fg="red")
            self.status_label.config(text="FFmpeg path not set")
        self.update_execute_button()

    def browse_file(self, var, file_type):
        """Browse for input files and potentially set output path"""
        if "video_input" in file_type:
            filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"), ("All files", "*.*")]
        elif file_type == "audio":
            filetypes = [("Audio files", "*.mp3 *.wav *.aac *.m4a *.ogg *.flac"), ("All files", "*.*")]
        else:
            filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"), ("All files", "*.*")]
            
        filename = filedialog.askopenfilename(
            title=f"Select {file_type.replace('_input_for_output_suggestion', '').replace('_', ' ')} file",
            filetypes=filetypes
        )
        if filename:
            var.set(filename)
            
            # Auto-fill output path with "_stitched" or "_stripped" suffix
            if "video_input_for_output_suggestion" in file_type:
                directory, base_name = os.path.split(filename)
                name, ext = os.path.splitext(base_name)
                
                suffix = ""
                if self.current_mode.get() == "stitch":
                    suffix = "_stitched"
                elif self.current_mode.get() == "strip":
                    suffix = "_stripped"
                
                # Avoid double-appending the suffix
                if not name.endswith(suffix):
                    suggested_output_name = f"{name}{suffix}{ext}"
                else:
                    suggested_output_name = f"{name}{ext}" # Keep as is if already has suffix
                        
                self.output_file.set(os.path.join(directory, suggested_output_name))

    def browse_output_file(self):
        """Browse for output file location"""
        default_name = "output.mp4"
        current_input_video_path = None

        if self.current_mode.get() == "stitch":
            current_input_video_path = self.video_source.get()
        elif self.current_mode.get() == "strip":
            current_input_video_path = self.video_to_strip.get()

        directory = os.path.expanduser("~")
        if current_input_video_path:
            directory, base_name = os.path.split(current_input_video_path)
            name, ext = os.path.splitext(base_name)
            
            suffix = ""
            if self.current_mode.get() == "stitch":
                suffix = "_stitched"
            elif self.current_mode.get() == "strip":
                suffix = "_stripped"
            
            # Avoid double-appending the suffix
            if not name.endswith(suffix):
                default_name = f"{name}{suffix}{ext}"
            else:
                default_name = f"{name}{ext}" # Keep as is if already has suffix
        
        filename = filedialog.asksaveasfilename(
            title="Save output file as",
            initialdir=directory,
            initialfile=default_name,
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)

    def on_mode_change(self):
        """Handle mode change between stitch and strip"""
        current_mode_val = self.current_mode.get()
        if current_mode_val == "stitch":
            self.stitch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.strip_frame.grid_remove()
        else: # strip mode
            self.strip_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.stitch_frame.grid_remove()
        self.update_command_preview()
        self.save_config()

    def update_command_preview(self):
        """Update the command preview text"""
        ffmpeg_path = self.ffmpeg_path.get().strip()
        output_file = self.output_file.get().strip()
        
        command = ""
        
        if self.current_mode.get() == "stitch":
            video_source = self.video_source.get().strip()
            audio_source = self.audio_source.get().strip()
            
            if ffmpeg_path and video_source and audio_source and output_file:
                command = f'"{ffmpeg_path}" -i "{video_source}" -i "{audio_source}" -c:v copy -c:a copy -map 0:v:0 -map 1:a:0 "{output_file}"'
        else:  # strip mode
            video_to_strip = self.video_to_strip.get().strip()
            
            if ffmpeg_path and video_to_strip and output_file:
                command = f'"{ffmpeg_path}" -i "{video_to_strip}" -c:v copy -an "{output_file}"'
        
        self.command_text.config(state=tk.NORMAL)
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, command if command else "Command will appear here...")
        self.command_text.config(state=tk.DISABLED)
        
        self.update_execute_button()

    def update_execute_button(self):
        """Update execute button state"""
        command = self.command_text.get(1.0, tk.END).strip()
        if (self.ffmpeg_path.get().strip() and
            command and
            command != "Command will appear here..."):
            self.execute_btn.config(state="normal")
        else:
            self.execute_btn.config(state="disabled")

    def execute_command(self):
        """Execute the FFmpeg command"""
        command = self.command_text.get(1.0, tk.END).strip()
        
        if not command or command == "Command will appear here...":
            messagebox.showerror("Error", "No valid command to execute")
            return
        
        final_output_path = self.output_file.get()

        # Disable the button and start progress
        self.execute_btn.config(state="disabled")
        self.progress.start()
        self.status_text.config(text="Processing...")
        
        # Execute in a separate thread to prevent UI freezing
        thread = threading.Thread(target=self.run_ffmpeg_command, 
                                  args=(command, final_output_path))
        thread.daemon = True
        thread.start()

    def run_ffmpeg_command(self, command, final_output_path):
        """Run FFmpeg command in a separate thread"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            self.root.after(0, self.command_completed, result.returncode, result.stderr, final_output_path)
            
        except Exception as e:
            self.root.after(0, self.command_completed, -1, str(e), None)

    def command_completed(self, return_code, error_output, final_output_path):
        """Handle command completion"""
        self.progress.stop()
        self.execute_btn.config(state="normal")
        
        if return_code == 0:
            self.status_text.config(text="✅ Processing completed successfully!")
            messagebox.showinfo("Success", "FFmpeg command executed successfully!")
        else:
            self.status_text.config(text="❌ Processing failed")
            messagebox.showerror("Error", f"FFmpeg command failed:\n\n{error_output}")

def main():
    root = tk.Tk()
    app = AudioVideoStitcher(root)
    root.mainloop()

if __name__ == "__main__":
    main()