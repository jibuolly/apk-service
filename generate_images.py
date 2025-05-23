from PIL import Image, ImageDraw, ImageFont
import os
import sys

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def generate_icon(site_name, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)
    font_size = 130

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    text = site_name[0].upper()
    text_width, text_height = get_text_size(draw, text, font)
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill="white", font=font)
    return image

def generate_splash(site_name, color_hex):
    size = (1280, 1920)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)
    font_size = 120

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    text = site_name.capitalize()
    text_width, text_height = get_text_size(draw, text, font)
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill="white", font=font)
    return image

if __name__ == "__main__":
    sitename = sys.argv[1]
    color = sys.argv[2]

    os.makedirs("output", exist_ok=True)

    icon = generate_icon(sitename, color)
    icon.save(f"output/{sitename}-512x512.png")

    splash = generate_splash(sitename, color)
    splash.save(f"output/{sitename}-splash-1280x1920.png")

    print(f"✅ Icon and splash generated for {sitename}")
