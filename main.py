from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from io import BytesIO
import logging, re
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


@app.post("/add-employee")
async def add_employee(
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    file: UploadFile = File(None),
    compressed_file: UploadFile = File(None),
    bulk_files: list[UploadFile] = File(None),
):
    try:
        
        print("\n===== DEBUG: Incoming form data =====")
        print("Name:", name)
        print("Email:", email)
        print("Position:", position)
        print("File provided:", bool(file))
        print("Compressed file provided:", bool(compressed_file))
        print("Bulk files type:", type(bulk_files))
        print("Bulk files length:", len(bulk_files) if bulk_files else 0)
        if bulk_files:
            for bf in bulk_files:
                print(" - Bulk file name:", bf.filename)
        print("=====================================\n")


        debug = {}
        file_url, compressed_file_url = None, None
        bulk_file_urls = []

        debug["received_fields"] = {
            "name": name,
            "email": email,
            "position": position,
            "file_provided": bool(file),
            "compressed_provided": bool(compressed_file),
            "bulk_files_count": len(bulk_files) if bulk_files else 0,
        }

        # ---------------- NORMAL FILE UPLOAD ----------------
        if file:
            file_bytes = await file.read()
            ts = int(time.time())
            safe_filename = f"{ts}_{quote(file.filename)}"
            upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_filename}"

            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type or "application/octet-stream",
            }

            res = requests.post(upload_url, headers=headers, data=file_bytes, timeout=30)
            debug["normal_upload_status"] = res.status_code

            if res.status_code in (200, 201):
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_filename}"
            else:
                debug["normal_upload_failed"] = res.text

        # ---------------- COMPRESSED FILE UPLOAD ----------------
        if compressed_file:
            comp_bytes = await compressed_file.read()
            ts2 = int(time.time())
            safe_comp_filename = f"{ts2}_compressed_{quote(compressed_file.filename)}"
            upload_url_comp = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_comp_filename}"

            headers_comp = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": compressed_file.content_type or "application/octet-stream",
            }

            res_comp = requests.post(upload_url_comp, headers=headers_comp, data=comp_bytes, timeout=30)
            debug["compressed_upload_status"] = res_comp.status_code

            if res_comp.status_code in (200, 201):
                compressed_file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_comp_filename}"
            else:
                debug["compressed_upload_failed"] = res_comp.text

        # ---------------- BULK FILE UPLOADS ----------------
        if bulk_files:
            for f in bulk_files:
                file_bytes = await f.read()
                ts3 = int(time.time())
                safe_bulk_name = f"{ts3}_bulk_{quote(f.filename)}"
                upload_url_bulk = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_bulk_name}"

                headers_bulk = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": f.content_type or "application/octet-stream",
                }

                res_bulk = requests.post(upload_url_bulk, headers=headers_bulk, data=file_bytes, timeout=30)
                debug.setdefault("bulk_upload_response_texts", []).append(res_bulk.text)

                debug.setdefault("bulk_upload_status", []).append(res_bulk.status_code)

                debug.setdefault("bulk_files_received", []).append(f.filename)


                if res_bulk.status_code in (200, 201):
                    bulk_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{safe_bulk_name}"
                    bulk_file_urls.append(bulk_url)
                else:
                    debug.setdefault("bulk_upload_failed_files", []).append(f.filename)
                    
        

        # ---------------- INSERT INTO EMPLOYEES TABLE ----------------
        insert_url = f"{SUPABASE_URL}/rest/v1/employees"
        insert_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        payload = {
            "name": name,
            "email": email,
            "position": position,
            "file_url": file_url,
            "compressed_file_url": compressed_file_url,
            "bulk_file_urls": json.dumps(bulk_file_urls),
        }

        insert_res = requests.post(insert_url, headers=insert_headers, json=payload, timeout=30)
        debug["db_insert_status"] = insert_res.status_code

        if insert_res.status_code in (200, 201):
            return {"message": "Employee added successfully!", "debug": debug, "row": insert_res.json()}
        else:
            return {"error": "Database insert failed", "debug": debug, "db_text": insert_res.text}

    except Exception as e:
        return {"error": str(e)}
        
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        SUPABASE_BUCKET = "employee-files"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file.filename}"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": file.content_type,
        }

        res = requests.post(upload_url, headers=headers, data=await file.read())

        if res.status_code in [200, 201]:
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file.filename}"
            return {"file_url": file_url}
        else:
            return {"error": res.text}

    except Exception as e:
        return {"error": str(e)}
 
# --------------------------------------------------------------------------
# ✅ Bulk upload (REST API version)
# --------------------------------------------------------------------------

@app.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...)):
    try:
        # ✅ Validate file type
        if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return JSONResponse(status_code=422, content={"error": "Invalid file type. Please upload .xlsx only."})

        contents = await file.read()

        # ✅ Load workbook in formula mode
        wb = openpyxl.load_workbook(BytesIO(contents), data_only=False)  # data_only=False → keeps formulas
        ws = wb.active

        # ✅ Formula Injection Check (before anything else)
        formula_cells = []
        for row in ws.iter_rows(values_only=False):
            for cell in row:
                if isinstance(cell.value, str) and cell.value.strip().startswith(("=", "+", "-", "@")):
                    formula_cells.append(f"{cell.coordinate}: {cell.value}")

        if formula_cells:
            return JSONResponse(
                status_code=400,
                content={"error": f"Formula injection detected in cells: {', '.join(formula_cells[:10])} (showing first 10). Upload rejected."},
            )

        # ✅ Safe to load with pandas now
        df = pd.read_excel(BytesIO(contents))

        # Clean & rename headers
        df.columns = [str(col).strip().replace(" ", "_").lower() for col in df.columns]
        column_mapping = {
            "first_name": "first_name",
            "last_name": "last_name",
            "gender": "gender",
            "country": "country",
            "age": "age",
            "date": "date_of_event",
            "id": "external_id",
        }
        df.rename(columns=column_mapping, inplace=True)

        # Required check
        required = ["first_name", "last_name", "gender", "country", "age", "date_of_event", "external_id"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            return JSONResponse(status_code=400, content={"error": f"Missing required columns: {', '.join(missing)}"})

        # Convert date safely
        if "date_of_event" in df.columns:
            df["date_of_event"] = pd.to_datetime(df["date_of_event"], errors="coerce").astype(str)

        records = df.to_dict(orient="records")

        # ✅ Atomic Upload (if supported)
        url = f"{SUPABASE_URL}/rest/v1/employee_bulk_imports"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "tx=commit",
        }

        response = requests.post(url, headers=headers, json=records)
        if response.status_code not in (200, 201):
            logging.error(f"Supabase insert failed: {response.text}")
            return JSONResponse(status_code=response.status_code, content={"error": response.text})

        inserted_count = len(response.json())
        return JSONResponse(content={"message": f"✅ Inserted {inserted_count} rows successfully", "status": "success"})

    except Exception as e:
        logging.error(f"Bulk upload failed: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})