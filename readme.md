# 🎬 AVStitchTool

### FFmpeg-powered media processing by Alexander Cuenin

## Description

The AVStitchTool is a straightforward desktop application designed to simplify common video and audio manipulation tasks using **FFmpeg**. It provides a user-friendly interface for two primary operations:

  * **🔗 Stitch Audio + Video:** Combine a video file with a separate audio file to create a new video with synchronized audio. This is perfect for syncing high-quality audio tracks to video recordings.
  * **🔇 Strip Audio:** Quickly remove the audio track from any video file, resulting in a video-only output.

This tool aims to make powerful FFmpeg commands accessible without needing to touch the command line.

-----

## OS Compatibility

This application is built with **Python Tkinter** and should run on any operating system that supports Python and FFmpeg.

  * **Windows:** An executable (`.exe`) file will typically be available in the [releases section](https://github.com/AlexanderCuenin/Audio-Video-Stitcher/releases) of this repository for direct use.
  * **macOS / Linux:** You'll need to run the Python script directly or use a tool like **PyInstaller** (as described in the "Building an Executable" section) to create a platform-specific application.

-----

## Requirements

To use the AVStitchTool, you'll need:

  * **Python 3.x:** (Tested with Python 3.11+)
      * [Download Python](https://www.python.org/downloads/)
  * **FFmpeg:** This is the tool that does all the video and audio magic.
      * [Download FFmpeg](https://ffmpeg.org/download.html) (You'll download this, and then tell the AVStitchTool where to find it.)

-----

## Installation & Setup

1.  **Install Python:** Download and install Python from the official website. It's often helpful to check the option **"Add Python to PATH"** during installation (if available) for easier command-line use, but it's not strictly required for running the `.exe` version of this app.
2.  **Install FFmpeg:**
    * Go to the official [FFmpeg download page](https://ffmpeg.org/download.html) and follow their instructions to download and set it up.
    * What you're looking for is the **`ffmpeg.exe`** file. After you download FFmpeg, you'll usually find this `ffmpeg.exe` file inside a folder named **`bin`** (e.g., `C:\wherever-you-put-ffmpeg\bin\ffmpeg.exe`).
    * **This `ffmpeg.exe` file is the one you'll point the AVStitchTool to later in the app's settings.** You don't need to do any tricky system setup!
3.  **Download the AVStitchTool:**
      * **For Windows users:**
        * Download the latest `AVStitchTool.exe` from the [releases section](https://github.com/AlexanderCuenin/Audio-Video-Stitcher/releases).
        * **It's recommended to place the `.exe` in its own dedicated folder. The application will create a `stitcher_config.json` file in the same directory to save your FFmpeg path and other settings.**
      * **For other OS or if running from source:** Clone this repository or download the source code:
        ```bash
        git clone [https://github.com/AlexanderCuenin/Audio-Video-Stitcher.git](https://github.com/AlexanderCuenin/Audio-Video-Stitcher.git)
        cd Audio-Video-Stitcher
        ```
4.  **Install Python Dependencies:**
    If you downloaded the source code, install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: A `requirements.txt` file is not currently in your provided code, but it's good practice for Python projects. It would list `tkinter` and any other external dependencies.)

-----

## Usage

1.  **Launch the Application:**
      * **Windows Executable:** Double-click `AVStitchTool.exe`.
      * **Python Script:** Run `python AVStitchTool.py` (or `python your_main_script_name.py` if you renamed it).
2.  **Configure FFmpeg Path:**
      * In the "FFmpeg Configuration" section, click **"Browse"** to locate your FFmpeg executable (e.g., `ffmpeg.exe` on Windows).
      * Click **"Save"** to save this path for future sessions. The status indicator will turn green if configured correctly.
3.  **Select Operation Mode:**
      * Choose **"🔗 Stitch Audio + Video"** to combine separate audio and video files.
      * Choose **"🔇 Strip Audio"** to remove audio from a video.
4.  **Input Files:**
      * **For "Stitch" mode:** Use **"Browse"** next to "Video Source" and "Audio Source" to select your input files.
      * **For "Strip" mode:** Use **"Browse"** next to "Video File" to select the video you want to process.
5.  **Set Output File:**
      * Click **"Browse"** next to "Output File" to choose where to save your processed file and define its filename (e.g., `my_stitched_video.mp4`, `my_video_no_audio.mp4`).
6.  **Review Command Preview:** The "Command Preview" box will automatically show the FFmpeg command the app will use. This means no surprises, and you can see exactly what's happening under the hood.
7.  **Execute Command:** Once all inputs are set and the command preview looks correct, click the **"Execute FFmpeg Command"** button.
8.  **Monitor Progress:** A progress bar will indicate activity, and the status text at the bottom will update upon completion. A success or error message will appear in a pop-up.

-----

## Troubleshooting

  * **"FFmpeg path not set" / Red Indicator:** Ensure you've correctly located and saved the path to your `ffmpeg.exe` (or `ffmpeg` on Linux/macOS) in the application.
  * **"FFmpeg command failed" Error:**
      * Double-check that your input files are valid and accessible.
      * Ensure the FFmpeg path is correct and FFmpeg is properly installed and working (you can test it by running `ffmpeg -version` in a terminal).
      * Verify that you have read/write permissions in the directories you are using for input and output.
      * Check the full error message in the pop-up for more specific details from FFmpeg.
  * **Application not launching (from source):** Make sure you have Python installed and any required dependencies (though currently minimal for this app).

-----

## Building an Executable (for Developers/Advanced Users)

If you've cloned the source code and want to create a standalone executable for distribution (especially for Windows):

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Navigate to your project directory** in your terminal where `AVStitchTool.py` (or your main script) is located.
3.  **Run PyInstaller:**
    ```bash
    python -m PyInstaller --onefile --windowed AVStitchTool.py --name "AVStitchTool"
    ```
      * `--onefile`: Creates a single `.exe` file.
      * `--windowed`: Prevents a console window from appearing when the app runs.
      * `--name "AVStitchTool"`: Sets the name of the executable file to `AVStitchTool.exe`.
4.  **Find your executable** in the newly created `dist/` folder within your project directory.

-----
