import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog

from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()


# Map user choices to Pillow format names and extensions
FORMAT_CHOICES = {
    "1": ("JPEG", "jpg"),
    "2": ("PNG",  "png"),
    "3": ("WEBP", "webp"),
}

# For compress-only: map extension → Pillow format
EXT_FORMAT_MAP = {
    "jpg":  "JPEG",
    "jpeg": "JPEG",
    "png":  "PNG",
    "webp": "WEBP",
}


def choose_operation():
    print("\nPick an operation:")
    print("  1. Convert")
    print("  2. Compress")
    print("  3. Compress & Convert")
    print("  4. Remove metadata")              
    op = input("Your choice: ").strip()
    return {"1": "convert",
            "2": "compress",
            "3": "both",
            "4": "metadata"                  
           }.get(op)


def choose_formats():
    print("\nSelect output format(s) (comma-separated):")
    for k, (fmt, _) in FORMAT_CHOICES.items():
        print(f"  {k}. {fmt}")
    picks = input("Choice(s): ")
    chosen = [
        FORMAT_CHOICES[p.strip()]
        for p in picks.split(",")
        if p.strip() in FORMAT_CHOICES
    ]
    if not chosen:
        print("No valid format chosen. Exiting.")
        sys.exit(1)
    return chosen  


def choose_quality():
    while True:
        q = input("\nEnter quality (0-100; 100=best clarity, largest size): ").strip()
        try:
            qi = int(q)
            if 0 <= qi <= 100:
                return qi
        except:
            pass
        print("Please enter an integer between 0 and 100.")


def get_save_kwargs(ext, quality):
    """Given an extension and quality, return Pillow kwargs."""
    if quality is None:
        return {}
    if ext in ("jpg", "jpeg", "webp"):
        return {"quality": quality}
    if ext == "png":
        # Map quality(0-100) → compress_level(9-0)
        level = int(round((100 - quality) / 100 * 9))
        return {"optimize": True, "compress_level": level}
    return {}


def pick_folder():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(title="Select folder with images")
    if not path:
        print("No folder selected. Exiting.")
        sys.exit(1)
    return path


def is_image_file(name):
    return name.lower().endswith((
        ".jpg", ".jpeg", ".png", ".webp",
        ".bmp", ".gif", ".tiff", ".heic"
    ))


def main():
    src_root = pick_folder()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = os.path.join(os.path.dirname(src_root), f"converted_{timestamp}")
    os.makedirs(out_root, exist_ok=True)

    op = choose_operation()
    if op not in ("convert", "compress", "both", "metadata"):
        print("Invalid operation. Exiting.")
        sys.exit(1)

    formats = choose_formats() if op in ("convert", "both") else None
    quality = choose_quality() if op in ("compress", "both") else None

    total = 0
    for dirpath, _, filenames in os.walk(src_root):
        rel_dir = os.path.relpath(dirpath, src_root)
        target_dir = os.path.join(out_root, rel_dir)
        os.makedirs(target_dir, exist_ok=True)

        for fname in filenames:
            if not is_image_file(fname):
                continue
            src_path = os.path.join(dirpath, fname)
            try:
                img = Image.open(src_path)
            except Exception as e:
                print(f"⚠ Skipping {src_path}: {e}")
                continue

            # Ensure mode
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            name_root, orig_ext = os.path.splitext(fname)
            orig_ext = orig_ext.lower().lstrip(".")

            # 1) Convert-only
            if op == "convert":
                for fmt, ext in formats:
                    out_path = os.path.join(target_dir, f"{name_root}.{ext}")
                    img.save(out_path, fmt)
                    total += 1
                    print(f"✔ Converted: {out_path}")

            # 2) Compress-only
            elif op == "compress":
                out_ext = orig_ext if orig_ext in EXT_FORMAT_MAP else "jpg"
                fmt = EXT_FORMAT_MAP.get(out_ext, "JPEG")
                kwargs = get_save_kwargs(out_ext, quality)
                out_path = os.path.join(target_dir, f"{name_root}.{out_ext}")
                img.save(out_path, fmt, **kwargs)
                total += 1
                print(f"✔ Compressed: {out_path} (quality={quality})")

            # 3) Compress & Convert
            elif op == "both":
                for fmt, ext in formats:
                    out_path = os.path.join(target_dir, f"{name_root}.{ext}")
                    kwargs = get_save_kwargs(ext, quality)
                    img.save(out_path, fmt, **kwargs)
                    total += 1
                    print(f"✔ Compressed+Converted: {out_path} (quality={quality})")

            # 4) Remove metadata
            elif op == "metadata":
                # Keep original extension/format, save without any metadata
                out_ext = orig_ext
                fmt = EXT_FORMAT_MAP.get(out_ext, orig_ext.upper())
                out_path = os.path.join(target_dir, f"{name_root}.{out_ext}")
                # Saving without any exif/pnginfo strips metadata by default
                img.save(out_path, fmt)
                total += 1
                print(f"✔ Metadata removed: {out_path}")

    print(f"\n✅ Done! Processed {total} files into:\n  {out_root}")


if __name__ == "__main__":
    main()
