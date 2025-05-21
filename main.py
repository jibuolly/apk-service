# Trigger redeploy

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, re, shutil, subprocess, requests, zipfile
from urllib.parse import unquote_plus
from pathlib import Path
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

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

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

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

    # Step 3: Download or copy icon and splash
    icon_url = f"https://apk-service-production.up.railway.app/output/{site_name}-512x512.png"
    splash_url = f"https://apk-service-production.up.railway.app/output/{site_name}-splash-1280x1920.png"

    icon_target = app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
    splash_target = app_dir / "app" / "src" / "main" / "res" / "drawable" / "splash.png"
    splash_target.parent.mkdir(parents=True, exist_ok=True)

    # Copy icon and splash from /app/output/ folder
    shutil.copy(f"/app/output/{site_name}-512x512.png", icon_target)
    shutil.copy(f"/app/output/{site_name}-splash-1280x1920.png", splash_target)

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

    # Step 5: Build APK
    subprocess.run(["chmod", "+x", "./gradlew"], check=True)
    result = subprocess.run(["./gradlew", "assembleDebug"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Build failed:")
        print(result.stdout)
        print(result.stderr)
        return JSONResponse(status_code=500, content={"error": "APK build failed"})

    print("✅ APK build successful")

    # Step 6: Locate the APK
    apk_path = app_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    if not apk_path.exists():
        return JSONResponse(status_code=500, content={"error": "APK not found after build"})

    # Copy APK to output for download (optional)
    shutil.copy(apk_path, output_dir / f"{site_name}.apk")
    print(f"✅ Final APK saved")

    # Step 7: Trigger GitHub Actions workflow
    import httpx

    trigger_url = "https://api.github.com/repos/jibuolly/apk-service/actions/workflows/apk-builder.yml/dispatches"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "ref": "main"
        "inputs": {
            "site_name": site_name
        }
    }

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

    return JSONResponse(content={
        "message": "APK built successfully",
        "apk_url": f"/output/{site_name}.apk"
    })

    # Trigger GitHub Actions workflow
