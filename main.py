import os
import shutil
import subprocess
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import re

app = FastAPI()

OUTPUT_DIR = "output"
TEMPLATE_DIR = "apk-template/app/src/main"
APK_OUTPUT_PATH = "apk-template/app/build/outputs/apk/debug/app-debug.apk"

# Utility to decide text color (black/white) based on brand color
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 186 else "#FFFFFF"

@app.post("/submit")
async def handle_submit(request: Request):
    try:
        body = await request.body()
        print("✅ Raw body received:", body.decode("utf-8"))

        form = await request.form()
        email = form.get("email")
        website_url = form.get("website_url")
        brand_color = form.get("brand_color", "#000000")

        # Validate and parse site name
        site_name = re.sub(r"^www\.", "", urlparse(website_url).netloc).split(".")[0].lower()
        app_label = site_name.capitalize()
        app_package = f"com.{site_name}.android"

        print(f"✅ App name: {app_package}")

        # Prepare output dir
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)

        # Icon
        icon_path = f"{OUTPUT_DIR}/{site_name}-512x512.png"
        img = Image.new("RGB", (512, 512), color=brand_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 350)
        text = site_name[0].upper()
        w, h = draw.textsize(text, font=font)
        draw.text(((512 - w) / 2, (512 - h) / 2 - 37), text, fill=get_contrast_color(brand_color), font=font)
        img.save(icon_path)
        print(f"✅ Icon saved: {icon_path}")

        # Splash
        splash_path = f"{OUTPUT_DIR}/{site_name}-splash-1280x1920.png"
        splash = Image.new("RGB", (1280, 1920), color=brand_color)
        draw = ImageDraw.Draw(splash)
        font = ImageFont.truetype("arial.ttf", 250)
        text = site_name.upper()
        w, h = draw.textsize(text, font=font)
        draw.text(((1280 - w) / 2, (1920 - h) / 2), text, fill=get_contrast_color(brand_color), font=font)
        splash.save(splash_path)
        print(f"✅ Splash saved: {splash_path}")

        # Apply changes to template
        strings_xml = os.path.join(TEMPLATE_DIR, "res/values/strings.xml")
        manifest_xml = os.path.join(TEMPLATE_DIR, "AndroidManifest.xml")
        main_activity = os.path.join(TEMPLATE_DIR, "java/com/wixify/android/MainActivity.java")

        with open(strings_xml, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_label}</string>
</resources>
""")

        with open(manifest_xml, "r") as f:
            manifest = f.read()
        manifest = manifest.replace('package="com.wixify.android"', f'package="{app_package}"')
        with open(manifest_xml, "w") as f:
            f.write(manifest)

        with open(main_activity, "r") as f:
            code = f.read()
        code = re.sub(r'mWebView\.loadUrl\(".*?"\)', f'mWebView.loadUrl("{website_url}")', code)
        with open(main_activity, "w") as f:
            f.write(code)

        # Copy images to mipmap folder
        shutil.copy(icon_path, os.path.join(TEMPLATE_DIR, "res/mipmap-hdpi/ic_launcher.png"))
        shutil.copy(splash_path, os.path.join(TEMPLATE_DIR, "res/drawable/splash.png"))

        # Build APK
        result = subprocess.run(["./gradlew", "assembleDebug"], cwd="apk-template", capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Build failed:")
            print(result.stdout)
            print(result.stderr)
            return JSONResponse(status_code=500, content={"error": "APK build failed"})

        print("✅ APK build completed.")

        # Email logic comes next in step 3...

        return JSONResponse(content={
            "message": "APK built successfully",
            "apk_path": APK_OUTPUT_PATH
        })

    except Exception as e:
        print("❌ Exception:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
