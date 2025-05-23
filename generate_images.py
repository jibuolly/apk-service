from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon(sitename, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    text = sitename[0].upper()
    font_size = 300

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # ✅ Center the text using textbbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    draw.text(position, text, font=font, fill="white")

    return image

def generate_splash(sitename, color_hex):
    size = (1280, 1920)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    text = sitename.title()
    font_size = 120

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    draw.text(position, text, font=font, fill="white")

    return image

if __name__ == "__main__":
    import sys
    sitename = sys.argv[1] if len(sys.argv) > 1 else "demo"
    color = sys.argv[2] if len(sys.argv) > 2 else "#000000"

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    icon = generate_icon(sitename, color)
    icon_path = os.path.join(output_dir, f"{sitename}-512x512.png")
    icon.save(icon_path)
    print(f"✅ Icon saved to {icon_path}")

    splash = generate_splash(sitename, color)
    splash_path = os.path.join(output_dir, f"{sitename}-splash-1280x1920.png")
    splash.save(splash_path)
    print(f"✅ Splash saved to {splash_path}")
