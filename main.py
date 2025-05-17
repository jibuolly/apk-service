from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace this with your domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}

# DEBUG VERSION: Log whatever data Fluent Forms sends
@app.post("/submit")
async def debug_submit(request: Request):
    try:
        data = await request.json()
        print("Received raw data:", data)
        return {"message": "Data received", "data": data}
    except Exception as e:
        print("Error parsing data:", e)
        return {"error": "Invalid JSON", "details": str(e)}
