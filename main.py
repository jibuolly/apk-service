from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from urllib.parse import urlparse, unquote_plus
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re, shutil, os, httpx

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

    hostname = urlparse(website_url).hostname or website_url
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

    # Icon
    icon_img = Image.new("RGB", (512, 512), color=brand_color)
    draw_icon = ImageDraw.Draw(icon_img)
    draw_icon.text((180, 240), site_name[:1].upper(), font=ImageFont.load_default(), fill="white")
    icon_img.save(icon_path)
    print(f"✅ Icon created at: {icon_path}")

    # Splash
    splash_img = Image.new("RGB", (1280, 1920), color=brand_color)
    draw_splash = ImageDraw.Draw(splash_img)
    draw_splash.text((500, 900), app_label, font=ImageFont.load_default(), fill="white")
    splash_img.save(splash_path)
    print(f"✅ Splash created at: {splash_path}")

    # Setup
    working_dir = Path(f"/tmp/{site_name}")
    if working_dir.exists():
        shutil.rmtree(working_dir)
    working_dir.mkdir(parents=True)

    os.chdir(working_dir)
    os.system("git clone --depth 1 https://github.com/jibuolly/apk-template.git")

    app_dir = working_dir / "apk-template"
    os.chdir(app_dir)

    icon_target = app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
    splash_target = app_dir / "app" / "src" / "main" / "res" / "drawable" / "splash.png"
    splash_target.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(icon_path, icon_target)
    shutil.copy(splash_path, splash_target)
    print(f"✅ Copied icon to {icon_target}")
    print(f"✅ Copied splash to {splash_target}")

    # Manifest & MainActivity
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

    # Skip local APK build
    print("ℹ️ Skipping local APK check, triggering GitHub Actions instead.")

    # Trigger GitHub Workflow
    trigger_url = "https://api.github.com/repos/jibuolly/apk-service/dispatches"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "event_type": "build-apk",
        "client_payload": {
            "site_name": site_name
        }
    }

    print("\n⚠️ Debug Triggering GitHub Workflow:")
    print(f"POST {trigger_url}")
    print(f"Headers: {headers}")

    try:
        r = httpx.post(trigger_url, headers=headers, json=payload)
        print(f"✅ Triggered GitHub Actions: {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger GitHub Actions: {e}")

    return JSONResponse(content={
        "message": "App processing started",
        "site": site_name
    })
