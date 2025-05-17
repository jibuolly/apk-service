from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/submit")
async def submit(request: Request):
    try:
        data = await request.json()
        print("✅ Received JSON data:", data)
        return JSONResponse(content={"message": "Data received successfully!"})
    except Exception as e:
        print("❌ Error parsing request:", str(e))
        return JSONResponse(content={"error": "Invalid request"}, status_code=400)

@app.get("/")
async def root():
    return {"message": "API is running!"}
