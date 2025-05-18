from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import os

app = FastAPI()

# Ensure output folder exists
if not os.path.exists("output"):
    os.makedirs("output")

# Mount /output for image access
app.mount("/output", StaticFiles(directory="output"), name="output")

# --- Utility functions ---

def extract_domain(website_url):
    parsed = urlparse(website_url)
    domain = parsed.netloc or parsed.path
    domain = domain.replace("www.", "").split('.')[0]
    return domain

def load_font(size):
    try:
        return ImageFont.truetype("Font.ttf", size)
    except:
        return ImageFont.load_default()

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def get_contrast_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "white" if brightness < 128 else "black"

# --- Image generators ---

def create_icon(domain_letter, brand_color, filename):
    size = (512, 512)
    image = Image.new("RGB", size, brand_color)
    draw = ImageDraw.Draw(image)
    font = load_font(300)
    text_color = get_contrast_text_color(brand_color)

    w, h = get_text_size(draw, domain_letter, font)
    ascent, descent = font.getmetrics()
    total_height = ascent + descent
    x = (size[0] - w) / 2
    y = (size[1] - total_height) / 2 + (ascent - h) / 2

    draw.text((x, y), domain_letter, fill=text_color, font=font)
    image.save(filename)

def create_splash(text, brand_color, filename):
    size = (1280, 1920)
    image = Image.new("RGB", size, brand_color)
    draw = ImageDraw.Draw(image)
    font = load_font(250)
    text_color = get_contrast_text_color(brand_color)

    w, h = get_text_size(draw, text, font)
    ascent, descent = font.getmetrics()
    total_height = ascent + descent
    x = (size[0] - w) / 2
    y = (size[1] - total_height) / 2 + (ascent - h) / 2

    draw.text((x, y), text, fill=text_color, font=font)
    image.save(filename)

# --- Submission route ---

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

        icon_filename = f"{domain}-512x512.png"
        splash_filename = f"{domain}-splash-1280x1920.png"
        icon_path = f"output/{icon_filename}"
        splash_path = f"output/{splash_filename}"

        create_icon(domain[0].upper(), brand_color, icon_path)
        create_splash(domain.upper(), brand_color, splash_path)

        icon_url = f"https://apk-service-production.up.railway.app/output/{icon_filename}"
        splash_url = f"https://apk-service-production.up.railway.app/output/{splash_filename}"

        print(f"✅ App name: {app_name}")
        print(f"✅ Icon URL: {icon_url}")
        print(f"✅ Splash URL: {splash_url}")

        return JSONResponse(content={
            "message": "Assets generated successfully!",
            "app_name": app_name,
            "icon_url": icon_url,
            "splash_url": splash_url
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Health check route ---
@app.get("/")
async def root():
    return {"message": "API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
