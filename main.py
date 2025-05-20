from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, re, shutil, subprocess, requests, zipfile
from urllib.parse import unquote_plus
from pathlib import Path
from pydantic import BaseModel

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
    site_name = re.sub(r'https?://|www\.|[^a-zA-Z0-9]', '', website_url).lower()
    package_name = f"com.{site_name}.android"
    app_label = site_name.capitalize()

    print(f"✅ App name: {package_name}")
    print(f"✅ Website: {website_url}")
    print(f"✅ Brand color: {brand_color}")

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

    # Step 3: Download icon and splash
    icon_url = f"https://apk-service-production.up.railway.app/output/{site_name}-512x512.png"
    splash_url = f"https://apk-service-production.up.railway.app/output/{site_name}-splash-1280x1920.png"

    icon_path = app_dir / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi" / "ic_launcher.png"
    splash_path = app_dir / "app" / "src" / "main" / "res" / "drawable" / "splash.png"
    splash_path.parent.mkdir(parents=True, exist_ok=True)

    with open(icon_path, "wb") as f:
        f.write(requests.get(icon_url).content)

    with open(splash_path, "wb") as f:
        f.write(requests.get(splash_url).content)

    print("✅ Downloaded icon and splash")

    # Step 4: Inject website URL and package name
    manifest_path = app_dir / "app" / "src" / "main" / "AndroidManifest.xml"
    main_activity_path = list(app_dir.glob("**/MainActivity.java"))[0]

    # Update AndroidManifest
    manifest = manifest_path.read_text()
    manifest = re.sub(r'package="[^"]+"', f'package="{package_name}"', manifest)
    manifest_path.write_text(manifest)

    # Update MainActivity
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

    print("✅ APK ready:", apk_path)

    # TODO Step 7: Email the APK using Brevo (coming next)

    return JSONResponse(content={
        "message": "APK built successfully",
        "apk_url": f"/output/{site_name}.apk"
    })

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
