from PIL import Image, ImageDraw, ImageFont
import sys
import os

def get_text_color(bg_hex):
    bg_hex = bg_hex.lstrip("#")
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"

def generate_icon(sitename, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    font_size = 280
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename.strip().capitalize()[0]
    text_color = get_text_color(color_hex)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=text_color, font=font)
    return image

def generate_splash(sitename, color_hex):
    size = (1280, 1920)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    font_size = 150
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename.capitalize()
    text_color = get_text_color(color_hex)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=text_color, font=font)
    return image

if __name__ == "__main__":
    sitename = sys.argv[1]
    color = sys.argv[2]

    os.makedirs("output", exist_ok=True)

    icon = generate_icon(sitename, color)
    icon.save(f"output/{sitename}-512x512.png")

    splash = generate_splash(sitename, color)
    splash.save(f"output/{sitename}-splash-1280x1920.png")
