
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, re, shutil, subprocess
from urllib.parse import unquote_plus, urlparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import httpx

app = FastAPI()

@app.post("/submit")
async def handle_form(request: Request):
    body = await request.body()
    print("✅ Raw body received:", body.decode("utf-8"))

    data = dict(re.findall(r'([\w\[\]_]+)=([^&]+)', body.decode("utf-8")))
    email = unquote_plus(data.get("email", ""))
    website_url = unquote_plus(data.get("website_url", ""))
    brand_color = unquote_plus(data.get("brand_color", "#000000"))

    if not email or not website_url:
        return JSONResponse(status_code=400, content={"error": "Missing email or website_url"})

    parsed = urlparse(website_url)
    hostname = parsed.hostname or website_url
    if hostname.startswith("www."):
        hostname = hostname[4:]
    site_name = hostname.split(".")[0].lower()
    full_domain = hostname

    package_name = f"com.{site_name}.android"
    app_label = site_name.capitalize()

    print(f"✅ App name: {package_name}")
    print(f"✅ Website: {website_url}")
    print(f"✅ Brand color: {brand_color}")

    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    icon_path = output_dir / f"{site_name}-512x512.png"
    splash_path = output_dir / f"{site_name}-splash-1280x1920.png"

    # Icon
    icon_img = Image.new("RGB", (512, 512), color=brand_color)
    draw_icon = ImageDraw.Draw(icon_img)
    font_icon = ImageFont.load_default()
    draw_icon.text((200, 220), site_name[:1].upper(), font=font_icon, fill="white")
    icon_img.save(icon_path)
    print(f"✅ Icon created at: {icon_path}")

    # Splash
    splash_img = Image.new("RGB", (1280, 1920), color=brand_color)
    draw_splash = ImageDraw.Draw(splash_img)
    font_splash = ImageFont.load_default()
    draw_splash.text((540, 900), app_label, font=font_splash, fill="white")
    splash_img.save(splash_path)
    print(f"✅ Splash created at: {splash_path}")

    # Workspace
    working_dir = Path(f"/tmp/{site_name}")
    if working_dir.exists():
        shutil.rmtree(working_dir)
    working_dir.mkdir(parents=True)

    os.chdir(working_dir)
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/jibuolly/apk-template.git"], check=True)
    app_dir = working_dir / "apk-template"
    os.chdir(app_dir)

    # Place icon and splash
    # Ensure the mipmap-xxxhdpi and drawable folders exist
    (app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi").mkdir(parents=True, exist_ok=True)
    (app_dir / "app" / "src" / "main" / "res" / "drawable").mkdir(parents=True, exist_ok=True)

    # Copy icon and splash
    shutil.copy(str(icon_path), app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png")
    shutil.copy(str(splash_path), app_dir / "app" / "src" / "main" / "res" / "drawable" / "splash.png")

    print(f"✅ Copied icon to {app_dir}/res/mipmap-xxxhdpi")
    print(f"✅ Copied splash to {app_dir}/res/drawable")

    print("ℹ️ Skipping local APK check, triggering GitHub Actions instead.")

    # Trigger GitHub
    trigger_url = "https://api.github.com/repos/jibuolly/apk-service/dispatches"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "event_type": "build-apk",
        "client_payload": {
            "site_name": site_name,
            "app_label": app_label,
            "website_url": website_url
        }
    }

    try:
        print(f"⚠️ Debug Triggering GitHub Workflow:")
        print("POST", trigger_url)
        print("Headers:", headers)
        r = httpx.post(trigger_url, headers=headers, json=payload)
        print(f"✅ Triggered GitHub Actions: {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger GitHub Actions: {e}")

    return JSONResponse(content={
        "message": "Triggered GitHub Actions for APK build",
        "apk_expected": f"{site_name}.apk"
    })
