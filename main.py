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
    brand_color = data.get("brand_color", "#000000")
    email = data.get("email", "").strip()

    print(f"✅ App name: com.{site_name}.android")
    print(f"✅ Website: {website_url}")
    print(f"✅ Brand color: {brand_color}")

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
            "website_url": website_url,
            "brand_color": brand_color
        }
    }

    try:
        r = httpx.post("https://api.github.com/repos/jibuolly/apk-service/dispatches", headers=headers, json=payload)
        print(f"✅ Triggered GitHub Actions: {r.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger GitHub Actions: {e}")

    return JSONResponse(content={"status": "success"})
