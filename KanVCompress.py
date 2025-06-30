import os
import sys
import subprocess
import shutil
from datetime import datetime
from tkinter import Tk, filedialog

try:
    from imageio_ffmpeg import get_ffmpeg_exe
except ImportError:
    print("❌ Missing dependency: run `pip install imageio-ffmpeg` then re-launch.")
    sys.exit(1)

def compress_videos(input_dir, output_dir, ffmpeg_path):
    supported_exts = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
    for fname in os.listdir(input_dir):
        name, ext = os.path.splitext(fname)
        if ext.lower() not in supported_exts:
            continue

        src = os.path.join(input_dir, fname)
        tmp_dst = os.path.join(output_dir, f"{name}_tmp{ext}")
        final_dst = os.path.join(output_dir, f"{name}{ext}")

        print(f"\n🔄 Compressing {fname} → temp file…")
        cmd = [
            ffmpeg_path,
            '-i', src,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '23',
            '-c:a', 'copy',
            tmp_dst
        ]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            print(f"⚠️  Error compressing {fname}:\n{result.stderr.decode()}")
            continue

        # Compare sizes
        orig_size = os.path.getsize(src)
        comp_size = os.path.getsize(tmp_dst)
        if comp_size >= orig_size:
            print(f"⚠️  Compressed is larger ({comp_size} bytes) than original ({orig_size} bytes). Keeping original.")
            shutil.copy2(src, final_dst)
            os.remove(tmp_dst)
        else:
            os.rename(tmp_dst, final_dst)
            print(f"✅ Done: {fname} compressed to {comp_size} bytes (original was {orig_size}).")

def main():
    root = Tk()
    root.withdraw()

    print("👉 Select the folder containing your videos…")
    folder = filedialog.askdirectory(title="Choose video folder")
    if not folder:
        print("No folder selected. Exiting.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    parent = os.path.dirname(folder)
    out_folder = os.path.join(parent, f"compress_{ts}")
    os.makedirs(out_folder, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_exe()
    print(f"Using ffmpeg at: {ffmpeg_bin}")
    print(f"Output directory: {out_folder}")

    compress_videos(folder, out_folder, ffmpeg_bin)
    print("\n🎉 Finished! Check out your videos in:\n   📂", out_folder)

if __name__ == "__main__":
    main()
