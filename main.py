from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time, requests, json, io, csv, openpyxl, logging
from urllib.parse import quote
import pandas as pd
from io import BytesIO
from supabase import create_client, Client

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Supabase Configuration ---
SUPABASE_URL = "https://nzqzhpeccenmgglkcmhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56cXpocGVjY2VubWdnbGtjbWhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ2NzAzMSwiZXhwIjoyMDc2MDQzMDMxfQ.z5qf6unizb_KaF8YKpc60V2jsP54v-NsKclDW9zfYEU"

# ✅ Define Supabase client (fix for “name 'supabase' is not defined”)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --------------------------------------------------------------------------
# ✅ Keep your existing routes exactly as they were
# --------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Backend running successfully"}


@app.get("/employees")
async def get_employees():
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching employees: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JSONResponse(status_code=400, content={"error": "Email and password required"})

        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        }
        payload = {"email": email, "password": password}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"error": "Invalid credentials"})

        return JSONResponse(content=response.json())
    except Exception as e:
        logging.error(f"Login error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# --------------------------------------------------------------------------
# ✅ Updated Bulk Upload API (fixed version)
# --------------------------------------------------------------------------

@app.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...)):
    try:
        # Validate file type
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            logging.error(f"Invalid file type: {file.content_type}")
            return JSONResponse(status_code=422, content={"error": "Invalid file type. Please upload .xlsx only."})

        # Read Excel content
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # Clean headers and ensure consistent format
        df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]

        required_columns = ["First_Name", "Last_Name", "Gender", "Country", "Age", "Date", "Id"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required columns: {', '.join(missing)}"},
            )

        # Convert date columns if present
        if "Date" in df.columns:
            df["Date"] = df["Date"].astype(str)

        records = df.to_dict(orient="records")

        # ✅ Insert data into your Supabase table
        response = supabase.table("employee_bulk_imports").insert(records).execute()

        if hasattr(response, "error") and response.error:
            raise Exception(str(response.error))

        inserted_count = len(response.data) if response.data else len(records)
        logging.info(f"Inserted {inserted_count} rows into employee_bulk_imports successfully.")

        return JSONResponse(
            content={
                "message": f"✅ Successfully inserted {inserted_count} rows into employee_bulk_imports",
                "status": "success",
            }
        )

    except Exception as e:
        logging.error(f"Bulk upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

