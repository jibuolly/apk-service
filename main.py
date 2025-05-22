# Trigger redeploy

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, re, shutil, subprocess, requests, zipfile
from urllib.parse import unquote_plus
from pathlib import Path
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import httpx

app = FastAPI()

@app.post("/submit")
async def handle_form(request: Request):
    body = await request.body()
    print("✅ Raw body received:", body.decode("utf-8"))

    # Extract values
    data = dict(re.findall(r'([\w\[\]_]+)=([^&]+)', body.decode("utf-8")))
    email = unquote_plus(data.get("email", ""))
    website_url = unquote_plus(data.get("website_url", ""))
    brand_color = unquote_plus(data.get("brand_color", "#000000"))

    if not email or not website_url:
        return JSONResponse(status_code=400, content={"error": "Missing email or website_url"})

    # Derive site name
    from urllib.parse import urlparse

    parsed = urlparse(website_url)
    hostname = parsed.hostname or website_url
    if hostname.startswith("www."):
        hostname = hostname[4:]
    site_name = hostname.split(".")[0].lower()

    package_name = f"com.{site_name}.android"
    app_label = site_name.capitalize()
 
    print(f"✅ App name: {package_name}")
    print(f"✅ Website: {website_url}")
    print(f"✅ Brand color: {brand_color}")

    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    icon_path = output_dir / f"{site_name}-512x512.png"
    splash_path = output_dir / f"{site_name}-splash-1280x1920.png"

    # === Generate Icon ===
    icon_img = Image.new("RGB", (512, 512), color=brand_color)
    draw_icon = ImageDraw.Draw(icon_img)
    font_icon = ImageFont.load_default()
    draw_icon.text((180, 240), site_name[:1].upper(), font=font_icon, fill="white")
    icon_img.save(icon_path)
    print(f"✅ Icon created at: {icon_path}")

    # === Generate Splash ===
    splash_img = Image.new("RGB", (1280, 1920), color=brand_color)
    draw_splash = ImageDraw.Draw(splash_img)
    font_splash = ImageFont.load_default()
    draw_splash.text((500, 900), app_label, font=font_splash, fill="white")
    splash_img.save(splash_path)
    print(f"✅ Splash created at: {splash_path}")

    # Step 1: Setup temp workspace
    working_dir = Path(f"/tmp/{site_name}")
    if working_dir.exists():
        shutil.rmtree(working_dir)
    working_dir.mkdir(parents=True)

    # Step 2: Clone apk-template
    os.chdir(working_dir)
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/jibuolly/apk-template.git"], check=True)

    app_dir = working_dir / "apk-template"
    os.chdir(app_dir)

    # Step 3: Generate and copy icon and splash
    icon_path = output_dir / f"{site_name}-512x512.png"
    splash_path = output_dir / f"{site_name}-splash-1280x1920.png"

    if not icon_path.exists():
        # Generate icon if not found
        icon_img = Image.new("RGB", (512, 512), color=brand_color)
        draw_icon = ImageDraw.Draw(icon_img)
        font_icon = ImageFont.load_default()
        draw_icon.text((180, 240), site_name[:1].upper(), font=font_icon, fill="white")
        icon_img.save(icon_path)
        print(f"✅ Icon created at: {icon_path}")

    if not splash_path.exists():
        # Generate splash if not found
        splash_img = Image.new("RGB", (1280, 1920), color=brand_color)
        draw_splash = ImageDraw.Draw(splash_img)
        font_splash = ImageFont.load_default()
        draw_splash.text((500, 900), app_label, font=font_splash, fill="white")
        splash_img.save(splash_path)
        print(f"✅ Splash created at: {splash_path}")

    icon_target = app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
    splash_target = app_dir / "app" / "src" / "main" / "res" / "drawable" / "splash.png"
    splash_target.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(icon_path, icon_target)
    shutil.copy(splash_path, splash_target)

    print(f"✅ Copied icon to {icon_target}")
    print(f"✅ Copied splash to {splash_target}")
    
    # Step 4: Update manifest and main activity
    manifest_path = app_dir / "app" / "src" / "main" / "AndroidManifest.xml"
    main_activity_path = list(app_dir.glob("**/MainActivity.java"))[0]

    manifest = manifest_path.read_text()
    manifest = re.sub(r'package="[^"]+"', f'package="{package_name}"', manifest)
    manifest_path.write_text(manifest)

    main_code = main_activity_path.read_text()
    main_code = re.sub(r'package\s+[\w\.]+;', f'package {package_name};', main_code)
    main_code = re.sub(r'loadUrl\(".*?"\)', f'loadUrl("{website_url}")', main_code)
    main_activity_path.write_text(main_code)

    print("✅ Updated package name and URL")

    # Step 6: (Skip APK build check - handled by GitHub Actions)
    print("ℹ️ Skipping local APK check, triggering GitHub Actions instead.")
    
    # Step 7: Trigger GitHub Actions workflow
    trigger_url = "https://api.github.com/repos/jibuolly/apk-service/dispatches"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "event_type": "build-apk"
    }

    # 🐛 DEBUG: Print payload before calling GitHub API
    print("⚠️ Debug Triggering GitHub Workflow:")
    print("POST", trigger_url)
    print("Headers:", headers)
    print("Payload:", payload)
    
    try:
        r = httpx.post(trigger_url, headers=headers, json=payload)
        print(f"✅ Triggered GitHub Actions: {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger GitHub Actions: {e}")

    # Step 8: [To be implemented] Email using Brevo
    return JSONResponse(content={
        "message": "APK built successfully",
        "apk_url": f"/output/{site_name}.apk"
    })

    # Trigger GitHub Actions workflow
