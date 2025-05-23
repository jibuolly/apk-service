import os
import re
import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def handle_form(request: Request):
    body = await request.body()
    print("✅ Raw body received:", body.decode("utf-8"))

    data = await request.form()
    website_url = data.get("website_url", "").strip()

    if not website_url.startswith("http://") and not website_url.startswith("https://"):
        website_url = f"https://{website_url}"

    site_name = re.sub(r"^https?://", "", website_url).split(".")[0]
    app_label = site_name.capitalize()

    brand_color = data.get("brand_color", "#000000")
    email = data.get("email", "").strip()

    print(f"✅ App name: com.{site_name}.android")
    print(f"✅ Website: {website_url}")
    print(f"✅ Brand color: {brand_color}")

    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)

    import time

    icon_path = output_dir / f"{site_name}-512x512.png"
    splash_path = output_dir / f"{site_name}-splash-1280x1920.png"

    # Retry up to 5 times to wait for icon and splash to appear
    for i in range(5):
        if icon_path.exists() and splash_path.exists():
            break
        print(f"⏳ Waiting for icon/splash to be ready... Retry {i+1}/5")
        time.sleep(1)

    if not icon_path.exists():
        raise FileNotFoundError(f"❌ Icon not found at {icon_path}")
    if not splash_path.exists():
        raise FileNotFoundError(f"❌ Splash not found at {splash_path}")

    print(f"✅ Icon created at: {icon_path}")
    print(f"✅ Splash created at: {splash_path}")

    tmp_dir = Path("/tmp") / site_name
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    os.chdir(tmp_dir)
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/jibuolly/apk-template.git"], check=True)

    app_dir = tmp_dir / "apk-template"

    # Copy icon to all mipmap folders
    icon_target_dirs = [
        "mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi",
        "mipmap-xxhdpi", "mipmap-xxxhdpi"
    ]
    for d in icon_target_dirs:
        target_dir = app_dir / "app" / "src" / "main" / "res" / d
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(icon_path, target_dir / "ic_launcher.png")
        print(f"✅ Copied icon to {target_dir / 'ic_launcher.png'}")

    # Copy splash
    splash_target = app_dir / "app" / "src" / "main" / "res" / "drawable"
    splash_target.mkdir(parents=True, exist_ok=True)
    shutil.copy(splash_path, splash_target / "splash.png")
    print(f"✅ Copied splash to {splash_target / 'splash.png'}")

    # Update manifest and code
    manifest_path = app_dir / "app" / "src" / "main" / "AndroidManifest.xml"
    main_activity_path = app_dir / "app" / "src" / "main" / "java" / "com" / "wixify" / "android" / "MainActivity.java"
    strings_xml_path = app_dir / "app" / "src" / "main" / "res" / "values" / "strings.xml"

    manifest = manifest_path.read_text()
    manifest = re.sub(r'package="[^"]+"', f'package="com.{site_name}.android"', manifest)
    manifest_path.write_text(manifest)

    main_code = main_activity_path.read_text()
    main_code = re.sub(r'package\s+[\w\.]+;', f'package com.{site_name}.android;', main_code)
    main_code = re.sub(r'loadUrl\(".*?"\)', f'loadUrl("{website_url}")', main_code)
    main_activity_path.write_text(main_code)

    strings = strings_xml_path.read_text()
    strings = re.sub(r'<string name="app_name">.*?</string>', f'<string name="app_name">{app_label}</string>', strings)
    strings_xml_path.write_text(strings)

    print("✅ Updated package name, URL, and app label")

    print("\n⚠️ Debug Triggering GitHub Workflow:")
    print("POST https://api.github.com/repos/jibuolly/apk-service/dispatches")
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "event_type": "build-apk",
        "client_payload": {
            "site_name": site_name,
            "website_url": website_url
        }
    }

    try:
        r = httpx.post("https://api.github.com/repos/jibuolly/apk-service/dispatches", headers=headers, json=payload)
        print(f"✅ Triggered GitHub Actions: {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger GitHub Actions: {e}")

    return JSONResponse(content={"status": "success"})

    # Trigger test
