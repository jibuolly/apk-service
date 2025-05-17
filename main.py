from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from urllib.parse import parse_qs

app = FastAPI()

@app.post("/submit")
async def submit(request: Request):
    try:
        # Get raw body and decode to string
        body = await request.body()
        decoded = body.decode("utf-8")
        print("✅ Raw body received:", decoded)

        # Parse the URL-encoded form data
        parsed_data = parse_qs(decoded)

        # Extract specific values
        email = parsed_data.get("email", [""])[0]
        website_url = parsed_data.get("website_url", [""])[0]
        brand_color = parsed_data.get("brand_color", [""])[0]

        # Log the clean values
        print("✅ Parsed Data:")
        print("   📧 Email:", email)
        print("   🌐 Website URL:", website_url)
        print("   🎨 Brand Color:", brand_color)

        return JSONResponse(content={"message": "Data received successfully!"})
    except Exception as e:
        print("❌ Error parsing request:", str(e))
        return JSONResponse(content={"error": "Invalid request"}, status_code=400)

@app.get("/")
async def root():
    return {"message": "API is running!"}

# Run on Railway's expected port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
