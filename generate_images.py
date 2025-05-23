from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon(sitename, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    # Determine white or black font color based on background brightness
    r, g, b = Image.new("RGB", (1, 1), color_hex).getpixel((0, 0))
    brightness = (r*299 + g*587 + b*114) / 1000
    text_color = "black" if brightness > 186 else "white"

    font_size = 280
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename[0].upper()

    # Use textbbox for compatibility with newer Pillow
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

    # Determine white or black font color based on background brightness
    r, g, b = Image.new("RGB", (1, 1), color_hex).getpixel((0, 0))
    brightness = (r*299 + g*587 + b*114) / 1000
    text_color = "black" if brightness > 186 else "white"

    font_size = 160
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename.capitalize()
    text_width, text_height = draw.textsize(text, font=font)
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=text_color, font=font)
    return image

if __name__ == "__main__":
    import sys
    import os

    sitename = sys.argv[1]
    color = sys.argv[2]

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    icon = generate_icon(sitename, color)
    icon.save(f"output/{sitename}-512x512.png")

    splash = generate_splash(sitename, color)
    splash.save(f"output/{sitename}-splash-1280x1920.png")

