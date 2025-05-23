from PIL import Image, ImageDraw, ImageFont
import sys
import os

def generate_icon(site_name, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    font_size = 160 if len(site_name) <= 6 else 100
    font = ImageFont.truetype("arial.ttf", font_size)
    text = site_name[0].upper()

    text_width, text_height = draw.textsize(text, font=font)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    draw.text(position, text, fill="white", font=font)
    return image

def generate_splash(site_name, color_hex):
    size = (1280, 1920)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    font_size = 200 if len(site_name) <= 8 else 120
    font = ImageFont.truetype("arial.ttf", font_size)
    text = site_name.capitalize()

    text_width, text_height = draw.textsize(text, font=font)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    draw.text(position, text, fill="white", font=font)
    return image

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_images.py sitename hexcolor")
        sys.exit(1)

    sitename = sys.argv[1].lower()
    color = sys.argv[2]

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    icon = generate_icon(sitename, color)
    splash = generate_splash(sitename, color)

    icon.save(f"{output_dir}/{sitename}-512x512.png")
    splash.save(f"{output_dir}/{sitename}-splash-1280x1920.png")

    print(f"✅ Generated images for {sitename}")
