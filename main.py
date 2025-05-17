from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/submit")
async def receive_form_data(
    site_url: str = Form(...),
    brand_color: str = Form(...),
    email: str = Form(...)
):
    print("Received:", site_url, brand_color, email)
    return JSONResponse(content={"status": "success", "message": "Data received"})
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
