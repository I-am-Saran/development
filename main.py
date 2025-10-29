from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from io import BytesIO
import logging
import requests

# Initialize FastAPI
app = FastAPI()
logging.basicConfig(level=logging.INFO)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Supabase credentials ---
SUPABASE_URL = "https://nzqzhpeccenmgglkcmhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56cXpocGVjY2VubWdnbGtjbWhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ2NzAzMSwiZXhwIjoyMDc2MDQzMDMxfQ.z5qf6unizb_KaF8YKpc60V2jsP54v-NsKclDW9zfYEU"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --------------------------------------------------------------------------
# ✅ Root route
# --------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Backend running successfully"}

# --------------------------------------------------------------------------
# ✅ Get employees
# --------------------------------------------------------------------------

@app.get("/employees")
async def get_employees():
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching employees: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --------------------------------------------------------------------------
# ✅ Login route
# --------------------------------------------------------------------------

@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JSONResponse(status_code=400, content={"error": "Email and password required"})

        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        payload = {"email": email, "password": password}
        response = requests.post(url, headers=HEADERS, json=payload)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"error": "Invalid credentials"})

        return JSONResponse(content=response.json())
    except Exception as e:
        logging.error(f"Login error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --------------------------------------------------------------------------
# ✅ Bulk upload (REST API version)
# --------------------------------------------------------------------------

@app.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...)):
    try:
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return JSONResponse(status_code=422, content={"error": "Invalid file type. Please upload .xlsx only."})

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]

        required_columns = ["First_Name", "Last_Name", "Gender", "Country", "Age", "Date", "Id"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required columns: {', '.join(missing)}"},
            )

        if "Date" in df.columns:
            df["Date"] = df["Date"].astype(str)

        records = df.to_dict(orient="records")

        # Insert records into Supabase via REST
        url = f"{SUPABASE_URL}/rest/v1/employee_bulk_imports"
        response = requests.post(url, headers=HEADERS, json=records)

        if response.status_code not in (200, 201):
            logging.error(f"Supabase insert failed: {response.text}")
            return JSONResponse(status_code=response.status_code, content={"error": response.text})

        return JSONResponse(
            content={
                "message": f"✅ Successfully inserted {len(records)} rows into employee_bulk_imports",
                "status": "success",
            }
        )

    except Exception as e:
        logging.error(f"Bulk upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})