import argparse
from pathlib import Path
from tkinter import Tk, filedialog

from PIL import Image


ICON_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
SUPPORTED_EXTENSIONS = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
    ("All files", "*.*"),
]


def choose_source_file():
    root = Tk()
    root.withdraw()
    root.update()
    source = filedialog.askopenfilename(title="Select source image", filetypes=SUPPORTED_EXTENSIONS)
    root.destroy()
    return Path(source) if source else None


def choose_output_file(default_name):
    root = Tk()
    root.withdraw()
    root.update()
    output = filedialog.asksaveasfilename(
        title="Save ICO file",
        defaultextension=".ico",
        initialfile=default_name,
        filetypes=[("ICO files", "*.ico")],
    )
    root.destroy()
    return Path(output) if output else None


def convert_to_ico(source_path, output_path):
    with Image.open(source_path) as image:
        rgba_image = image.convert("RGBA")
        rgba_image.save(output_path, format="ICO", sizes=ICON_SIZES)


def parse_args():
    parser = argparse.ArgumentParser(description="Convert an image to Windows ICO format.")
    parser.add_argument("source", nargs="?", help="Path to the source image")
    parser.add_argument("output", nargs="?", help="Output .ico path")
    return parser.parse_args()


def main():
    args = parse_args()

    source_path = Path(args.source) if args.source else choose_source_file()
    if not source_path:
        print("No source image selected.")
        return 1

    if not source_path.exists():
        print(f"Source image not found: {source_path}")
        return 1

    output_path = Path(args.output) if args.output else choose_output_file(f"{source_path.stem}.ico")
    if not output_path:
        print("No output path selected.")
        return 1

    convert_to_ico(source_path, output_path)
    print(f"ICO created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())