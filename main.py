from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import os

app = FastAPI()

# Mount static directory to serve images
# Ensure the 'output' folder exists before mounting it
if not os.path.exists("output"):
    os.makedirs("output")

app.mount("/output", StaticFiles(directory="output"), name="output")

def extract_domain(website_url):
    parsed = urlparse(website_url)
    domain = parsed.netloc or parsed.path
    domain = domain.replace("www.", "").split('.')[0]
    return domain

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def create_icon(domain_letter, brand_color, filename):
    size = (512, 512)
    image = Image.new("RGB", size, brand_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 300)
    except:
        font = ImageFont.load_default()

    w, h = get_text_size(draw, domain_letter, font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), domain_letter, fill="white", font=font)
    image.save(filename)

def create_splash(text, brand_color, filename):
    size = (1280, 1920)
    image = Image.new("RGB", size, brand_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 250)
    except:
        font = ImageFont.load_default()

    w, h = get_text_size(draw, text, font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill="white", font=font)
    image.save(filename)

@app.post("/submit")
async def submit(request: Request):
    try:
        body = await request.body()
        decoded = body.decode("utf-8")
        print("✅ Raw body received:", decoded)

        parsed_data = parse_qs(decoded)
        email = parsed_data.get("email", [""])[0]
        website_url = parsed_data.get("website_url", [""])[0]
        brand_color = parsed_data.get("brand_color", [""])[0]

        domain = extract_domain(website_url)
        app_name = f"com.{domain}.android"

        os.makedirs("output", exist_ok=True)
        icon_filename = f"{domain}-512x512.png"
        splash_filename = f"{domain}-splash-1280x1920.png"
        icon_path = f"output/{icon_filename}"
        splash_path = f"output/{splash_filename}"

        create_icon(domain[0].upper(), brand_color, icon_path)
        create_splash(domain.upper(), brand_color, splash_path)

        icon_url = f"https://app.jibuolly.com/output/{icon_filename}"
        splash_url = f"https://app.jibuolly.com/output/{splash_filename}"

        print(f"✅ App name: {app_name}")
        print(f"✅ Icon URL: {icon_url}")
        print(f"✅ Splash URL: {splash_url}")

        return JSONResponse(content={
            "message": "Assets generated successfully!",
            "app_name": app_name,
            "icon_url": icon_url,
            "splash_url": splash_url
        })
