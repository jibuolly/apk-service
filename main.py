from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/submit")
async def submit(request: Request):
    try:
        body = await request.body()
        print("✅ Raw body received:", body.decode("utf-8"))
        return JSONResponse(content={"message": "Data received successfully!"})
    except Exception as e:
        print("❌ Error parsing request:", str(e))
        return JSONResponse(content={"error": "Invalid request"}, status_code=400)

@app.get("/")
async def root():
    return {"message": "API is running!"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
