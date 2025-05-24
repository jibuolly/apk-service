from PIL import Image, ImageDraw, ImageFont

def generate_icon(sitename, color_hex):
    size = (512, 512)
    image = Image.new("RGB", size, color_hex)
    draw = ImageDraw.Draw(image)

    # Choose black or white text based on background brightness
    def is_light(hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r*299 + g*587 + b*114) / 1000
        return brightness > 150

    text_color = "#000000" if is_light(color_hex) else "#FFFFFF"

    font_size = 280
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename[0].upper()
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

    def is_light(hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r*299 + g*587 + b*114) / 1000
        return brightness > 150

    text_color = "#000000" if is_light(color_hex) else "#FFFFFF"

    font_size = 180
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text = sitename[0].upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=text_color, font=font)
    return image

if __name__ == "__main__":
    import os
    import sys

    sitename = sys.argv[1]
    color = sys.argv[2]

    os.makedirs("output", exist_ok=True)

    icon = generate_icon(sitename, color)
    icon.save(f"output/{sitename}-512x512.png")

    splash = generate_splash(sitename, color)
    splash.save(f"output/{sitename}-splash-1280x1920.png")
