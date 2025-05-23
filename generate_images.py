from PIL import Image, ImageDraw, ImageFont
import sys
import os

def get_contrast_color(hex_color):
    """Return black or white depending on background brightness"""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 186 else "#FFFFFF"

def generate_icon(sitename, color_hex):
    image = Image.new("RGB", (512, 512), color_hex)
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 220
    font = ImageFont.truetype(font_path, font_size)

    text = sitename[0].upper()
    text_color = get_contrast_color(color_hex)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((512 - text_width) // 2, (512 - text_height) // 2)
    draw.text(text_position, text, fill=text_color, font=font)

    return image

def generate_splash(sitename, color_hex):
    image = Image.new("RGB", (1280, 1920), color_hex)
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 160
    font = ImageFont.truetype(font_path, font_size)

    text = sitename.capitalize()
    text_color = get_contrast_color(color_hex)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((1280 - text_width) // 2, (1920 - text_height) // 2)
    draw.text(text_position, text, fill=text_color, font=font)

    return image

if __name__ == "__main__":
    sitename = sys.argv[1]
    color = sys.argv[2]

    os.makedirs("output", exist_ok=True)
    icon = generate_icon(sitename, color)
    icon.save(f"output/{sitename}-512x512.png")

    splash = generate_splash(sitename, color)
    splash.save(f"output/{sitename}-splash-1280x1920.png")

    print(f"✅ Icon and splash generated for {sitename} with color {color}")
